"""Private per-run audio/transport. Backend failure never prevents the game starting."""
from pathlib import Path
import sys,os,json,time,argparse,threading,shutil,signal
sys.dont_write_bytecode=True
from watch_imports import Importer
from backends import PdBackend,StudioBackend,Validator,PD
from native_engine import Engine
O=Path(__file__).resolve().parent

def launch(args,observe=None):
 if shutil.disk_usage(O).free<15_000_000_000:raise RuntimeError('Disk below 15 GB')
 run=O/('run-'+str(time.time_ns()));run.mkdir();backend=None;engine=None;quitting=False
 requested='studio' if args.studio else 'pd' if args.pd or (not args.native and PD.exists()) else 'native'
 mode=requested;events=(run/'events.jsonl').open('w',buffering=1)
 status={'requested':requested,'mode':mode,'nr_debug':False,'run':str(run),'fallback':None,'ports':{}}
 def log(e):events.write(json.dumps(e,allow_nan=False)+'\n')
 def fallback(error):
  nonlocal backend,mode
  reason=' '.join(str(error).split())[:400] or type(error).__name__
  old=backend;backend=None;mode='native';status.update(mode=mode,fallback=reason)
  print('Null Run: native music fallback: '+reason,flush=True);log({'backend_error':reason,'fallback':'native'})
  if old:
   try:old.close()
   except Exception as exc:log({'backend_cleanup_error':str(exc)})
  if engine and engine.proc.poll() is None:
   try:engine.pulse(1073741893) # F12, owned stdin bridge only
   except Exception as exc:log({'native_switch_error':str(exc)})
 try:
  try:
   if mode=='studio':
    if not args.studio_info:raise ValueError('Studio discovery file not supplied')
    backend=StudioBackend(args.studio_info,lambda e:log({'backend':e}))
   elif mode=='pd':
    backend=PdBackend(run,args.capture)
    status['ports']={'control':backend.control_port,'clock':backend.clock_port}
  except Exception as exc:fallback(exc)
  child_env={}
  if args.capture:
   conf=run/'alsoft.conf';conf.write_text('[general]\ndrivers=wave\nfrequency=48000\n[wave]\nfile='+str(run/'native.wav')+'\n')
   child_env.update(ALSOFT_DRIVERS='wave',ALSOFT_CONF=str(conf),NULLRUN_CAPTURE='1')
  else:child_env.update(NULLRUN_VISIBLE='1',SDL_VIDEODRIVER='x11',ALSOFT_DRIVERS='pulse')
  child_env.update({f'NULLRUN_MUSIC_{k.upper()}_PORT':str(v) for k,v in status['ports'].items()})
  cfg=f'nr_music_mode {0 if mode=="native" else 1}; snd_musicvolume .7; nr_music_root "{O}/bank/native"; bind f10 "netevent nr_music_reload"; bind f11 "netevent nr_music_beat"; bind f12 "netevent nr_music_mode 0"; con_notifytime 3'
  engine=Engine(O/'runtime-binary/uzdoom',O/'capture.so',O/'freedoom2.wad',[O/x for x in json.loads((O/'load-order.json').read_text())],run/'engine',developer=False,initial_map=args.warp,sound=True,extra_config=cfg,extra_env=child_env)
  status['engine_pid']=engine.proc.pid
  def forward():
   nonlocal quitting
   for line in sys.stdin:
    words=line.strip().split()
    if words and words[0] in ('KEY','MOVE','BUTTON','QUIT'):
     try:
      engine.send(line.strip())
      if words[0]=="QUIT":quitting=True
     except (BrokenPipeError,ValueError):break
  threading.Thread(target=forward,daemon=True).start()
  (run/'ready.json').write_text(json.dumps(status,indent=2))
  valid=Validator();lastbeat=-1;started=time.monotonic();native_retry=0;native_confirmed=False
  try:watcher=Importer()
  except Exception as exc:watcher=None;fallback(exc)
  with (engine.root/'engine.log').open() as source:
   while not quitting and engine.proc.poll() is None and (not args.seconds or time.monotonic()-started<args.seconds):
    for line in source:
     if not line.startswith('NRMUSIC '):continue
     try:e=json.loads(line[8:])
     except ValueError:continue
     if valid.accept(e):
      log(e)
      if e.get('type')=='native' and e.get('ok'):native_confirmed=True
      if backend:
       try:backend.handle(e)
       except Exception as exc:fallback(exc)
    if watcher:
     try:
      changed=watcher.poll()
      if changed:
       if backend and mode=='pd':backend.send('reload 1')
       elif mode=='native':engine.pulse(1073741891)
       log({'imported':changed})
     except Exception as exc:watcher=None;fallback(exc)
    if backend:
     try:
      clock=backend.poll()
      if mode=='pd':
       if not backend.healthy():raise RuntimeError('Pd process, audio device or heartbeat failed')
       if clock and int(clock['beat'])!=lastbeat:
        engine.pulse(1073741892);lastbeat=int(clock['beat'])
     except Exception as exc:
      if not quitting:fallback(exc)
    if mode=='native' and status['fallback'] and not native_confirmed and engine.game_ready and time.monotonic()>native_retry:
     
     try:
      if engine.proc.poll() is None:engine.pulse(1073741893)
     except BrokenPipeError:pass
     native_retry=time.monotonic()+.6
    if observe:observe(engine,run,time.monotonic()-started)
    time.sleep(.01)
  status['seconds']=time.monotonic()-started
 finally:
  if engine:engine.close()
  if backend:
   try:backend.close()
   except Exception as exc:log({'backend_cleanup_error':str(exc)})
  status['mode']=mode;events.close();(run/'status.json').write_text(json.dumps(status,indent=2))
 return run

def parser():
 p=argparse.ArgumentParser();m=p.add_mutually_exclusive_group();m.add_argument('--studio',action='store_true');m.add_argument('--pd',action='store_true');m.add_argument('--native',action='store_true');p.add_argument('--studio-info');p.add_argument('--warp',type=int,choices=range(1,7),default=None);p.add_argument('--seconds',type=float,default=0);p.add_argument('--capture',action='store_true',help='private file audio; Pd -noaudio, no hardware');p.add_argument('--visible',action='store_true');return p
if __name__=='__main__':
 signal.signal(signal.SIGTERM,lambda *_:sys.exit(143))
 args=parser().parse_args();print(launch(args))
