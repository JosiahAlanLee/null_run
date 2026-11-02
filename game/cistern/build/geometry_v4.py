#!/usr/bin/env python3
"""Cistern topology BLOCKOUT. Geometry-derived pre-emission routing; no art acceptance."""
from pathlib import Path
import json,struct,zipfile,collections,hashlib,subprocess,re,shutil,random,argparse
from udmf import emit,parse,lumps
from routing import Chunk,Link,Composition,prove,RoutingFailure
O=Path(__file__).resolve().parent
BASE=Path('/home/echevarian/dev/shared/codex/nullrun-build-20261101e')
G=32

def wad(text):
 entries=[('MAP04',b''),('TEXTMAP',text.encode()),('ENDMAP',b'')];data=b'';directory=b''
 for name,blob in entries:
  directory+=struct.pack('<II8s',12+len(data),len(blob),name.encode());data+=blob
 return struct.pack('<4sII',b'PWAD',len(entries),12+len(data))+data+directory

def make(seed=0):
 rng=random.Random(seed)
 cells={};styles={};tags={};optional=set()
 # Widths and treads snap to 32 u (1 m); every riser is 8 u (25 cm).
 def rect(name,x0,y0,x1,y1,z=0,h=128,light=112,style='pools',tag=0):
  styles[name]=style
  for x in range(x0,x1,G):
   for y in range(y0,y1,G):
    if (x,y) in cells:raise ValueError('Overlapping modules: '+name+' '+str((x,y)))
    cells[x,y]=(name,z,h,light,tag)
 for x in range(-256,256,G):
  for y in range(-256,256,G):
   if abs(x+16)+abs(y+16)<=384:rect('tidal_hub',x,y,x+G,y+G,h=320,light=128,style='caustic')
 rect('intake',-64,-640,64,-256,h=96,light=88,style='single-practical')
 rect('east_service',256,-64,512,64,h=96,light=96,style='cold-strip')
 for i in range(8):rect('east_stair',512+i*32,-64,544+i*32,64,z=(i+1)*8,h=144,light=120,style='sodium')
 rect('gallery',768,-128,1088,768,z=64,h=224,light=144,style='daylight')
 rect('upper_pipe',-256,640,768,768,z=64,h=96,light=80,style='single-practical')
 rect('pump',-640,640,-256,896,z=64,h=192,light=160,style='silhouette')
 rect('west_throat',-512,-64,-256,64,h=96,light=96,style='sodium')
 rect('sump',-768,-128,-512,128,h=160,light=112,style='caustic')
 rect('culvert',-768,128,-640,384,h=80,light=72,style='pools')
 for i in range(8):rect('drain_stair',-768,384+i*32,-640,416+i*32,z=(i+1)*8,h=128,light=96,style='caustic')
 # Turn landing joins the pump via its west side.
 rect('pump_landing',-768,640,-640,768,z=64,h=128,light=144,style='daylight')
 # Return stair behind the far-side latch: rise 8 every 32, landing at both ends.
 rect('shortcut_gate',-64,256,64,288,z=0,h=80,light=152,style='warm',tag=2101)
 rect('shortcut_foot',-64,288,64,320,z=0,h=112,light=96,style='pools')
 for i in range(8):rect('return_stair',-64,320+i*32,64,352+i*32,z=(i+1)*8,h=112,light=96,style='pools')
 rect('shortcut_head',-64,576,64,640,z=64,h=112,light=144,style='silhouette')
 # Optional ward off gallery, with a narrow vestibule. Blockout, not E17 likeness.
 rect('harvest_vestibule',1088,0,1152,128,z=64,h=80,light=128,style='silhouette')
 rect('ward_vestibule',1088,448,1152,576,z=64,h=80,light=112,style='warm')
 rect('optional_ward',1152,384,1440,640,z=64,h=144,light=160,style='daylight')
 optional.add('optional_ward')
 rect('exit_gate',-512,896,-384,992,z=64,h=80,light=160,style='warm',tag=2102)
 rect('exit',-544,992,-352,1248,z=64,h=160,light=208,style='daylight')
 # One openable service door interrupts the long pipe run.
 for p,row in list(cells.items()):
  if p[0]==448 and -64<=p[1]<64:cells[p]=('service_gate',0,80,128,2103)
 styles['service_gate']='silhouette'
 # Shared adjacent cells with identical properties own one sector; interior tile edges vanish.
 d={k:[] for k in ('vertex','linedef','sidedef','sector','thing')};sector={};owners={};vlookup={};edges={}
 def vert(p):
  if p not in vlookup:vlookup[p]=len(d['vertex']);d['vertex'].append(dict(x=p[0],y=p[1]))
  return vlookup[p]
 def side(s,mid='-'):
  n=len(d['sidedef']);d['sidedef'].append(dict(sector=s,texturetop='NRLIME',texturebottom='NRLIME',texturemiddle=mid));return n
 for p,row in cells.items():
  if row not in sector:
   name,z,h,light,tag=row
   if not tag:light=max(64,min(208,light+rng.choice([-8,0,8])))
   s=len(d['sector']);sector[row]=s;owners[s]=name
   d['sector'].append(dict(heightfloor=z,heightceiling=z+(0 if tag else h),texturefloor='NRFCON1',textureceiling='NSF4',lightlevel=light,id=tag))
  s=sector[row];x,y=p
  # Clockwise boundary: front sector lies on the right.
  for a,b in [((x,y),(x,y+G)),((x,y+G),(x+G,y+G)),((x+G,y+G),(x+G,y)),((x+G,y),(x,y))]:
   if (b,a) in edges:
    other=edges.pop((b,a))
    if other!=s:
     d['linedef'].append(dict(v1=vert(b),v2=vert(a),sidefront=side(other),sideback=side(s),twosided=True))
   else:edges[a,b]=s
 for (a,b),s in edges.items():d['linedef'].append(dict(v1=vert(a),v2=vert(b),sidefront=side(s,'NRLIME'),blocking=True))
 d['thing']=[dict(x=0,y=-592,type=1,angle=90),dict(x=-352,y=-448,type=17003)] if False else [dict(x=0,y=-592,type=1,angle=90)]
 # Native reusable Door_Raise for ordinary door only, actual tagged gate sector.
 for line in d['linedef']:
  if 'sideback' not in line:continue
  ss=[d['sidedef'][line[k]]['sector'] for k in ('sidefront','sideback')]
  if any(d['sector'][s]['id']==2103 for s in ss):line.update(special=12,arg0=2103,arg1=16,arg2=150,playeruse=True,repeatspecial=True)
 from import_chunk import attach
 provenance=attach(d,owners,styles,optional)
 (O/'harvest-provenance.json').write_text(json.dumps(provenance,indent=2))
 return d,owners,styles,optional,cells

