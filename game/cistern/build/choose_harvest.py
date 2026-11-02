from pathlib import Path
import json,math
from udmf import parse
P=Path('/home/echevarian/dev/shared/codex/nullrun-modular-20261101/job-20261101-214437/harvested-v2')
out=[]
for c in json.loads((P/'catalog.json').read_text())['chunks']:
 if not 3<=len(c['source_sectors'])<=12 or max(c['bounds'])>1024 or c['verticality']>64:continue
 d=parse((P/c['file']).read_text())
 if any(s['heightceiling']-s['heightfloor']<80 for s in d['sector']):continue
 if any(abs(d['sector'][d['sidedef'][l['sidefront']]['sector']]['heightfloor']-d['sector'][d['sidedef'][l['sideback']]['sector']]['heightfloor'])>8 for l in d['linedef'] if 'sideback' in l):continue
 for sock in c['sockets']:
  l=d['linedef'][sock['line']];a=d['vertex'][l['v1']];b=d['vertex'][l['v2']]
  if a['x']==b['x']==0 and sock['floor']==0 and sock['width']==128:
   out.append(dict(id=c['id'],sectors=len(d['sector']),bounds=c['bounds'],socket=sock));break
print(json.dumps(out[:30],indent=2))
