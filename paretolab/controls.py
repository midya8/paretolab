"""Synthetic deterministic graph controls, no empirical planning claims."""
import random

def graph(costs):return dict(version=1,nodes=2,edges=[{'from':0,'to':1,'cost':c}for c in costs])
def controls():
 def wrap(name,p):return dict(name=name,input=p)
 out=[wrap('Unsupported compromise',graph([[0,12],[7,7],[12,0]])),wrap('Collinear all-tie',graph([[0,12],[6,6],[12,0]])),wrap('Supported compromise',graph([[0,12],[4,4],[12,0]])),wrap('Dominated zero-weight tie',graph([[0,5],[0,9],[8,0],[10,0]])),wrap('Equal costs, distinct paths',graph([[2,8],[2,8],[5,5],[8,2]])),wrap('All zero costs',graph([[0,0],[0,0]])),wrap('Empty path set',dict(version=1,nodes=4,edges=[{'from':0,'to':1,'cost':[2,2]}])),wrap('One path',graph([[4,7]])),wrap('Same second cost',graph([[4,3],[2,3],[7,3]])),wrap('Label pruning diamond',dict(version=1,nodes=5,edges=[{'from':0,'to':1,'cost':[1,4]},{'from':0,'to':2,'cost':[4,1]},{'from':1,'to':3,'cost':[1,3]},{'from':2,'to':3,'cost':[3,1]},{'from':0,'to':3,'cost':[8,8]},{'from':3,'to':4,'cost':[2,2]},{'from':0,'to':4,'cost':[12,0]}])),wrap('Three-stage planning',dict(version=1,nodes=4,edges=[{'from':a,'to':a+1,'cost':c}for a in range(3)for c in[[0,4],[3,3],[4,0]]])),wrap('Disconnected suffix',dict(version=1,nodes=5,edges=[{'from':0,'to':4,'cost':[5,5]},{'from':1,'to':2,'cost':[0,0]},{'from':2,'to':4,'cost':[1,1]}]))]
 return out

def suite():
 out=controls();rng=random.Random(20261110)
 for case in range(40):
  n=rng.randrange(2,8);es=[]
  for a in range(n-1):
   for b in range(a+1,n):
    if rng.random()<.4:es.append({'from':a,'to':b,'cost':[rng.randrange(21),rng.randrange(21)]})
  es=es[:12];out.append(dict(name=f'Seeded DAG {case}',input=dict(version=1,nodes=n,edges=es)))
 return out
