import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from paretolab import analyze,verify
from paretolab.controls import controls,suite
cases=[]
for z in suite():
 r=analyze(z['input']);assert verify(r)['valid'];cases.append(dict(**z,report=r))
(ROOT/'examples/reports.json').write_text(json.dumps(cases,separators=(',',':'))+'\n')
(ROOT/'docs/controls.json').write_text(json.dumps(controls(),separators=(',',':'))+'\n')
print(json.dumps(dict(reports=len(cases),paths=sum(len(z['report']['paths'])for z in cases),weight_cells=sum(len(z['report']['weights'])for z in cases),constraints=sum(len(z['report']['constraints'])for z in cases))))
