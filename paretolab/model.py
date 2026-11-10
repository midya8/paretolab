"""Strict bounded acyclic two-cost planning inputs."""
import json

def keys(x,ks):
 if type(x)is not dict or set(x)!=set(ks):raise ValueError('unexpected fields')
def integer(x):
 if type(x)is not int:raise ValueError('expected non-boolean integer')
 return x
def parse(p):
 keys(p,['version','nodes','edges'])
 if integer(p['version'])!=1:raise ValueError('version must be 1')
 n=integer(p['nodes'])
 if not 2<=n<=7:raise ValueError('nodes must be 2..7')
 if type(p['edges'])is not list or len(p['edges'])>12:raise ValueError('at most 12 directed edges')
 out=[[]for _ in range(n)]
 for i,e in enumerate(p['edges']):
  keys(e,['from','to','cost']);a=integer(e['from']);b=integer(e['to'])
  if not 0<=a<b<n:raise ValueError('edges must follow strict node order')
  if type(e['cost'])is not list or len(e['cost'])!=2:raise ValueError('two costs required')
  if any(not 0<=integer(v)<=20 for v in e['cost']):raise ValueError('cost integer 0..20')
  out[a].append(i)
 counts=[0]*n;counts[-1]=1
 for a in range(n-2,-1,-1):counts[a]=sum(counts[p['edges'][i]['to']]for i in out[a])
 if max(counts)>64:raise ValueError('at most 64 suffix paths per node')
 return n,out

def loads(text):
 def pairs(ps):
  out={}
  for k,v in ps:
   if k in out:raise ValueError('duplicate key')
   out[k]=v
  return out
 def no(_):raise ValueError('JSON decimals/constants forbidden')
 return json.loads(text,object_pairs_hook=pairs,parse_float=no,parse_constant=no)
