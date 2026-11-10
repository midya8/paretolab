"""Report-independent verification via forward path census and line arrangement.

This module imports input validation only. It does not call the producer or
reuse its dynamic program, interval clipping, dominance helper or mixing code.
"""
from fractions import Fraction as R
from copy import deepcopy
import json
from .model import parse

def verify(report):
 try:
  p=report['input'];n,adj=parse(p);edges=p['edges'];allp=[];suffix_counts=[];full=[]
  for start in range(n):
   stack=[(start,[],[start],(0,0))];found=[]
   while stack:
    v,ids,nodes,cost=stack.pop()
    if v==n-1:found.append(dict(edges=ids,nodes=nodes,cost=list(cost)));continue
    for i in reversed(adj[v]):
     e=edges[i];stack.append((e['to'],ids+[i],nodes+[e['to']],(cost[0]+e['cost'][0],cost[1]+e['cost'][1])))
   found.sort(key=lambda z:z['edges']);full.append(found);suffix_counts.append(len(found))
  allp=[dict(id=i,**z)for i,z in enumerate(full[0])];costs=[tuple(z['cost'])for z in allp];dominators=[]
  def dom(a,b):return a[0]<=b[0]and a[1]<=b[1]and(a[0]<b[0]or a[1]<b[1])
  for c in costs:dominators.append([i for i,d in enumerate(costs)if dom(d,c)])
  frontier=[i for i,z in enumerate(dominators)if not z]
  # Sweep the complete arrangement of all objective lines, not only the envelope.
  cross={R(0),R(1)}
  for a in costs:
   for b in costs:
    denominator=a[0]-a[1]-b[0]+b[1]
    if denominator:
     t=R(b[1]-a[1],denominator)
     if 0<=t<=1:cross.add(t)
  knots=sorted(cross);cells=[(x,x)for x in knots]+[(x,y)for x,y in zip(knots,knots[1:])]
  def solve(t):
   v=[t*c[0]+(1-t)*c[1]for c in costs];m=min(v,default=None)
   return m,[i for i,x in enumerate(v)if x==m]
  coverage=[[]for _ in costs]
  for a,b in cells:
   _,ids=solve((a+b)/2)
   for i in ids:coverage[i].append((a,b))
  rows=[]
  for i,c in enumerate(costs):
   # Bounds are also certificate evidence, even when contradictory or outside [0,1].
   lower=[R(0)];upper=[R(1)];ineq=[];contradiction=False
   for j,d in enumerate(costs):
    a=(c[0]-c[1])-(d[0]-d[1]);b=d[1]-c[1];ineq.append(dict(other=j,coefficient=a,rhs=b))
    if a:
     (upper if a>0 else lower).append(R(b,a))
    elif b<0:contradiction=True
   lo=max(lower);hi=min(upper);support=bool(coverage[i]);positive=any(b>0 and a<1 for a,b in coverage[i]);assert support==(not contradiction and lo<=hi)
   rows.append(dict(path=i,dominators=dominators[i],equals=[j for j,d in enumerate(costs)if d==c],pareto=i in frontier,inequalities=ineq,lower=str(lo),upper=str(hi),constant_contradiction=contradiction,closed_support=support,positive_support=positive))
  breaks=sorted({R(0),R(1)}|{R(z[k])for z in rows if z['closed_support']for k in['lower','upper']});atlas=[]
  for a,b,kind in sorted([(t,t,'point')for t in breaks]+[(a,b,'open')for a,b in zip(breaks,breaks[1:])],key=lambda z:(z[0],0 if z[2]=='point'else 1)):
   t=(a+b)/2;value,ids=solve(t);atlas.append(dict(kind=kind,lower=str(a),upper=str(b),sample=str(t),score=str(value)if value is not None else None,paths=ids))
  # Reconstruct local candidates from independently classified complete child paths.
  labels=[]
  for node in reversed(range(n)):
   candidates=[dict(edges=[],nodes=[n-1],cost=[0,0])]if node==n-1 else[]
   for edge in adj[node]:
    e=edges[edge];child=full[e['to']]
    for z in child:
     if any(dom(tuple(w['cost']),tuple(z['cost']))for w in child):continue
     candidates.append(dict(edges=[edge]+z['edges'],nodes=[node]+z['nodes'],cost=[e['cost'][k]+z['cost'][k]for k in[0,1]]))
   candidates.sort(key=lambda z:z['edges']);ds=[[j for j,w in enumerate(candidates)if dom(tuple(w['cost']),tuple(z['cost']))]for z in candidates];kept=[j for j,d in enumerate(ds)if not d];labels.append(dict(node=node,candidates=candidates,dominators=ds,kept=kept,labels=[candidates[j]for j in kept],full_suffix_count=suffix_counts[node]))
  levels=sorted(set(c[1]for c in costs));levels=([levels[0]-1]+levels)if levels else[0];constraints=[]
  for bound in levels:
   fs=[i for i,c in enumerate(costs)if c[1]<=bound];best=min((costs[i]for i in fs),default=None);opts=[i for i in fs if costs[i]==best];vertices=[]
   for i in fs:vertices.append(dict(paths=[i],probabilities=['1'],expected=[str(R(x))for x in costs[i]],violation_probability='0'))
   # Solve each two-support basic feasible solution using a 2x2 determinant.
   for i in range(len(costs)):
    for j in range(i+1,len(costs)):
     y,z=costs[i][1],costs[j][1];det=z-y
     if det==0:continue
     pi=R(z-bound,det);pj=R(bound-y,det)
     if not 0<pi<1 or not 0<pj<1:continue
     ex=[pi*costs[i][k]+pj*costs[j][k]for k in[0,1]];violation=(pi if y>bound else R(0))+(pj if z>bound else R(0));vertices.append(dict(paths=[i,j],probabilities=[str(pi),str(pj)],expected=[str(x)for x in ex],violation_probability=str(violation)))
   optimum=min((tuple(R(x)for x in v['expected'])for v in vertices),default=None);witnesses=[v for v in vertices if tuple(R(x)for x in v['expected'])==optimum];constraints.append(dict(bound=bound,feasible=fs,best_cost=list(best)if best is not None else None,paths=opts,mixture_cost=[str(x)for x in optimum]if optimum else None,mixtures=witnesses,expected_gap=str(R(best[0])-optimum[0])if best is not None and optimum is not None else None))
  expected=dict(version=1,kind='paretolab-dag',input=deepcopy(p),paths=allp,path_audit=rows,frontier=frontier,supported=[i for i,z in enumerate(rows)if z['positive_support']],unsupported=[i for i in frontier if not rows[i]['positive_support']],weights=atlas,labels=labels,constraints=constraints)
  # JSON type comparison prevents True == 1 and 1.0 == 1 from passing.
  if json.dumps(report,sort_keys=True,separators=(',',':'),allow_nan=False)!=json.dumps(expected,sort_keys=True,separators=(',',':'),allow_nan=False):return dict(valid=False,error='report differs from independent census')
  return dict(valid=True,paths=len(allp),frontier=len(frontier),weight_cells=len(atlas),constraints=len(constraints))
 except(Exception)as e:return dict(valid=False,error=str(e))
