#!/usr/bin/env python3
"""Package actual ordinary-input recordings and their native completion receipts."""
from pathlib import Path
import json,re,subprocess,zipfile,hashlib,concurrent.futures,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.io import wavfile
from udmf import parse,lumps
O=Path(__file__).resolve().parent;C=O/'candidate-v4';E=O/'v4-evidence'
SOURCES={'east':'east-proof','west':'west-final','shortcut':'shortcut-proof'}

def movie(item):
 label,name=item;r=E/name;m=json.loads((r/'recording.json').read_text());run=Path(m['run']);log=(run/'engine/engine.log').read_text()
 ticks=re.findall(r'C4 COMPLETE (\d+) TICS',log);assert len(ticks)==1,(label,'No unique actual Exit_Normal receipt')
 assert m['finish_mark'] is not None and m['route_seconds']>0
 commands=[json.loads(l)['input'] for l in (r/'inputs.jsonl').read_text().splitlines()]
 allowed={'w','s','a','d','f','left','right','mouse','snap','mark','quit','c'}
 assert all(v.split()[0] in allowed for v in commands)
 status=json.loads((run/'status.json').read_text());ready=json.loads((run/'ready.json').read_text());assert ready['nr_debug']==False
 assert ready['requested']=='pd' and status['mode']=='pd' and not status['fallback'],status
 assert (run/'alsoft.conf').read_text().find('drivers=wave')>=0
 # Keep the entire route, including wrong turns and inspection pauses. Trim only
 # initial waiting at spawn and the surplus end-card hold after completion.
 start=max(0,m['first_input']-1);duration=m['finish_mark']-start+3
 prefix=m['audio_prefix_seconds'];assert prefix is not None
 out=O/f'{label}-route.mp4'
 subprocess.run(['ffmpeg','-y','-loglevel','error','-ss',str(start),'-i',str(r/'silent.mp4'),'-ss',str(prefix+start),'-i',str(run/'native.wav'),'-t',str(duration),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','veryfast','-crf','22','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)],check=True)
 info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type,width,height,r_frame_rate','-of','json',str(out)]))
 assert {s['codec_type'] for s in info['streams']}=={'audio','video'}
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(out),'-vn','-f','f32le','-ac','1','-ar','12000','-']);x=np.frombuffer(raw,dtype='<f4');rms=float(np.sqrt(np.mean(x*x)));assert rms>1e-5
 return label,dict(source=name,run=str(run),route_seconds=m['route_seconds'],map_clock_seconds=int(ticks[0])/35,completion='native Exit_Normal to C4END end card',commands=commands,automap_used=False,console_commands=False,coordinate_routing=False,author_informed=True,requested_backend=ready['requested'],backend=status['mode'],ports=ready['ports'],audio_rms=rms,audio_prefix_seconds=prefix,clip_start_seconds=start,clip_duration=float(info['format']['duration']),video=out.name,media=info)

