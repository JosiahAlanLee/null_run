from pathlib import Path
import sys,json,time
from PIL import Image
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O/'candidate'))
from native_engine import Engine
if Path('/home/echevarian/dev/shared/PLAYTEST-IN-PROGRESS').exists():raise SystemExit('Playtest lock; no engine launched')
p=O/'candidate'
e=Engine(p/'runtime-binary/uzdoom',p/'capture.so',p/'freedoom2.wad',[p/n for n in json.loads((p/'load-order.json').read_text())],O/('smoke-'+str(time.time_ns())),developer=False,initial_map=4,sound=False)
try:
 time.sleep(2);Image.fromarray(e.frame()).save(O/'spawn.png');print(e.root)
finally:e.close()
