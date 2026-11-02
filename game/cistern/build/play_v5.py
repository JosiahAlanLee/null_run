"""Manual, picture-only run.sh recording. No map state, coordinates or route controller."""
from pathlib import Path
import subprocess,sys,time,json,threading,mmap,struct,select,os
import numpy as np
from PIL import Image
O=Path(__file__).resolve().parent;C=O/'candidate-v5';name=sys.argv[1]
if not name.replace('-','').isalnum():raise ValueError('Simple recording name required')
R=O/'v5-evidence'/name;R.mkdir(parents=True,exist_ok=False)
if Path('/home/echevarian/dev/shared/PLAYTEST-IN-PROGRESS').exists():raise SystemExit('Playtest lock: no engine launched')
previous=set(C.glob('run-*'));log=(R/'launch.log').open('w')
p=subprocess.Popen([str(C/'run.sh'),'--capture','--seconds','900'],cwd=C,stdin=subprocess.PIPE,stdout=log,stderr=subprocess.STDOUT,text=True)
ready=None;deadline=time.monotonic()+90
while time.monotonic()<deadline:
 for r in C.glob('run-*/ready.json'):
  if r.parent not in previous:ready=r.parent
 if ready:break
 if p.poll() is not None:raise RuntimeError('Launcher failed: '+str(R/'launch.log'))
 time.sleep(.1)
if not ready:raise RuntimeError('No readiness')
f=(ready/'engine/frame').open('rb');m=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)
ff=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgba','-s','1280x800','-r','20','-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','22',str(R/'silent.mp4')],stdin=subprocess.PIPE)
events=(R/'inputs.jsonl').open('w',buffering=1);running=True;started=time.monotonic();nframes=0;firstinput=None;finish=None
keys={'w':119,'s':115,'a':97,'d':100,'f':102,'left':1073741904,'right':1073741903,'c':99,'g':103,'r':114,'profile':1073741888,'shift':1073742049,'alt':1073742050,'fire':1073742048}
def picture():
 for _ in range(1000):
  a=struct.unpack_from('<Q',m,32)[0]
  if a&1:time.sleep(.001);continue
  buf=bytes(m[64:64+1280*800*4]);b=struct.unpack_from('<Q',m,32)[0]
  if a==b:return np.frombuffer(buf,dtype=np.uint8).reshape(800,1280,4)[::-1].copy()
 raise RuntimeError('No coherent frame')
def save(pic,path):
 tmp=path.with_suffix('.'+str(threading.get_ident())+'.tmp.png');Image.fromarray(pic).save(tmp);os.replace(tmp,path)
def capture():
 global nframes
 at=time.monotonic()
 while running and p.poll() is None:
  try:
   pic=picture();ff.stdin.write(pic.tobytes());nframes+=1
   if nframes%5==0:save(pic,R/'current.png')
  except Exception as exc:print('CAPTURE ERROR',exc,flush=True);break
  time.sleep(max(0,at+nframes/20-time.monotonic()))
def audio_prefix():
 data=(ready/'native.wav').read_bytes();at=12;rate=None
 while at+8<=len(data):
  tag=data[at:at+4];size=struct.unpack_from('<I',data,at+4)[0]
  if tag==b'fmt ':rate=struct.unpack_from('<I',data,at+16)[0]
  if tag==b'data':return (len(data)-at-8)/rate if rate else None
  at+=8+size+(size&1)
 return None
prefix=audio_prefix()
thread=threading.Thread(target=capture);thread.start();print('READY',R,flush=True)
try:
 while p.poll() is None:
  line=sys.stdin.readline().strip()
  if not line:continue
  elapsed=time.monotonic()-started;events.write(json.dumps(dict(t=elapsed,input=line))+'\n');words=line.split();cmd=words[0]
  if cmd=='quit':p.stdin.write('QUIT\n');p.stdin.flush();break
  elif cmd=='snap':
   tag=words[1] if len(words)>1 else 'shot';save(picture(),R/(tag+'.png'));save(picture(),R/'current.png');print('SHOT',round(elapsed,2),flush=True)
  elif cmd=='mark':
   if words[1]=='finish':finish=elapsed
   print('MARK',words[1],round(elapsed,2),flush=True)
  elif cmd in ('down','up'):
   if firstinput is None:firstinput=elapsed
   p.stdin.write(f'KEY {1 if cmd=="down" else 0} {keys[words[1]]}\n');p.stdin.flush()
  elif cmd=='mouse':
   if firstinput is None:firstinput=elapsed
   p.stdin.write('MOVE '+words[1]+' '+(words[2] if len(words)>2 else '0')+'\n');p.stdin.flush();time.sleep(.25);save(picture(),R/'current.png')
  elif cmd in keys:
   if firstinput is None:firstinput=elapsed
   key=keys[cmd];duration=float(words[1]);assert 0<=duration<=15
   p.stdin.write(f'KEY 1 {key}\n');p.stdin.flush();time.sleep(duration);p.stdin.write(f'KEY 0 {key}\n');p.stdin.flush();time.sleep(.25);save(picture(),R/'current.png');print('SHOT',round(time.monotonic()-started,2),flush=True)
finally:
 running=False;thread.join();ff.stdin.close();ff.wait();events.close()
 if p.poll() is None:
  try:p.stdin.write('QUIT\n');p.stdin.flush()
  except BrokenPipeError:pass
  try:p.wait(timeout=20)
  except subprocess.TimeoutExpired:p.terminate();p.wait(timeout=20)
 log.close();m.close();f.close()
 (R/'recording.json').write_text(json.dumps(dict(run=str(ready),candidate='candidate-v5',audio_prefix_seconds=prefix,capture_frames=nframes,first_input=firstinput,finish_mark=finish,route_seconds=finish-firstinput if finish is not None and firstinput is not None else None,author_informed=True,automap_used=False,coordinate_routing=False),indent=2));print('ENDED',p.returncode,flush=True)