def plan():
 z=zipfile.ZipFile(C/'build.pk3');d=parse(dict(lumps(z.read('maps/map04.wad')))[b'TEXTMAP'].decode());manifest=json.loads((O/'v4-module-manifest.json').read_text());objects=json.loads((O/'v4-objects.json').read_text())
 im=Image.new('RGB',(1640,1280),(17,25,29));dr=ImageDraw.Draw(im);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',16)
 xs=[v['x'] for v in d['vertex']];ys=[v['y'] for v in d['vertex']];scale=min(1390/(max(xs)-min(xs)),1060/(max(ys)-min(ys)))
 def pos(x,y):return 100+(x-min(xs))*scale,1190-(y-min(ys))*scale
 groups={}
 for c in manifest['cells']:
  a=pos(c['x'],c['y']);b=pos(c['x']+32,c['y']+32);n=c['module'];col=(62,98,104) if n in ('tidal_hub','gallery') else (50,92,79) if n in ('sump','culvert','drain_stair') else (100,77,53) if n in ('east_service','east_stair') else (72,72,65)
  dr.rectangle((a[0],b[1],b[0],a[1]),fill=col);groups.setdefault(n,[]).append((c['x']+16,c['y']+16))
 for l in d['linedef']:
  a=d['vertex'][l['v1']];b=d['vertex'][l['v2']];dr.line([pos(a['x'],a['y']),pos(b['x'],b['y'])],fill=(210,215,205) if 'sideback' not in l else (84,91,87),width=1)
 routes=[([(0,-592),(0,0),(650,0),(920,0),(920,704),(-560,704),(-560,850)],(236,179,66)), ([(0,-592),(0,0),(-704,0),(-704,704),(-560,704),(-560,850)],(78,203,215)),([(-560,840),(-560,704),(0,704),(0,310),(0,0)],(138,225,135))]
 for pts,col in routes:
  dr.line([pos(*p) for p in pts],fill=col,width=4)
  for a,b in zip(pts,pts[1:]):
   xx,yy=pos((a[0]+b[0])/2,(a[1]+b[1])/2);angle=math.atan2(-(b[1]-a[1]),b[0]-a[0]);dr.polygon([(xx+8*math.cos(angle),yy+8*math.sin(angle)),(xx+7*math.cos(angle+2.5),yy+7*math.sin(angle+2.5)),(xx+7*math.cos(angle-2.5),yy+7*math.sin(angle-2.5))],fill=col)
 for i,s in enumerate(objects['signs']):
  x,y=pos(s['x'],s['y']);dr.ellipse((x-3,y-3,x+3,y+3),fill=(245,238,208));dr.text((x+4,y-10),str(i+1),font=font,fill=(225,219,196))
 for i,c in enumerate(objects['controls']):
  x,y=pos(c['x'],c['y']);dr.ellipse((x-8,y-8,x+8,y+8),fill=(208,66,34),outline=(255,225,170),width=2);dr.text((x+10,y),f'C{i+1}',font=font,fill=(255,204,134))
 for name,text in [('tidal_hub','G1 / HUB'),('gallery','W3 / GALLERY'),('sump','S-4a / SUMP'),('pump','V-07 / PUMP'),('exit','OUTFALL / EXIT'),('optional_ward','INSPECTION'),('upper_pipe','WEIR WALK')]:
  pts=groups[name];x=sum(p[0] for p in pts)/len(pts);y=sum(p[1] for p in pts)/len(pts);dr.text(pos(x,y),text,font=font,fill=(255,240,193),anchor='mm')
 x,y=pos(-448,1205);dr.rectangle((x-90,y-18,x+90,y+18),outline=(120,255,172),width=3);dr.text((x,y),'EXIT / END CARD',font=font,fill=(160,255,190),anchor='mm')
 dr.text((40,22),'THE CISTERN / CANDIDATE V4 / EMITTED GEOMETRY + PHYSICAL OBJECTS',font=font,fill='white')
 dr.text((40,53),'Gold: east route   Cyan: west route   Green: return shortcut   White numbers: signs (v4-objects.json)',font=font,fill='white')
 dr.text((40,84),'C1: outfall wheel   C2: far-side shortcut wheel   C3/C4: service door wheels   C5: exit handle',font=font,fill='white')
 im.save(O/'MAP-PLANS.jpg',quality=94)

def sheet():
 views=[('west-final/hub.png','G1: two maintained routes'),('east-proof/service.png','Brick service run: physical F control'),('west-final/sump-approach.png','S-4a: water, gauge and drain-head pull'),('east-proof/gallery.png','W3: gallery / no-through-route branch'),('shortcut-proof/shortcut-open-wide.png','Far-side release: return to G1'),('shortcut-proof/outfall-pull.png','V-07: the open outfall threshold')]
 im=Image.new('RGB',(1920,912),(15,23,27));dr=ImageDraw.Draw(im);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',19)
 for i,(file,caption) in enumerate(views):
  pic=Image.open(E/file).convert('RGB').resize((640,400),Image.Resampling.LANCZOS);x=(i%3)*640;y=(i//3)*456;im.paste(pic,(x,y));dr.text((x+12,y+414),caption,font=font,fill=(240,226,192))
 im.save(O/'SLICE-SHEET.jpg',quality=94)

def audit():
 z=zipfile.ZipFile(C/'build.pk3');v3=zipfile.ZipFile(O/'candidate-v3/build.pk3');assert z.testzip() is None
 same={f'MAP{i:02}':z.read(f'maps/map{i:02}.wad')==v3.read(f'maps/map{i:02}.wad') for i in [1,2,3,5,6]};assert all(same.values())
 d=parse(dict(lumps(z.read('maps/map04.wad')))[b'TEXTMAP'].decode());assert [t['type'] for t in d['thing']]==[1]
 used={l[k] for l in d['linedef'] for k in ('v1','v2')};seen=set()
 for i in used:
  v=d['vertex'][i];p=(v['x'],v['y']);assert p not in seen;seen.add(p)
 return dict(package_crc='pass',other_maps_unchanged=same,things=[1],creatures='none; no creature spawners in CisternSlice',duplicate_used_vertices=0,build_sha256=hashlib.sha256((C/'build.pk3').read_bytes()).hexdigest())
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:routes=dict(pool.map(movie,SOURCES.items()))
 package=audit();plan();sheet();result=dict(routes=routes,package=package,limitations=['Author-informed, not an independent stranger test.','No speaker/hardware audio test; private wave capture.','Recordings retain wrong turns and pauses; only initial waiting and surplus end-card hold trimmed.'])
 (O/'VERIFICATION-V4.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:dict(seconds=v['route_seconds'],video=v['video'],audio_rms=v['audio_rms']) for k,v in routes.items()},indent=2))
