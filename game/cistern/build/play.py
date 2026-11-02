"""Ordinary run.sh launch; manual keyboard/mouse choices from screenshots only.
No world state, positions, nav target, teleport, console commands or route script.
"""
from pathlib import Path
import subprocess,sys,time,json,threading,mmap,struct,select,os
import numpy as np
from PIL import Image
O=Path(__file__).resolve().parent;C=O/'candidate-v2'
if Path('/home/echevarian/dev/shared/PLAYTEST-IN-PROGRESS').exists():raise SystemExit('Playtest lock: no engine launched')
previous=set(C.glob('run-*'))
log=(O/'play-launch.log').open('w');p=subprocess.Popen([str(C/'run.sh'),'--native','--capture','--warp','4','--seconds','240'],cwd=C,stdin=subprocess.PIPE,stdout=log,stderr=subprocess.STDOUT,text=True)
start=time.monotonic();ready=None
while time.monotonic()-start<90:
 for r in C.glob('run-*/ready.json'):
  if r.parent not in previous:ready=r.parent
 if ready:break
 if p.poll() is not None:raise RuntimeError('Launcher failed; see play-launch.log')
 time.sleep(.1)
if not ready:raise RuntimeError('No launcher readiness')
print('READY',ready,flush=True)
f=(ready/'engine/frame').open('rb');m=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)
ff=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgba','-s','1280x800','-r','10','-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','23',str(O/'exploration-silent.mp4')],stdin=subprocess.PIPE)
events=(O/'manual-inputs.jsonl').open('w',buffering=1);running=True
keys={'w':119,'s':115,'a':97,'d':100,'f':102,'left':1073741904,'right':1073741903,'tab':9,'c':99}
def picture():
 for i in range(1000):
  a=struct.unpack_from('<Q',m,32)[0]
  if a&1:time.sleep(.001);continue
  buf=bytes(m[64:64+1280*800*4]);b=struct.unpack_from('<Q',m,32)[0]
  if a==b:return np.frombuffer(buf,dtype=np.uint8).reshape(800,1280,4)[::-1].copy()
 raise RuntimeError('No coherent frame')
def capture():
 n=0;at=time.monotonic()
 while running and p.poll() is None:
  try:
   pic=picture();ff.stdin.write(pic.tobytes());n+=1
   if n%10==0:Image.fromarray(pic).save(O/'play-current.png')
  except Exception as exc:print('Capture:',exc,flush=True);break
  time.sleep(max(0,at+n/10-time.monotonic()))
thread=threading.Thread(target=capture);thread.start()
print('Commands: w seconds, left seconds, mouse dx dy, f seconds, shot, quit',flush=True)
try:
 while p.poll() is None:
  if not select.select([sys.stdin],[],[],.2)[0]:continue
  line=sys.stdin.readline().strip()
  if not line:continue
  events.write(json.dumps(dict(t=time.monotonic()-start,input=line))+'\n');words=line.split()
  if words[0]=='quit':p.stdin.write('QUIT\n');p.stdin.flush();break
  elif words[0]=='shot':Image.fromarray(picture()).save(O/'play-current.png');print('SHOT',flush=True)
  elif words[0]=='mouse':p.stdin.write('MOVE '+words[1]+' '+(words[2] if len(words)>2 else '0')+'\n');p.stdin.flush()
  elif words[0] in keys:
   key=keys[words[0]];p.stdin.write(f'KEY 1 {key}\n');p.stdin.flush();time.sleep(float(words[1]));p.stdin.write(f'KEY 0 {key}\n');p.stdin.flush();time.sleep(.25);Image.fromarray(picture()).save(O/'play-current.png');print('SHOT',flush=True)
finally:
 running=False;thread.join();ff.stdin.close();ff.wait();events.close()
 if p.poll() is None:p.wait(timeout=20)
 log.close();m.close();f.close()
 (O/'play-run-path.txt').write_text(str(ready)+'\n')
 print('ENDED',p.returncode,flush=True)
