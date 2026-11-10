"""Complete bounded path, scalarization and expected-cost evidence."""
from fractions import Fraction as F
from copy import deepcopy
from .model import parse

def q(x):return str(F(x))
def dominates(a,b):return all(x<=y for x,y in zip(a,b))and a!=b

def analyze(p):
 n,out=parse(p);edges=p['edges'];suffix=[[]for _ in range(n)];suffix[-1]=[dict(edges=[],nodes=[n-1],cost=[0,0])]
 for a in range(n-2,-1,-1):
  for i in out[a]:
   e=edges[i]
   for z in suffix[e['to']]:suffix[a].append(dict(edges=[i]+z['edges'],nodes=[a]+z['nodes'],cost=[e['cost'][j]+z['cost'][j]for j in range(2)]))
  suffix[a].sort(key=lambda z:z['edges'])
 paths=[dict(id=i,**z)for i,z in enumerate(suffix[0])];frontier=[z['id']for z in paths if not any(dominates(w['cost'],z['cost'])for w in paths)];pathrows=[]
 for z in paths:
  inequalities=[];lo=F(0);hi=F(1);impossible=False
  for w in paths:
   dx=z['cost'][0]-w['cost'][0];dy=z['cost'][1]-w['cost'][1];coef=dx-dy;rhs=-dy
   if coef>0:hi=min(hi,F(rhs,coef))
   elif coef<0:lo=max(lo,F(rhs,coef))
   elif rhs<0:impossible=True
   inequalities.append(dict(other=w['id'],coefficient=coef,rhs=rhs))
  valid=not impossible and lo<=hi;positive=valid and hi>0 and lo<1
  pathrows.append(dict(path=z['id'],dominators=[w['id']for w in paths if dominates(w['cost'],z['cost'])],equals=[w['id']for w in paths if w['cost']==z['cost']],pareto=z['id']in frontier,inequalities=inequalities,lower=q(lo),upper=q(hi),constant_contradiction=impossible,closed_support=valid,positive_support=positive))
 breaks=sorted({F(0),F(1)}|{F(z[k])for z in pathrows if z['closed_support']for k in['lower','upper']});atlas=[]
 def winners(t):
  scores=[t*z['cost'][0]+(1-t)*z['cost'][1]for z in paths]
  if not scores:return None,[]
  best=min(scores);return q(best),[i for i,v in enumerate(scores)if v==best]
 for i,t in enumerate(breaks):
  score,opts=winners(t);atlas.append(dict(kind='point',lower=q(t),upper=q(t),sample=q(t),score=score,paths=opts))
  if i+1<len(breaks):
   u=breaks[i+1];sample=(t+u)/2;score,opts=winners(sample);atlas.append(dict(kind='open',lower=q(t),upper=q(u),sample=q(sample),score=score,paths=opts))
 # Dynamic-program evidence uses only nondominated child suffixes, retaining equal path identities.
 labels=[[]for _ in range(n)];trace=[]
 for a in range(n-1,-1,-1):
  candidates=[dict(edges=[],nodes=[n-1],cost=[0,0])]if a==n-1 else[]
  for i in out[a]:
   e=edges[i]
   for z in labels[e['to']]:candidates.append(dict(edges=[i]+z['edges'],nodes=[a]+z['nodes'],cost=[e['cost'][j]+z['cost'][j]for j in range(2)]))
  candidates.sort(key=lambda z:z['edges']);keep=[i for i,z in enumerate(candidates)if not any(dominates(w['cost'],z['cost'])for w in candidates)];labels[a]=[candidates[i]for i in keep];trace.append(dict(node=a,candidates=candidates,dominators=[[j for j,w in enumerate(candidates)if dominates(w['cost'],z['cost'])]for z in candidates],kept=keep,labels=deepcopy(labels[a]),full_suffix_count=len(suffix[a])))
 assert[z['edges']for z in labels[0]]==[paths[i]['edges']for i in frontier]
 budgets=sorted({z['cost'][1]for z in paths});budgets=([budgets[0]-1]+budgets)if budgets else[0];constraints=[]
 for bound in budgets:
  feasible=[z for z in paths if z['cost'][1]<=bound];best=min((tuple(z['cost'])for z in feasible),default=None);opts=[z['id']for z in feasible if tuple(z['cost'])==best];mixes=[]
  for z in feasible:mixes.append(dict(paths=[z['id']],probabilities=['1'],expected=[q(v)for v in z['cost']],violation_probability='0'))
  for i,a in enumerate(paths):
   for b in paths[i+1:]:
    y0,y1=a['cost'][1],b['cost'][1]
    if not min(y0,y1)<bound<max(y0,y1):continue
    t=F(bound-y1,y0-y1);ex=[t*a['cost'][j]+(1-t)*b['cost'][j]for j in range(2)];mixes.append(dict(paths=[a['id'],b['id']],probabilities=[q(t),q(1-t)],expected=[q(v)for v in ex],violation_probability=q(sum(ti for ti,z in[(t,a),(1-t,b)]if z['cost'][1]>bound))))
  mb=min((tuple(F(x)for x in z['expected'])for z in mixes),default=None);optimal=[z for z in mixes if tuple(F(x)for x in z['expected'])==mb];constraints.append(dict(bound=bound,feasible=[z['id']for z in feasible],best_cost=list(best)if best else None,paths=opts,mixture_cost=[q(x)for x in mb]if mb else None,mixtures=optimal,expected_gap=q(F(best[0])-mb[0])if best and mb else None))
 return dict(version=1,kind='paretolab-dag',input=deepcopy(p),paths=paths,path_audit=pathrows,frontier=frontier,supported=[z['path']for z in pathrows if z['positive_support']],unsupported=[i for i in frontier if not pathrows[i]['positive_support']],weights=atlas,labels=trace,constraints=constraints)
