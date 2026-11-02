from pathlib import Path
import zipfile,json,hashlib,re
from udmf import parse,lumps
from generate import BASE
O=Path(__file__).resolve().parent;C=O/'candidate-v3'
z=zipfile.ZipFile(C/'build.pk3');base=zipfile.ZipFile(BASE/'build.pk3');d=parse(dict(lumps(z.read('maps/map04.wad')))[b'TEXTMAP'].decode());seen=set();dups=[]
for i,l in enumerate(d['linedef']):
 a=tuple(d['vertex'][l['v1']].values());b=tuple(d['vertex'][l['v2']].values());edge=tuple(sorted([a,b]))
 if edge in seen:dups.append(i)
 seen.add(edge)
 assert a!=b
 assert bool(l.get('twosided'))==('sideback' in l)
assert not dups,dups
used_vertices={l[k] for l in d['linedef'] for k in ('v1','v2')};positions={};aliases=[]
for i in used_vertices:
 v=d['vertex'][i];key=(v['x'],v['y'])
 if key in positions:aliases.append([positions[key],i])
 positions[key]=i
assert not aliases,aliases
unchanged={f'map{i:02}':z.read(f'maps/map{i:02}.wad')==base.read(f'maps/map{i:02}.wad') for i in [1,2,3,5,6]};assert all(unchanged.values())
assets={f'game-{i:02}.pk3':hashlib.sha256((C/f'game-{i:02}.pk3').read_bytes()).hexdigest()==hashlib.sha256((BASE/f'game-{i:02}.pk3').read_bytes()).hexdigest() for i in range(1,9)};assert all(assets.values())
assert z.testzip() is None
# A package-resource existence check, not a visual material/surface audit.
resources=set()
for path in [*[C/f'game-{i:02}.pk3' for i in range(1,9)],C/'build.pk3']:
 zz=zipfile.ZipFile(path)
 for n in zz.namelist():
  if n.lower().startswith(('textures/','flats/')):resources.add(Path(n).stem.upper())
  if n.upper()=='TEXTURES':resources.update(n.upper() for n in re.findall(r'(?im)^\s*(?:Texture|WallTexture|Flat)\s+"?([^",\s]+)',zz.read(n).decode()))
used={s[k].upper() for s in d['sector'] for k in ('texturefloor','textureceiling')}|{s.get(k,'-').upper() for s in d['sidedef'] for k in ('texturemiddle','texturetop','texturebottom')};missing=sorted(used-resources-{'-'})
assert not missing,missing
result=dict(package_crc='pass',duplicate_geometric_edges=dups,duplicate_used_vertex_coordinates=aliases,unchanged_other_maps=unchanged,unchanged_frozen_assets=assets,material_names=sorted(used),missing_material_names=missing,native_visual_audit='not established by this script')
(O/'PACKAGE-AUDIT.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
