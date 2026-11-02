#!/usr/bin/env python3
from pathlib import Path
import json,zipfile,shutil,subprocess,struct,io,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont,PngImagePlugin
from scipy.io import wavfile
from udmf import parse,emit,lumps
from generate import wad
from geometry_v4 import make,audit
O=Path(__file__).resolve().parent;C=O/'candidate-v4';V3=O/'candidate-v3'
F='/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
signs=[];controls=[]
def sign(text,x,y,z,angle,width=112,height=28,lit=True,kind='route'):
 signs.append(dict(text=text.split('|'),x=x,y=y,z=z,angle=angle,width=width,height=height,lit=lit,kind=kind));return len(signs)-1
# Lamp -> code -> datum -> arrow: maintained routes share the same visual grammar.
sign('OUTFALL / V-07|FOLLOW W3 OR S-4a',0,-382,78,270,112,16,kind='exit')
sign('G1 - GAUGE GALLERY|HUB / ALL ROUTES|OUTFALL AT V-07|FOLLOW THE LAMPS',0,246,102,270,160,56,kind='hub')
sign('W3 >|WEIR WALK / V-07',246,0,100,180,120,28)
sign('< S-4a|SLUICE RUN / V-07',-246,0,100,0,120,28)
sign('DOOR OPENS FROM|THE FAR SIDE|GO ROUND',0,248,82,270,112,18,False,'shortcut-near')
sign('G1|GAUGE GALLERY',0,-250,78,270,112,16)
sign('G1|GAUGE GALLERY',-60,-448,68,0,96,22,False,'intake')
# East service wheel / stair.
sign('SLUICE 3|HANDWHEEL [F]',408,-58,70,90,64,20,False,'control')
sign('G1 <|GAUGE GALLERY',270,0,78,0,112,16)
sign('W3|+1 LEVEL',508,0,100,180,112,24)
sign('V-07 < / G1 >|OUTFALL / RETURN',1080,688,114,180,144,34)
sign('V-07|OUTFALL RELEASE',-250,704,132,0,112,24)
sign('G1 >|EAST STAIR',1044,-122,104,90,80,28)
# Optional branches: no route code, no lit transom.
sign('GAUGE STATION 3|NO THROUGH ROUTE',1080,64,146,180,112,28,False,'dead-end')
sign('INSPECTION GALLERY|NO THROUGH ROUTE',1080,512,146,180,112,28,False,'dead-end')
# West run / drainage landing.
sign('S-4a|SLUICE RUN',-508,0,104,0,112,24)
sign('D1 >|DRAIN HEAD / V-07',-756,108,70,0,96,24)
sign('D1|+1 LEVEL',-704,378,60,270,112,16)
sign('V-07 >|OUTFALL RELEASE',-754,694,148,0,112,24)
sign('G1 <|SLUICE RUN',-640,648,148,90,112,24)
# Pump release and return choices, all explicit and truthful.
sign('V-07 / OUTFALL|HANDWHEEL [F]',-564,886,132,270,96,24,False,'control')
sign('G1 >|S-4b - SLUICE RUN',-460,648,148,90,144,28)
sign('G1 >|W3 - WEIR WALK',-266,748,112,180,144,28)
sign('G1|< SHORT RETURN',0,758,132,270,112,24)
sign('G1|SHORT RETURN',0,632,132,90,112,24)
sign('SHORTCUT|HANDWHEEL [F]',-58,308,70,0,64,20,False,'control')
sign('G1|GAUGE GALLERY',0,292,82,90,112,18)
# Returning to hub puts the outfall direction on the far wall.
sign('G1|INTAKE',0,-248,122,90,144,28,kind='exit')
sign('OUTFALL|[F] LEAVE CISTERN',-448,1238,130,270,144,28,kind='exit')
sign('OUTFALL|RELEASE AT V-07',-448,886,148,270,112,24,kind='exit')
# Water staff gauges, text from CISTERN-TEXT; not route lamps.
sign('LEVEL GAUGE|WORKS ZERO|AT SLUICE 1|+2.40|+1.95|+1.60',-244,140,4,0,30,104,False,'gauge')
sign('DEPTH AT THE LINE|0.6 M / SUMP 1.9 M',-756,-64,42,0,96,28,False,'gauge')
sign('LEVEL GAUGE|+2.40|+1.95|+1.60',1050,755,68,270,26,88,False,'gauge')
sign('G1|GAUGE GALLERY',-270,0,78,180,112,16)
sign('G1 / OUTFALL|DOWN EAST STAIR',774,0,152,0,112,28)
sign('G1 <|GAUGE GALLERY',-640,-122,66,90,112,32)
sign('G1 <|GAUGE GALLERY',-704,124,60,90,112,16)
# Each release is a distinct wall object, not an invisible rectangular use region.
controls=[dict(id=1,name='V-07 outfall handwheel',x=-564,y=886,z=88,angle=270),dict(id=2,name='far-side shortcut handwheel',x=-54,y=310,z=24,angle=0),dict(id=3,name='east service handwheel',x=410,y=-54,z=24,angle=90),dict(id=3,name='west service handwheel',x=502,y=-54,z=24,angle=90),dict(id=4,name='outfall exit handle',x=-448,y=1237,z=88,angle=270)]

