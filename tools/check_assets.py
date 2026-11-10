import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from paretolab import analyze,verify
from paretolab.controls import suite,controls
assert json.loads((ROOT/'docs/controls.json').read_text())==controls()
cases=json.loads((ROOT/'examples/reports.json').read_text());expected=[dict(**z,report=analyze(z['input']))for z in suite()];assert cases==expected
for z in cases:assert verify(z['report'])['valid']
html=(ROOT/'docs/index.html').read_text();ids=re.findall(r'id="([^"]+)"',html);assert len(ids)==len(set(ids))
for path in re.findall(r'(?:src|href)="([^"]+)"',html):
 if not path.startswith(('http','#')):assert(ROOT/'docs'/path).is_file(),path
for name in['README.md','MODEL.md','EVIDENCE.md','SOURCES.md','LICENSE']:assert(ROOT/name).is_file()
print(json.dumps(dict(controls=len(controls()),reports=len(cases),unique_dom_ids=len(ids),assets=5)))
