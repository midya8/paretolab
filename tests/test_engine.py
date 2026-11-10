import unittest,copy,json,subprocess,sys,tempfile,itertools
from pathlib import Path
from fractions import Fraction as F
from paretolab import analyze,verify
from paretolab.controls import controls,suite,graph
from paretolab.model import loads
ROOT=Path(__file__).resolve().parents[1]

def leaves(x,path=()):
 if type(x)is dict:
  for k,v in x.items():yield from leaves(v,path+(k,))
 elif type(x)is list:
  for k,v in enumerate(x):yield from leaves(v,path+(k,))
 else:yield path,x

def mutate(r,path,value):
 x=copy.deepcopy(r);y=x
 for k in path[:-1]:y=y[k]
 y[path[-1]]=value;return x

def changed(v):
 if type(v)is bool:return not v
 if type(v)is int:return v+1
 if v is None:return 0
 return v+'!'

class EngineTests(unittest.TestCase):
 def test_default(self):
  r=analyze(controls()[0]['input']);self.assertEqual(r['frontier'],[0,1,2]);self.assertEqual(r['supported'],[0,2]);self.assertEqual(r['unsupported'],[1]);self.assertEqual((r['path_audit'][1]['lower'],r['path_audit'][1]['upper']),('7/12','5/12'));z=r['constraints'][2];self.assertEqual(z['best_cost'],[7,7]);self.assertEqual(z['mixture_cost'],['5','7']);self.assertEqual(z['mixtures'][0]['probabilities'],['7/12','5/12']);self.assertEqual(z['mixtures'][0]['violation_probability'],'7/12')
 def test_all_controls_independent(self):
  for z in suite():self.assertTrue(verify(analyze(z['input']))['valid'],z['name'])
 def test_collinear(self):
  r=analyze(controls()[1]['input']);self.assertEqual(r['supported'],[0,1,2]);self.assertEqual([z['paths']for z in r['weights']if z['sample']=='1/2'],[[0,1,2]])
 def test_endpoint_dominated_ties(self):
  r=analyze(controls()[3]['input']);self.assertEqual(r['weights'][0]['paths'],[2,3]);self.assertEqual(r['weights'][-1]['paths'],[0,1]);self.assertFalse(r['path_audit'][1]['positive_support']);self.assertTrue(r['path_audit'][1]['closed_support']);self.assertEqual(r['frontier'],[0,2])
 def test_duplicates(self):
  r=analyze(controls()[4]['input']);self.assertEqual(r['path_audit'][0]['equals'],[0,1]);self.assertTrue(0 in r['frontier']and 1 in r['frontier'])
 def test_zero(self):
  r=analyze(controls()[5]['input']);self.assertEqual(r['supported'],[0,1]);self.assertEqual(r['constraints'][1]['paths'],[0,1]);self.assertEqual(len(r['constraints'][1]['mixtures']),2)
 def test_disconnected(self):
  r=analyze(controls()[6]['input']);self.assertEqual(r['paths'],[]);self.assertTrue(all(z['score']is None and not z['paths']for z in r['weights']));self.assertTrue(verify(r)['valid'])
 def test_label_pruning(self):
  r=analyze(controls()[9]['input']);self.assertTrue(any(len(z['kept'])<len(z['candidates'])for z in r['labels']));self.assertEqual([z['edges']for z in r['labels'][-1]['labels']],[r['paths'][i]['edges']for i in r['frontier']])
 def test_all_729_ordered_three_path_profiles(self):
  vectors=list(itertools.product(range(3),repeat=2));total=0
  for cs in itertools.product(vectors,repeat=3):
   p=graph([list(x)for x in cs]);r=analyze(p);self.assertTrue(verify(r)['valid']);self.assertEqual(set(i for z in r['constraints']for i in z['paths']),set(r['frontier']));self.assertTrue(set(r['supported'])<=set(r['frontier']));total+=1
  self.assertEqual(total,729)
 def test_every_primitive_forgery(self):
  n=0
  for idx in[0,9]:
   r=analyze(controls()[idx]['input'])
   for p,v in leaves(r):self.assertFalse(verify(mutate(r,p,changed(v)))['valid'],p);n+=1
  self.assertGreater(n,500)
 def test_shape_and_types(self):
  r=analyze(controls()[0]['input'])
  for bad in[{**r,'extra':0},mutate(r,('paths',0,'id'),False),mutate(r,('paths',0,'id'),0.0),mutate(r,('constraints',0,'paths'),[0]),mutate(r,('frontier',),[0,2]),mutate(r,('path_audit',0,'lower'),'2/4')]:self.assertFalse(verify(bad)['valid'])
 def test_invalid_inputs(self):
  p=controls()[0]['input'];bads=[{**p,'version':True},{**p,'nodes':8},{**p,'extra':0},{**p,'edges':[{'from':1,'to':0,'cost':[1,1]}]},{**p,'edges':[{'from':0,'to':1,'cost':[True,0]}]},{**p,'edges':[{'from':0,'to':1,'cost':[1.,0]}]},{**p,'edges':[{'from':0,'to':1,'cost':[21,0]}]},{**p,'edges':p['edges']*5}]
  for p in bads:
   with self.assertRaises(ValueError):analyze(p)
 def test_path_budget_boundary(self):
  p=dict(version=1,nodes=5,edges=[{'from':a,'to':a+1,'cost':[0,0]}for a,k in enumerate([4,4,2,2])for _ in range(k)]);self.assertEqual(len(analyze(p)['paths']),64);p['edges'].append({'from':0,'to':4,'cost':[1,1]})
  # This input is separately rejected on arc count; 65 paths with 12 arcs also rejected.
  p=dict(version=1,nodes=5,edges=[{'from':a,'to':a+1,'cost':[0,0]}for a in range(4)for _ in range(3)])
  with self.assertRaises(ValueError):analyze(p)
 def test_no_input_mutation_or_output_alias(self):
  p=controls()[0]['input'];old=copy.deepcopy(p);r=analyze(p);self.assertEqual(p,old);r['input']['edges'][0]['cost'][0]=99;self.assertEqual(p,old)
 def test_scaling_weight_map(self):
  p=controls()[2]['input'];r=analyze(p);s=copy.deepcopy(p)
  for e in s['edges']:e['cost'][0]*=1;e['cost'][1]*=1
  self.assertEqual(analyze(s)['supported'],r['supported'])
  # Positive rescaling 12 -> 18 and 4 -> 6 on cost1 maps t -> t/(1.5 - .5t).
  for e in s['edges']:e['cost'][0]=e['cost'][0]*3//2
  z=analyze(s);self.assertEqual(z['frontier'],r['frontier']);self.assertEqual(z['supported'],r['supported'])
  for i,a in enumerate(r['path_audit']):
   if a['closed_support']:
    for k in['lower','upper']:
     t=F(a[k]);self.assertEqual(F(z['path_audit'][i][k]),t/(F(3,2)-t/2))
 def test_permuted_parallel_identity(self):
  p=controls()[0]['input'];q=copy.deepcopy(p);q['edges'].reverse();r=analyze(p);s=analyze(q);self.assertEqual(sorted(r['paths'][i]['cost']for i in r['frontier']),sorted(s['paths'][i]['cost']for i in s['frontier']))
 def test_weights_all_cells_recompute(self):
  for z in suite():
   r=analyze(z['input'])
   for c in r['weights']:
    t=F(c['sample']);scores=[t*w['cost'][0]+(1-t)*w['cost'][1]for w in r['paths']];self.assertEqual(c['paths'],[i for i,v in enumerate(scores)if v==min(scores)]if scores else[])
 def test_mixture_primal(self):
  for z in suite():
   r=analyze(z['input'])
   for c in r['constraints']:
    for w in c['mixtures']:
     ps=list(map(F,w['probabilities']));self.assertEqual(sum(ps),1);self.assertTrue(all(x>0 for x in ps));ex=[sum(p*r['paths'][i]['cost'][k]for p,i in zip(ps,w['paths']))for k in range(2)];self.assertEqual(ex,list(map(F,w['expected'])));self.assertLessEqual(ex[1],c['bound']);self.assertEqual(sum(p for p,i in zip(ps,w['paths'])if r['paths'][i]['cost'][1]>c['bound']),F(w['violation_probability']))
 def test_strict_json(self):
  for s in['{"a":1,"a":2}','{"a":1.0}','{"a":NaN}','{"a":1e1}']:
   with self.assertRaises(ValueError):loads(s)
 def test_cli(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/'r.json';r=analyze(controls()[0]['input']);p.write_text(json.dumps(r));ok=subprocess.run([sys.executable,'-m','paretolab','verify',str(p)],capture_output=True,text=True);self.assertEqual(ok.returncode,0);self.assertTrue(json.loads(ok.stdout)['valid']);r['supported']=[];p.write_text(json.dumps(r));bad=subprocess.run([sys.executable,'-m','paretolab','verify',str(p)],capture_output=True,text=True);self.assertEqual(bad.returncode,2);self.assertEqual(bad.stdout,'')
if __name__=='__main__':unittest.main()