def png(im):
 b=io.BytesIO();meta=PngImagePlugin.PngInfo();meta.add(b'grAb',struct.pack('>ii',im.width//2,im.height));im.save(b,format='PNG',pnginfo=meta);return b.getvalue()
def panel(s):
 w=768;h=max(112,int(768*s['height']/s['width']));im=Image.new('RGBA',(w,h),(48,54,48,255));d=ImageDraw.Draw(im)
 if s['kind']=='gauge':bg=(218,215,191);fg=(34,40,38)
 elif s['kind'] in ('exit','control'):bg=(113,48,29);fg=(241,230,193)
 else:bg=(54,77,67);fg=(232,222,181)
 d.rectangle((8,8,w-9,h-9),fill=bg,outline=(173,151,104),width=4)
 # Rivets and a solid hood distinguish a physical plate from floating type.
 for x in [20,w-21]:
  for y in [20,h-21]:d.ellipse((x-5,y-5,x+5,y+5),fill=(128,113,84));d.line((x-3,y,x+3,y),fill=(30,34,29),width=2)
 if s['lit']:
  d.rectangle((40,0,w-40,18),fill=(35,36,28));d.rectangle((72,12,w-72,25),fill=(255,218,139))
 fontsz=min(int((h-35)/len(s['text'])*.76),int((w-68)/(max(map(len,s['text']))*.63)));font=ImageFont.truetype(F,max(16,fontsz))
 step=(h-34)/len(s['text'])
 for i,t in enumerate(s['text']):d.text((w//2,35+step*(i+.5)),t,font=font,anchor='mm',fill=fg)
 if s['kind']=='gauge':
  d.line((40,h*.3,40,h-30),fill=(33,36,30),width=8)
  for y in range(int(h*.35),h-30,28):d.line((36,y,75,y),fill=(33,36,30),width=5)
  d.line((30,int(h*.53),130,int(h*.53)),fill=(153,37,20),width=10)
 if s['kind']=='dead-end':d.line((34,30,65,56),fill=(226,195,137),width=7)
 return png(im)
def wheel(frame):
 im=Image.new('RGBA',(512,576));d=ImageDraw.Draw(im)
 d.rounded_rectangle((195,0,317,576),radius=16,fill=(105,76,35),outline=(190,145,65),width=8)
 d.rectangle((171,6,341,56),fill=(39,47,42));d.rectangle((189,20,323,42),fill=(255,222,135))
 d.rounded_rectangle((82,99,430,485),radius=24,fill=(53,63,58),outline=(142,132,99),width=10)
 for x in [108,403]:
  for y in [125,456]:d.ellipse((x-12,y-12,x+12,y+12),fill=(126,131,118),outline=(24,29,25),width=5)
 color=(176,60,30) if frame==0 else (145,143,59)
 d.ellipse((107,150,405,448),fill=(24,35,30),outline=(74,49,25),width=24)
 d.ellipse((114,157,398,441),outline=color,width=24)
 for i in range(5):
  a=math.radians(i*72+(frame*35));x=256+math.cos(a)*123;y=299+math.sin(a)*123
  d.line((256,299,x,y),fill=(190,134,62),width=24)
 d.ellipse((226,269,286,329),fill=(166,124,61),outline=(52,46,27),width=7)
 d.ellipse((350,112,395,157),fill=(72,201,118) if frame else (173,67,33))
 return png(im)
def sound(seed,seconds,kind):
 rng=np.random.default_rng(seed);sr=48000;t=np.arange(int(sr*seconds))/sr
 noise=rng.normal(0,1,len(t));smooth=np.convolve(noise,np.ones(21)/21,mode='same')
 if kind=='water':v=.075*smooth+.025*np.sin(2*np.pi*147*t)*(0.5+.5*np.sin(2*np.pi*.7*t))
 else:v=(.12*smooth+.06*np.sin(2*np.pi*(135-30*t)*t))*np.sin(np.pi*np.minimum(t/seconds,1))**.5
 b=io.BytesIO();wavfile.write(b,sr,np.int16(np.clip(v,-.4,.4)*32767));return b.getvalue()
def build():
 if shutil.disk_usage(O).free<15*1024**3:raise RuntimeError('Disk below 15 GiB')
 if not C.exists():
  C.mkdir()
  for n in ['runtime-binary','bank','lib']:subprocess.run(['cp','-a','--reflink=auto',str(V3/n),str(C/n)],check=True)
  for n in ['freedoom2.wad','capture.so','native_engine.py','launcher.py','backends.py','watch_imports.py','bank.py','pd_patch.py','run.sh','load-order.json','THIRD_PARTY.md','CREDITS.md',*[f'game-{i:02}.pk3' for i in range(1,9)]]:subprocess.run(['cp','--reflink=auto',str(V3/n),str(C/n)],check=True)
  shutil.copytree(V3/'slice-licenses',C/'slice-licenses')
 shutil.copyfile(O/'v4-launcher.py',C/'launcher.py')
 z=zipfile.ZipFile(V3/'build.pk3');r={n:z.read(n) for n in z.namelist()};d,owners,styles,optional,cells=make(0);proof=audit(d,owners,styles,optional);(O/'v4-routing-proof.json').write_text(json.dumps(proof,indent=2));(O/'v4-module-manifest.json').write_text(json.dumps(dict(owners=owners,cells=[dict(x=x,y=y,module=row[0],floor=row[1]) for (x,y),row in cells.items()]),indent=2))
 def zone(n):
  if n in ['tidal_hub','gallery','optional_ward','ward_vestibule']:return 'tile'
  if n in ['east_service','east_stair','service_gate']:return 'brick'
  if n in ['sump','culvert','drain_stair','west_throat','pump_landing']:return 'wet'
  if n in ['pump','upper_pipe','shortcut_head','return_stair','shortcut_foot']:return 'pipe'
  if n.startswith('harvest'):return 'rust'
  return 'rust'
 walls={'tile':'NSW4','brick':'BRICK7','wet':'STONE2','pipe':'PIPEWAL1','rust':'METAL2'}
 for i,s in enumerate(d['sector']):
  n=owners[i];q=zone(n);s['lightlevel']={'tile':152,'brick':140,'wet':136,'pipe':136,'rust':144}[q]
  if n.startswith('harvest') or n in ('optional_ward','ward_vestibule'):s['lightlevel']=112
  if n=='exit':s['lightlevel']=224
  s['texturefloor']='NR2WATR' if n in ('sump','culvert') else 'NRFCON1';s['textureceiling']='NSF4' if q=='tile' else 'NRFCON1'
 for side in d['sidedef']:
  tex=walls[zone(owners[side['sector']])]
  for k in ['texturemiddle','texturetop','texturebottom']:
   if side.get(k,'-')!='-':side[k]=tex
 for line in d['linedef']:
  if line.get('special')==12:
   for key in ['special','arg0','arg1','arg2','playeruse','repeatspecial']:line.pop(key,None)
 r['maps/map04.wad']=wad(emit(d));(O/'cistern-v4.udmf').write_text(emit(d))
 classes=[];spawn=[]
 for i,s in enumerate(signs):
  r[f'sprites/Z{i:03}A0.png']=panel(s)
  classes.append(f'class C4Sign{i}:Actor {{ Default {{ Radius 1; Height 1; XScale {s["width"]/768}; YScale {s["width"]/768/1.2}; +NOINTERACTION +NOGRAVITY +WALLSPRITE }} States {{ Spawn: Z{i:03} A -1 '+('Bright;' if s['lit'] else ';')+' Stop; } }')
  spawn.append(f'PutSign("C4Sign{i}",({s["x"]},{s["y"]},{s["z"]}),{s["angle"]},{str(s["lit"]).lower()});')
 for i in range(5):r[f'sprites/C4WVA0.png' if i==0 else f'sprites/C4WV{chr(65+i)}0.png']=wheel(i)
 for c in controls:spawn.append(f'PutWheel(({c["x"]},{c["y"]},{c["z"]}),{c["angle"]},{c["id"]});')
 source=(O/'cistern-v4.zs').read_text().replace('// GENERATED OBJECTS','\n'.join(spawn)).replace('// GENERATED SECTOR COLOURS','\n'.join(f'level.sectors[{i}].SetColor(Color({"150,210,208" if zone(owners[i])=="tile" else "120,200,178" if zone(owners[i])=="wet" else "230,190,138" if zone(owners[i])=="brick" else "215,191,142"}));' for i in range(len(d['sector']))))
 r['cistern-slice.zs']=('\n'.join(classes)+'\n'+source).encode()
 r['SNDINFO']+=b'\nc4/valve sounds/c4valve.wav\nc4/outfall sounds/c4water.wav\n$attenuation c4/outfall 0.8\n'
 r['sounds/c4valve.wav']=sound(123,1.4,'valve');r['sounds/c4water.wav']=sound(321,3,'water')
 # A native end sequence, reached by Exit_Normal, not a HUD pretending the level ended.
 r['MAPINFO']+=b'\nmap MAP04 "The Cistern" { levelnum = 4 next = EndGame { pic = "C4END" } nointermission cluster = 104 }\ncluster 104 { }\n'
 im=Image.new('RGB',(1280,800),(18,35,34));dr=ImageDraw.Draw(im);dr.rectangle((70,70,1210,730),outline=(185,156,91),width=4)
 for y,text,size in [(235,'NULL RUN / THE CISTERN',38),(360,'OUTFALL REACHED',70),(465,'THE SLUICE IS BEHIND YOU.',28),(575,'END OF THE CISTERN SLICE',24)]:dr.text((640,y),text,font=ImageFont.truetype(F,size),anchor='mm',fill=(231,220,177))
 r['graphics/C4END.png']=png(im.convert('RGBA'))
 with zipfile.ZipFile(C/'build.pk3','w',zipfile.ZIP_DEFLATED) as zz:
  for n,b in r.items():zz.writestr(n,b)
 (O/'v4-objects.json').write_text(json.dumps(dict(signs=signs,controls=controls),indent=2))
 print('Built candidate-v4:',len(signs),'physical plates,',len(controls),'wall controls; native outfall end sequence')
if __name__=='__main__':build()
