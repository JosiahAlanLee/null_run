#!/usr/bin/env python3
from pathlib import Path
import json,re,subprocess,zipfile,hashlib,concurrent.futures
import numpy as np
from PIL import Image,ImageDraw,ImageFont
O=Path(__file__).resolve().parent;C=O/'candidate-v5';E=O/'v5-evidence'
def movie(label,name):
 r=E/name;m=json.loads((r/'recording.json').read_text());run=Path(m['run']);log=(run/'engine/engine.log').read_text();inputs=[json.loads(l) for l in (r/'inputs.jsonl').read_text().splitlines()];commands=[x['input'] for x in inputs]
 assert all(v.split()[0] in {'w','s','a','d','f','g','r','left','right','mouse','snap','mark','quit','c','profile','shift','alt','fire','down','up'} for v in commands)
 ticks=re.findall(r'C4 COMPLETE (\d+) TICS',log)
 if ticks:
  end=m['finish_mark'];result='native Exit_Normal to C4END';assert end is not None
  # Find the first rendered end card; the operator's later mark can include thinking time.
  framefile=r/'exit.png';assert framefile.exists()
  ref=np.asarray(Image.open(framefile).convert('L').resize((96,60)),dtype=np.float32)
  raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(r/'silent.mp4'),'-vf','scale=96:60,fps=10','-pix_fmt','gray','-f','rawvideo','-'])
  frames=np.frombuffer(raw,dtype=np.uint8).reshape(-1,60,96)
  dif=np.mean(abs(frames.astype(np.float32)-ref),axis=(1,2));matches=np.flatnonzero(dif<3)
  assert len(matches)>0, 'No visually verified end card'
  end=min(end,float(matches[0])/10)

 else:
  end=next(x['t'] for x in inputs if x['input']=='mark death');result='fair death: Hollow, two telegraphed 80-point Heavy blows';assert 'C5 HEAVY_BLOW before=20 damage=80' in log
 ready=json.loads((run/'ready.json').read_text());status=json.loads((run/'status.json').read_text());assert not ready['nr_debug'] and ready['requested']=='pd' and status['mode']=='pd' and not status['fallback'];assert 'drivers=wave' in (run/'alsoft.conf').read_text()
 start=max(0,m['first_input']-1);duration=end-start+3;out=O/(label+'.mp4');prefix=m['audio_prefix_seconds']
 subprocess.run(['ffmpeg','-y','-loglevel','error','-ss',str(start),'-i',str(r/'silent.mp4'),'-ss',str(prefix+start),'-i',str(run/'native.wav'),'-t',str(duration),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','veryfast','-crf','22','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)],check=True)
 info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type,width,height,r_frame_rate','-of','json',str(out)]));assert {s['codec_type'] for s in info['streams']}=={'audio','video'}
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(out),'-vn','-f','f32le','-ac','1','-ar','12000','-']);x=np.frombuffer(raw,dtype='<f4');rms=float(np.sqrt(np.mean(x*x)));assert rms>1e-5
 alerts={}
 for pattern in ['PAIR_ALERT','REDEAD_REACH_WARN','SNARE','GRAPPLE_RELEASE','HOLLOW_CRAWL','HOLLOW_POUNCE_WARN','CERAMIC_WARNING','ARM_STRIKE','ENEMY_DEAD','AI_STUCK','PHYSICAL_PICKUP','FIELD_REPAIR']:
  alerts[pattern]=[l for l in log.splitlines() if 'C5 '+pattern in l]
 return dict(source=name,run=str(run),video=out.name,outcome=result,route_seconds=end-m['first_input'],map_exit_seconds=int(ticks[0])/35 if ticks else None,author_informed=True,automap=False,console=False,coordinate_routing=False,default_start=True,audio_rms=rms,ports=ready['ports'],events=alerts,media=info)
def audit():
 v4=zipfile.ZipFile(O/'candidate-v4/build.pk3');v5=zipfile.ZipFile(C/'build.pk3');assert v5.testzip() is None
 same={str(i):v4.read(f'maps/map{i:02}.wad')==v5.read(f'maps/map{i:02}.wad') for i in [1,2,3,5,6]};assert all(same.values())
 return dict(other_five_maps_unchanged=same,archives={n:hashlib.sha256((C/n).read_bytes()).hexdigest() for n in json.loads((C/'load-order.json').read_text())},art='Hollow and Armatures use debug placeholder sprites. Stone ReDead and weighted weapons use existing rendered project art.')
if __name__=='__main__':
 import sys
 sources=dict(x.split('=',1) for x in sys.argv[1:])
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:rs=list(pool.map(lambda p:(p[0],movie(*p)),sources.items()))
 result=dict(runs=dict(rs),package=audit());(O/'VERIFICATION-V5.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:{x:v[x] for x in ['outcome','route_seconds','video','audio_rms']} for k,v in rs},indent=2))
