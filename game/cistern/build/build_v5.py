#!/usr/bin/env python3
from pathlib import Path
import zipfile,json,shutil,subprocess,re,struct,io,hashlib
from PIL import Image,ImageDraw,ImageFont,PngImagePlugin
from geometry_v5 import make
from generate import wad
from routing import Chunk,Link,Composition,prove
from build_v4 import panel,sound
O=Path(__file__).resolve().parent;C=O/'candidate-v5';V4=O/'candidate-v4';LAB=Path('/home/echevarian/dev/shared/codex/nullrun-argon-verify-20261102-0042');WEAP=Path('/home/echevarian/dev/shared/codex/nullrun-weapons-aim-20261101/weapons-aim.pk3')
def png(im):
 m=PngImagePlugin.PngInfo();m.add(b'grAb',struct.pack('>ii',im.width//2,im.height));b=io.BytesIO();im.save(b,format='PNG',pnginfo=m);return b.getvalue()
def main():
 if shutil.disk_usage(O).free<15*1024**3:raise RuntimeError('Disk below 15 GiB')
 if not C.exists():
  C.mkdir()
  for n in ['runtime-binary','bank','lib','slice-licenses']:subprocess.run(['cp','-a','--reflink=auto',str(V4/n),str(C/n)],check=True)
  for n in ['freedoom2.wad','capture.so','native_engine.py','launcher.py','backends.py','watch_imports.py','bank.py','pd_patch.py','run.sh','THIRD_PARTY.md','CREDITS.md',*[f'game-{i:02}.pk3' for i in range(1,9)]]:subprocess.run(['cp','--reflink=auto',str(V4/n),str(C/n)],check=True)
  subprocess.run(['cp','--reflink=auto',str(WEAP),str(C/'weapons-aim.pk3')],check=True)
 d,owners,styles,optional,cells=make(0)
 # Walkable graph excludes the solid 26u storage platforms; F reaches their tops.
 nodes=[i for i,n in owners.items() if not n.startswith('stores_')];links=[]
 for i,l in enumerate(d['linedef']):
  if 'sideback' not in l or l.get('blocking'):continue
  a=d['sidedef'][l['sidefront']]['sector'];b=d['sidedef'][l['sideback']]['sector']
  if a not in nodes or b not in nodes:continue
  if abs(d['sector'][a]['heightfloor']-d['sector'][b]['heightfloor'])>8:continue
  for s,t in [(a,b),(b,a)]:links.append(Link(str(i)+':'+str(s),str(s),str(t),latch={2101:'shortcut',2102:'sluice'}.get(d['sector'][t].get('id',0))))
 def node(n):return str(next(i for i,k in owners.items() if k==n))
 proof=prove(Composition([Chunk(str(i),owners[i],optional=owners[i] in optional or owners[i]=='pair_bay',unlocks=('sluice',) if owners[i]=='pump' else ('shortcut',) if owners[i]=='shortcut_foot' else ()) for i in nodes],links,node('intake'),node('exit')))
 (O/'v5-routing-proof.json').write_text(json.dumps(proof,indent=2))
 def zone(n):
  if n in ('tidal_hub','gallery','optional_ward','ward_vestibule','pair_bay'):return 'tile'
  if n in ('east_service','east_stair','service_gate'):return 'brick'
  if n in ('sump','culvert','drain_stair','west_throat','pump_landing'):return 'wet'
  if n in ('pump','upper_pipe','shortcut_head','return_stair','shortcut_foot'):return 'pipe'
  return 'rust'
 wall={'tile':'NSW4','brick':'BRICK7','wet':'STONE2','pipe':'PIPEWAL1','rust':'METAL2'}
 for i,s in enumerate(d['sector']):
  n=owners[i];s['lightlevel']=116 if n=='pair_bay' else {'tile':152,'brick':140,'wet':136,'pipe':136,'rust':144}[zone(n)]
  if n.startswith('harvest') or n in ('optional_ward','ward_vestibule'):s['lightlevel']=112
  if n=='exit':s['lightlevel']=224
  s['texturefloor']='NR2WATR' if n in ('sump','culvert') else 'NRFCON1';s['textureceiling']='NSF4' if zone(n)=='tile' else 'NRFCON1'
 for s in d['sidedef']:
  for k in ('texturemiddle','texturetop','texturebottom'):
   if s.get(k,'-')!='-':s[k]=wall[zone(owners[s['sector']])]
 for l in d['linedef']:
  if l.get('special')==12:
   for k in ('special','arg0','arg1','arg2','playeruse','repeatspecial'):l.pop(k,None)
 z=zipfile.ZipFile(V4/'build.pk3');r={n:z.read(n) for n in z.namelist()};r['maps/map04.wad']=wad(__import__('udmf').emit(d))
 with zipfile.ZipFile(C/'build.pk3','w',zipfile.ZIP_DEFLATED) as z:
  for n,b in r.items():z.writestr(n,b)
 out={}
 w=zipfile.ZipFile(C/'weapons-aim.pk3');feel=w.read('feel.zs').decode()
 # Preserve slice isolation. Weapon overlay originally contains legacy population code.
 start=feel.index('class LDPopulation');end=feel.index('class NRFeelPlayer')
 mid=re.sub(r'(override\s+void\s+(?:WorldLoaded|WorldTick)\s*\([^)]*\)\s*\{)',r'\1 if(level.levelnum==4)return;',feel[start:end]);feel=feel[:start]+mid+feel[end:]
 feel=feel.replace('class NRFeelPlayer:NRPlayer {','class NRFeelPlayer:NRPlayer {\n Default {Height 60;Radius 12;Player.ViewHeight 50;}')
 feel=feel.replace('override void RenderOverlay(RenderEvent e){let p=NRFeelPlayer', 'override void RenderOverlay(RenderEvent e){if(level.levelnum==4)return;let p=NRFeelPlayer')
 feel=feel.replace(' void QueueTick(){',' virtual void QueueTick(){')
 feel+='\nclass NEQuietImpBall:DoomImpBall replaces DoomImpBall {Default {Scale .2; RenderStyle \"Translucent\"; Alpha .32;} States {Spawn:FDST A 2;Loop;Death:FDST A 2 A_FadeOut(.08);Loop;}}\n'
 out['feel.zs']=feel.encode()
 weight=w.read('weight.zs').decode().replace('p.Angle+=yaw-s.LastYaw;p.Pitch=clamp(p.Pitch+pitch-s.LastPitch,-85.,85.);s.LastYaw=yaw;s.LastPitch=pitch;', 's.LastYaw=yaw;s.LastPitch=pitch; // Camera untouched; displacement is consumed by weapon Bob only.')
 weight=weight.replace('clamp(s.LagX*.025*mass,-.12,.12),clamp(s.LagY*.025*mass,-.12,.12)', 'clamp(s.LagX*.025*mass+s.LastYaw,-.5,.5),clamp(s.LagY*.025*mass+s.LastPitch,-2.,2.)')
 out['weight.zs']=weight.encode()
 aim=w.read('aim.zs').decode();old="p.LineAttack(p.angle,8192,p.pitch,damage,'Hitscan','NRAimPuff',LAF_NORANDOMPUFFZ|LAF_OVERRIDEZ,victim,(p.player.viewz-p.Pos.z));"
 new="FLineTraceData tr;p.LineTrace(p.Angle,8192,p.Pitch,offsetz:p.player.viewz-p.Pos.Z,data:tr);let enemy=C5Enemy(tr.HitActor);if(enemy){int k=NRMechanics.Kind(p.player.ReadyWeapon);int material=k==1?0:(k==2||k==4)?1:(k==3||k==5)?2:3;enemy.PictureHit(p,Eye(p),tr.HitDir,material,damage);}else "+old
 assert old in aim;out['aim.zs']=w.read('aim.zs') # Native Hitscan is routed through C5Enemy.DamageMobj, avoiding cross-unit coupling.
 panic=zipfile.ZipFile(LAB/'panic01/panic-lab.pk3');anat=zipfile.ZipFile(LAB/'anatomy01/anatomy-lab.pk3')
 for n in panic.namelist():
  if n.lower().startswith('sprites/nrho'):out[n]=panic.read(n)
 for n in anat.namelist():
  if re.fullmatch(r'sprites/Z[0-4][0-7][ICW]A0\.png',n,re.I):out[n.replace('/Z','/Q')]=anat.read(n)
 out['v5-mask.zs']=(LAB/'anatomy01/projection.zs').read_text().replace('NRProjection','C5Mask').encode()
 out['v5-player.zs']=(O/'v5-src/player.zs').read_bytes()
 enc=(O/'v5-src/encounters.zs').read_text()
 setup=[]
 for j,(x,y) in enumerate([(-48,-528),(48,-432),(-48,-336)]):setup.append(f'let q{j}=C5Pickup(Actor.Spawn("C5Pickup",({x},{y},26)));q{j}.Kind={j};q{j}.sprite=Actor.GetSpriteIndex("C5T{j}");')
 setup+=['BaySectors.Push('+str(i)+');level.sectors['+str(i)+'].SetColor(Color(125,190,180));' for i,n in owners.items() if n=='pair_bay']
 setup+=['GallerySectors.Push('+str(i)+');' for i,n in owners.items() if n=='gallery']
 setup.append('let a=Actor.Spawn("C5BayPlate",(-264,842,160));a.Angle=180;let lp=DynamicLight(Actor.Spawn("PointLight",(80,1000,155)));lp.args[0]=95;lp.args[1]=190;lp.args[2]=165;lp.args[3]=100;')
 registry='class C5SpriteRegistry:Actor {States {Spawn:TNT1 A -1;Stop;Register:'+' '.join(f'Q{b}{y}{p} A 0;' for b in range(5) for y in range(8) for p in 'ICW')+' C5T0 A 0; C5T1 A 0; C5T2 A 0; Stop;}}'
 enc=enc+'\n'+registry
 enc=enc.replace('// GENERATED PICKUPS AND SECTORS' ,'\n'.join(setup))
 out['v5-encounters.zs']=enc.encode()
 out['zscript']=b'version "4.14"\n#include "v5-mask.zs"\n#include "v5-player.zs"\n#include "v5-encounters.zs"\nclass C5BayPlate:Actor {Default {Radius 1;Height 1;XScale .145833;YScale .1215278;+NOINTERACTION +NOGRAVITY +WALLSPRITE}States {Spawn:C5BP A -1;Stop;}}\n'
 out['sprites/C5BPA0.png']=panel(dict(text=['PUMP INSPECTION','NO THROUGH ROUTE'],height=28,width=112,lit=False,kind='dead-end'))
 for i,(name,col) in enumerate([('MEDICAL TIN',(170,155,113)),('AMMUNITION',(110,130,116)),('SCRAP',(125,78,40))]):
  im=Image.new('RGBA',(128,64));dr=ImageDraw.Draw(im);dr.rounded_rectangle((5,6,123,63),radius=5,fill=col,outline=(37,41,34),width=5);dr.rectangle((10,6,117,17),fill=(155,150,127));dr.text((64,38),['MED','AMMO','SCRAP'][i],font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf',22),anchor='mm',fill=(25,34,28));out[f'sprites/C5T{i}A0.png']=png(im)
 out['sprites/C5TIA0.png']=out['sprites/C5T0A0.png']
 snd=[]
 for n,key in [('grip','grip'),('release','release'),('take','tap'),('repair','clatter'),('wood','drag')]:out[f'sounds/c5{n}.wav']=anat.read(f'sounds/{key}.wav');snd.append(f'c5/{n} sounds/c5{n}.wav')
 out['sounds/c5tick.wav']=panic.read('sounds/ceramic.wav');snd.append('c5/tick sounds/c5tick.wav')
 out['SNDINFO']='\n'.join(snd).encode()
 out['CVARINFO']=b'server int nr_walk_profile = 0;\n'
 menu=r['MENUDEF'].decode();start=menu.index('OptionMenu "NullRunMovementOptions"');end=menu.index('AddOptionMenu "OptionsMenu"',start)
 menu=menu[:start]+'''OptionValue "C5WalkProfiles" {0,"Careful / 2.4 m/s" 1,"Brisk / 3.65 m/s"}
OptionMenu "NullRunMovementOptions" { Title "Cyborg locomotion" Option "Walk profile", "nr_walk_profile", "C5WalkProfiles" StaticText "F7 changes profile live" Control "Hurry (hold Shift)", "+speed" Control "Overdrive (hold Alt)", "+user4" Control "Field repair (hold G)", "+user3" }
'''+menu[end:]
 out['MENUDEF']=menu.encode()
 out['MAPINFO']=b'gameinfo {PlayerClasses="C5Player" AddEventHandlers="C5Encounter","C5HUD","NRWeightVision","NRMechanismHandler"}\n'
 with zipfile.ZipFile(C/'cistern-v5.pk3','w',zipfile.ZIP_DEFLATED) as z:
  for n,b in out.items():z.writestr(n,b)
 (C/'load-order.json').write_text(json.dumps([*[f'game-{i:02}.pk3' for i in range(1,9)],'build.pk3','weapons-aim.pk3','cistern-v5.pk3'],indent=2))
 # This is player binding configuration, not console automation or test fixtures.
 launcher=(C/'launcher.py').read_text();launcher=launcher.replace("con_notifytime 3'",'''con_notifytime 3; bind alt "+user4"; bind z "+user3"; bind g "+user3"; bind f7 "netevent c5_profile"' ''') if False else launcher
 launcher=launcher.replace("con_notifytime 3'", '''con_notifytime 3; bind alt \\"+user4\\"; bind z \\"+user3\\"; bind g \\"+user3\\"; bind f7 \\"netevent c5_profile\\"' ''')
 # Avoid duplicate insertion on rebuild.
 if 'bind f7' not in (C/'launcher.py').read_text():(C/'launcher.py').write_text(launcher)
 shutil.copyfile(O/'v5-src/launcher.py',C/'launcher.py')
 (O/'v5-module-manifest.json').write_text(json.dumps(dict(owners=owners,cells=[dict(x=x,y=y,module=t[0],floor=t[1]) for (x,y),t in cells.items()]),indent=2))
 (O/'V5-ART-PROVENANCE.json').write_text(json.dumps(dict(hollow='panic01 geometric placeholder',armatures='anatomy01 debug Blender sprites with exact matching body/core masks',stone_redead='existing E2IP/E2AP project sprites retained from v4',weapons='original weapons-aim.pk3 loaded, compatibility patch isolates Cistern and moves view drift/recoil to weapon sway',pair=['C5Hollow','C5Stone']),indent=2))
 print('V5 packaged: physical pickups, paired bay, 3 coordinated armatures; placeholder Hollow/Armature art disclosed')
if __name__=='__main__':main()
