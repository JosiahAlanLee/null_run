from pathlib import Path
import json,struct,wave,subprocess,hashlib
import numpy as np
from PIL import Image,ImageDraw
from udmf import parse,lumps
import zipfile
O=Path(__file__).resolve().parent;C=O/'candidate-v3'
run=Path((O/'plain-launch-retry.log').read_text().strip().splitlines()[-1]);status=json.loads((run/'status.json').read_text());log=(run/'engine/engine.log').read_text()
assert status['nr_debug']==False and status['seconds']>=9
assert 'MAP04 - NULL RUN' in log
errors=[l for l in log.splitlines() if any(x in l for x in ['unconnected','Script error','Execution could not continue','Unknown texture'])];assert not errors,errors
frame=(run/'engine/frame').read_bytes();assert frame[:4]==b'NRF1'
a=np.frombuffer(frame,dtype=np.uint8,offset=64,count=1280*800*4).reshape(800,1280,4)[::-1];Image.fromarray(a).save(O/'candidate-v3-spawn.png')
old=Path((O/'play-run-path.txt').read_text().strip())
from scipy.io import wavfile
sr,raw=wavfile.read(old/'native.wav');x=raw.astype(float)
if raw.dtype.kind in 'iu':x/=float(2**(raw.dtype.itemsize*8-1))
audio=dict(channels=raw.shape[1] if raw.ndim>1 else 1,rate=sr,duration=len(raw)/sr,rms=float(np.sqrt(np.mean(x*x))),peak=float(np.max(abs(x))))
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type','-of','json',str(O/'exploration-with-audio.mp4')]))
v=dict(final_launch=dict(run=str(run),status=status,map04_started=True,errors=errors,audio_device='capture uses OpenAL wave file and Pd -noaudio; no hardware listening test'),real_play=dict(candidate='candidate-v2 before final vertex repair',duration=probe['format']['duration'],streams=probe['streams'],completed=False,independent_unassisted=False,real_input=True,default_music_mode=False,native_audio=audio),acceptance='partial; empty exploration blockout only',not_verified=['final-v3 full traversal','exit completion','shortcut operation','complete door traversal','prop audit','Mimic socket','encounters','injury/healing','GI','authored set pieces','default safety','soak','portal navigation'])
(O/'VERIFICATION.json').write_text(json.dumps(v,indent=2))
z=zipfile.ZipFile(C/'build.pk3');d=parse(dict(lumps(z.read('maps/map04.wad')))[b'TEXTMAP'].decode());hashes=json.loads((O/'base-map-hashes.json').read_text());hashes['after']={f'map{i:02}':hashlib.sha256(z.read(f'maps/map{i:02}.wad')).hexdigest() for i in range(1,7)};(O/'base-map-hashes.json').write_text(json.dumps(hashes,indent=2))
im=Image.new('RGB',(1500,1080),(18,23,28));dr=ImageDraw.Draw(im)
xs=[v['x'] for v in d['vertex']];ys=[v['y'] for v in d['vertex']];scale=min(1360/(max(xs)-min(xs)),890/(max(ys)-min(ys)))
def pos(x,y):return (70+(x-min(xs))*scale,980-(y-min(ys))*scale)
manifest=json.loads((O/'module-manifest.json').read_text());groups={}
for c in manifest['cells']:
 a=pos(c['x'],c['y']);b=pos(c['x']+32,c['y']+32);color=(45+c['floor'],65+c['floor'],85+c['floor']);dr.rectangle((a[0],b[1],b[0],a[1]),fill=color);groups.setdefault(c['module'],[]).append((c['x']+16,c['y']+16))
for l in d['linedef']:
 a=d['vertex'][l['v1']];b=d['vertex'][l['v2']];dr.line([pos(a['x'],a['y']),pos(b['x'],b['y'])],fill=(210,215,220) if 'sideback' not in l else (85,100,115),width=1)
for n,pts in groups.items():
 if 'stair' in n or 'gate' in n:continue
 x=sum(t[0] for t in pts)/len(pts);y=sum(t[1] for t in pts)/len(pts);dr.text(pos(x,y),n,fill=(255,220,130),anchor='mm')
dr.text((40,25),'CISTERN / EMITTED BLOCKOUT PLAN / NOT AN ART OR TRAVERSAL ACCEPTANCE SHEET',fill='white')
dr.text((40,55),'Hub: east stair/gallery and west culvert/drain routes; upper loop and far-side return stair; optional branches to east.',fill='white')
dr.text(pos(1320,30),'Freedoom E2M5 cluster',fill=(255,220,130),anchor='mm');im.save(O/'MAP-PLANS.jpg',quality=92)
print(json.dumps(v,indent=2))
