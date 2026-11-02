"""Attach a source-preserving Freedoom cluster at a real 128 u tunnel socket."""
import json,copy
from pathlib import Path
from udmf import parse,merge
P=Path(__file__).resolve().parent/'harvest-source'
ID='freedoom1-E2M5-s0087'
def attach(d,owners,styles,optional):
 c=next(c for c in json.loads((P/'catalog.json').read_text())['chunks'] if c['id']==ID)
 h=parse((P/c['file']).read_text())
 sock=next(s for s in c['sockets'] if s['line']==4)
 line=h['linedef'][sock['line']];a=h['vertex'][line['v1']];b=h['vertex'][line['v2']]
 assert a['x']==b['x']==0 and abs(a['y']-b['y'])==128
 y0=min(a['y'],b['y'])
 for v in h['vertex']:v['x']+=1152;v['y']-=y0
 for s in h['sector']:s.update(heightfloor=s['heightfloor']+64,heightceiling=s['heightceiling']+64,texturefloor='NRFCON1',textureceiling='NSF4',lightlevel=136,id=0)
 for s in h['sidedef']:
  for k in ('texturetop','texturemiddle','texturebottom'):
   if s.get(k,'-')!='-':s[k]='NRLIME'
 off=merge(d,h)
 for i in range(len(h['sector'])):owners[off['sector']+i]='harvest_'+str(i);styles['harvest_'+str(i)]='cold-strip';optional.add('harvest_'+str(i))
 # Split the harvested seam to native 32u segments and weld reversed boundary lines.
 rows=[]
 for l in d['linedef']:
  a=d['vertex'][l['v1']];b=d['vertex'][l['v2']]
  if 'sideback' not in l and a['x']==b['x']==1152 and min(a['y'],b['y'])==0 and max(a['y'],b['y'])==128:
   sign=1 if b['y']>a['y'] else -1;ids=[l['v1']]
   for i in range(1,4):ids.append(len(d['vertex']));d['vertex'].append(dict(x=1152,y=a['y']+sign*i*32))
   ids.append(l['v2'])
   for va,vb in zip(ids,ids[1:]):r=copy.deepcopy(l);r.update(v1=va,v2=vb);rows.append(r)
  else:rows.append(l)
 def xy(i):v=d['vertex'][i];return v['x'],v['y']
 boundary={};out=[]
 for l in rows:
  if 'sideback' in l:out.append(l);continue
  a,b=xy(l['v1']),xy(l['v2'])
  if (b,a) in boundary:
   r=boundary.pop((b,a));r.update(sideback=l['sidefront'],twosided=True,blocking=False)
   d['sidedef'][r['sidefront']]['texturemiddle']='-';d['sidedef'][l['sidefront']]['texturemiddle']='-';out.append(r)
  else:boundary[a,b]=l
 d['linedef']=out+list(boundary.values())
 # UDMF joins require vertex identity, not just equal coordinates.
 vertices=[];lookup={};remap={}
 for i,v in enumerate(d['vertex']):
  key=(v['x'],v['y'])
  if key not in lookup:lookup[key]=len(vertices);vertices.append(v)
  remap[i]=lookup[key]
 for l in d['linedef']:l['v1']=remap[l['v1']];l['v2']=remap[l['v2']]
 d['vertex']=vertices
 return c