def audit(d,owners,styles,optional):
 sectors=d['sector'];adj=[];balance=collections.defaultdict(collections.Counter);socket_groups=collections.defaultdict(list)
 for i,line in enumerate(d['linedef']):
  a=d['vertex'][line['v1']];b=d['vertex'][line['v2']];a=(a['x'],a['y']);b=(b['x'],b['y'])
  fs=d['sidedef'][line['sidefront']]['sector'];balance[fs][a]+=1;balance[fs][b]-=1
  if 'sideback' not in line:
   if not line.get('blocking'):raise RoutingFailure('Unsealed outer edge')
   continue
  bs=d['sidedef'][line['sideback']]['sector'];balance[bs][b]+=1;balance[bs][a]-=1
  if line.get('blocking'):continue
  for s,t in [(fs,bs),(bs,fs)]:
   sf=sectors[s]['heightfloor'];tf=sectors[t]['heightfloor']
   sh=80 if sectors[s]['id'] else sectors[s]['heightceiling']-sf
   th=80 if sectors[t]['id'] else sectors[t]['heightceiling']-tf
   if min(sf+sh,tf+th)-max(sf,tf)<60:raise RoutingFailure('Head clearance under player height')
   if abs(tf-sf)>8:raise RoutingFailure('Riser exceeds 8 u: '+str((s,t)))
   latch={2101:'shortcut',2102:'sluice'}.get(sectors[t]['id'])
   adj.append(Link(str(i)+':'+str(s),str(s),str(t),latch=latch))
  socket_groups[tuple(sorted((fs,bs)))].append((a,b))
 if any(any(v!=0 for v in b.values()) for b in balance.values()):raise RoutingFailure('Open sector boundary')
 chunks=[Chunk(str(i),styles[owners[i]],optional=owners[i] in optional,unlocks=('sluice',) if owners[i]=='pump' else ('shortcut',) if owners[i]=='shortcut_foot' else ()) for i in range(len(sectors))]
 def node(name):return str(next(i for i,n in owners.items() if n==name))
 proof=prove(Composition(chunks,adj,node('intake'),node('exit')))
 # Geometric centreline widths; connected boundary pieces must total >=64 u.
 # Intersections of cells produce contiguous straight interfaces in this blockout.
 widths=[]
 for (s,t),lines in socket_groups.items():
  width=sum(((a[0]-b[0])**2+(a[1]-b[1])**2)**.5 for a,b in lines)
  if width<64:raise RoutingFailure('Socket narrower than 64 u')
  widths.append(dict(sectors=[s,t],modules=[owners[s],owners[t]],width=width))
 proof.update(status='emitted-sector-topology-proved',sectors=len(sectors),lines=len(d['linedef']),outer_edges=sum('sideback' not in l for l in d['linedef']),interfaces=widths,
  limits=['Sector connectivity does not prove a player-disc path inside a sector.','Socket totals do not prove contiguous openings in general imported geometry.','Interactive release placement and native doors require real play.','No combat, consumable keys, lifts, drops, or portal geometry in this blockout.'])
 return proof

