from pathlib import Path
import sys,json,time,zipfile,re,concurrent.futures
O=Path(__file__).resolve().parent;C=O/'candidate-v5';sys.path.insert(0,str(C));from native_engine import Engine
D=O/'v5-calibration';D.mkdir(exist_ok=True)
with zipfile.ZipFile(D/'probe.pk3','w') as z:
 z.writestr('ZSCRIPT','version "4.14"\n'+(O/'v5-src/calibrate.zs').read_text());z.writestr('MAPINFO','gameinfo {AddEventHandlers="C5Calibration"}')
with zipfile.ZipFile(D/'damage.pk3','w') as z:
 z.writestr('CVARINFO','server bool c5_test_low=false;')
 z.writestr('ZSCRIPT','''version "4.14"
class C5DamageProbe:EventHandler {override void WorldTick(){let p=C5Player(players[0].mo);if(!p)return;
 if(level.time==35){if(CVar.GetCVar('c5_test_low').GetBool()){p.health=2;p.player.health=2;}int before=p.health;p.DamageMobj(p,p,150,'Heavy');Console.Printf("C5DAMAGE first before=%d after=%d",before,p.health);}
 if(level.time==70&&p.health>0){int before=p.health;p.DamageMobj(p,p,150,'Heavy');Console.Printf("C5DAMAGE second before=%d after=%d",before,p.health);}}}
''');z.writestr('MAPINFO','gameinfo {AddEventHandlers="C5DamageProbe"}')
def run(case):
 if Path('/home/echevarian/dev/shared/PLAYTEST-IN-PROGRESS').exists():return case,dict(blocked='playtest lock; no engine launched')
 folder=D/(case+'-'+str(time.time_ns()));probe='damage.pk3' if case in ['heavy_high','heavy_low'] else 'probe.pk3';cfg='bind alt "+user4"; bind f7 "netevent c5_profile"; m_filter false;'
 if case=='heavy_low':cfg+='c5_test_low true;'
 e=Engine(C/'runtime-binary/uzdoom',C/'capture.so',C/'freedoom2.wad',[*[C/n for n in json.loads((C/'load-order.json').read_text())],D/probe],folder,developer=False,initial_map=4,sound=False,extra_config=cfg)
 try:
  time.sleep(4)
  if case.startswith('heavy'):time.sleep(2.7)
  else:
   if case=='brisk_live':e.pulse(1073741888)
   held=1073742049 if case=='hurry' else 1073742050 if case=='overdrive' else None
   if held:e.key(held,True)
   e.key(119,True);time.sleep(1.65 if case=='overdrive' else 4.4);e.key(119,False)
   if held:e.key(held,False)
   time.sleep(.4)
 finally:e.close()
 text=(folder/'engine.log').read_text();errors=[l for l in text.splitlines() if 'Script error' in l or 'VM execution aborted' in l]
 if errors:raise RuntimeError(errors)
 speed=[float(m) for m in re.findall(r'C5CAL speed=([\d.]+)',text)]
 events=[l for l in text.splitlines() if 'C5DAMAGE' in l or 'C5 WALK_PROFILE' in l]
 return case,dict(folder=str(folder),speed=speed[-1] if speed else None,events=events,feet=len(re.findall('C5CAL FOOT',text)),log=str(folder/'engine.log'))
if __name__=='__main__':
 cases=['careful','brisk_live','hurry','overdrive','heavy_high','heavy_low']
 with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
  r=dict(pool.map(run,cases))
 (O/'V5-CALIBRATION.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
