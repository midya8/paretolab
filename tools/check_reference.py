"""Optional numeric HiGHS reference, constraints built from original graph input.

Binary arc-flow MILPs check each atlas witness and deterministic epsilon solve.
A separate path-probability LP checks expected-cost feasibility and optimum.
It checks objective values, not every tie or certificate field.
"""
import sys,json
from pathlib import Path
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np,scipy
from scipy.optimize import milp,linprog,Bounds,LinearConstraint
from paretolab import analyze
from paretolab.controls import suite
solves=0;rows=0;maxerr=0.
def close(actual,exact):
 global maxerr
 err=abs(actual-float(exact));maxerr=max(err,maxerr);assert err<1e-8,(actual,exact)
for case in suite():
 p=case['input'];r=analyze(p);n=p['nodes'];m=len(p['edges']);flow=np.zeros((n,m));rhs=np.zeros(n);rhs[0]=1;rhs[-1]=-1
 for i,e in enumerate(p['edges']):flow[e['from'],i]=1;flow[e['to'],i]=-1
 if not m:
  assert not r['paths'];continue
 costs=np.array([e['cost']for e in p['edges']],dtype=float).T
 def binary(c,extra=[]):
  global solves,rows
  a=np.array(list(flow)+[x[0]for x in extra]);lo=np.array(list(rhs)+[x[1]for x in extra]);hi=np.array(list(rhs)+[x[2]for x in extra]);solves+=1;rows+=len(a);return milp(c,integrality=np.ones(m),bounds=Bounds(np.zeros(m),np.ones(m)),constraints=LinearConstraint(a,lo,hi),options={'mip_rel_gap':0})
 for z in r['weights']:
  t=float(F(z['sample']));c=t*costs[0]+(1-t)*costs[1];opt=binary(c)
  if z['score']is None:assert opt.status==2
  else:
   assert opt.success;close(opt.fun,F(z['score']));x=np.rint(opt.x);assert np.max(np.abs(flow@x-rhs))<1e-8;assert np.max(np.abs(opt.x-x))<1e-8
 for z in r['constraints']:
  extra=[(costs[1],-np.inf,z['bound'])];opt=binary(costs[0],extra)
  if z['best_cost']is None:assert opt.status==2
  else:
   assert opt.success;close(opt.fun,z['best_cost'][0]);tie=binary(costs[1],extra+[(costs[0],z['best_cost'][0],z['best_cost'][0])]);assert tie.success;close(tie.fun,z['best_cost'][1])
  if not r['paths']:continue
  cp=np.array([w['cost']for w in r['paths']],dtype=float).T;ones=np.ones((1,len(r['paths'])));prob=linprog(cp[0],A_ub=[cp[1]],b_ub=[z['bound']],A_eq=ones,b_eq=[1],bounds=(0,None),method='highs');solves+=1;rows+=2
  if z['mixture_cost']is None:assert prob.status==2
  else:
   assert prob.success;close(prob.fun,F(z['mixture_cost'][0]));lex=linprog(cp[1],A_ub=[cp[1]],b_ub=[z['bound']],A_eq=np.concatenate([ones,[cp[0]]]),b_eq=[1,float(F(z['mixture_cost'][0]))],bounds=(0,None),method='highs');solves+=1;rows+=3;assert lex.success;close(lex.fun,F(z['mixture_cost'][1]))
print(json.dumps(dict(scipy=scipy.__version__,problems=len(suite()),solves=solves,constraint_rows=rows,max_objective_error=maxerr,tolerance=1e-8)))