def main():
 if shutil.disk_usage(O).free<15*1024**3:raise RuntimeError('Disk below 15 GiB')
 parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=O/'candidate-v3');parser.add_argument('--seed',type=int,default=0);args=parser.parse_args()
 target=args.out.resolve()
 if O not in target.parents:raise ValueError('Output must be inside this job folder')
 if target.exists():raise FileExistsError(target)
 rejected=[]
 for attempt in range(32):
  try:
   d,owners,styles,optional,cells=make(args.seed+attempt);proof=audit(d,owners,styles,optional);break
  except RoutingFailure as exc:rejected.append(dict(seed=args.seed+attempt,reason=str(exc)))
 else:raise RoutingFailure('No certified layout within 32 attempts')
 proof.update(requested_seed=args.seed,accepted_seed=args.seed+attempt,rerolls=attempt,rejections=rejected)
 target.mkdir()
 (O/'geometry-proof.json').write_text(json.dumps(proof,indent=2))
 (O/'module-manifest.json').write_text(json.dumps(dict(owners=owners,styles=styles,cells=[dict(x=x,y=y,module=r[0],floor=r[1]) for (x,y),r in cells.items()]),indent=2))
 (O/'cistern.udmf').write_text(emit(d))
 # Freeze the repaired base privately; no source imports or writes at launch.
 for name in ['freedoom2.wad','capture.so','native_engine.py','launcher.py','backends.py','watch_imports.py','bank.py','pd_patch.py','run.sh','load-order.json']:
  subprocess.run(['cp','--reflink=auto',str(BASE/name),str(target/name)],check=True)
 for name in ['runtime-binary','bank','lib']:
  subprocess.run(['cp','-a','--reflink=auto',str(BASE/name),str(target/name)],check=True)
 for name in [f'game-{i:02}.pk3' for i in range(1,9)]:subprocess.run(['cp','--reflink=auto',str(BASE/name),str(target/name)],check=True)
 (target/'run.sh').write_text('#!/bin/bash\nset -euo pipefail\ncd "$(dirname "$0")"\nexec /home/echevarian/miniconda3/envs/hydrapy/bin/python "$PWD/launcher.py" --warp 4 "$@"\n')
 (target/'run.sh').chmod(0o755)
 for name in ['THIRD_PARTY.md','CREDITS.md']:shutil.copyfile(O/name,target/name)
 shutil.copytree(O/'licenses',target/'slice-licenses')
 original=zipfile.ZipFile(BASE/'build.pk3');records={n:original.read(n) for n in original.namelist()}
 map_hash={}
 for n in range(1,7):map_hash[f'map{n:02}']=hashlib.sha256(records[f'maps/map{n:02}.wad']).hexdigest()
 records['maps/map04.wad']=wad(emit(d))
 # Suppress legacy coordinate/population handlers only in the replacement Cistern.
 # Keep NRFeelHandler active so movement/body/weapon behavior is inherited.
 for name,blob in list(records.items()):
  if not name.lower().endswith('.zs'):continue
  text=blob.decode()
  pattern=r'(override\s+void\s+(?:WorldLoaded|WorldTick)\s*\([^)]*\)\s*\{)'
  if name=='feel.zs':
   cut=text.index('class NRFeelHandler') if 'class NRFeelHandler' in text else len(text)
   text=re.sub(pattern,r'\1 if(level.levelnum==4)return;',text[:cut])+text[cut:]
  else:text=re.sub(pattern,r'\1 if(level.levelnum==4)return;',text)
  if name=='nrui.zs':text=text.replace('Screen.DrawText(f,Font.CR_GOLD,24*s,20*s,cue,', 'if(level.levelnum!=4)Screen.DrawText(f,Font.CR_GOLD,24*s,20*s,cue,')
  if name=='hud.zs':text=text.replace('DrawString(Ink,cue,(0,22)', 'if(level.levelnum!=4)DrawString(Ink,cue,(0,22)')
  records[name]=text.encode()
 records['ZSCRIPT']+=b'\n#include "cistern-slice.zs"\n'
 records['cistern-slice.zs']=(O/'cistern-slice.zs').read_bytes()
 # Add an independently guarded handler; no effects on other strata.
 records['MAPINFO']+=b'\ngameinfo { AddEventHandlers = "CisternSlice" }\n'
 with zipfile.ZipFile(target/'build.pk3','w',zipfile.ZIP_DEFLATED) as z:
  for name,blob in records.items():z.writestr(name,blob)
 (O/'base-map-hashes.json').write_text(json.dumps(dict(before=map_hash,after={f'map{n:02}':hashlib.sha256(records[f'maps/map{n:02}.wad']).hexdigest() for n in range(1,7)}),indent=2))
 print('Candidate emitted after sector proof:',len(d['sector']),'sectors;',proof['states'],'routing states')
if __name__=='__main__':main()
