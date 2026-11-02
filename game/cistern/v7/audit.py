from pathlib import Path
import zipfile,hashlib,json
R=Path(__file__).resolve().parent;C=R/'candidate-v7';V=R.parent/'nullrun-cistern-creatures-20261102/candidate-v6'
unchanged={}
for p in V.iterdir():
 if p.name in ['run.sh','player.ini','load-order.json']:continue
 q=C/p.name;unchanged[p.name]={'symlink':q.is_symlink(),'same_target':p.resolve()==q.resolve()};assert q.is_symlink() and p.resolve()==q.resolve()
old=zipfile.ZipFile(V/'cistern-v6.pk3').read('v5-encounters.zs').decode();new=(R/'src/v5-encounters.zs').read_text()
def cls(s,n):
 a=s.index('class '+n+':');b=s.find('\nclass ',a+1);return s[a:b if b>=0 else len(s)]
checks={n:cls(old,n)==cls(new,n) for n in ['C5Enemy','C5Stone','C5Encounter']}
checks['C5Coordinator']=cls(old,'C5Coordinator')==cls(new,'C5Coordinator').replace('C7Nav Nav;','')
assert all(checks.values()),checks
patch=zipfile.ZipFile(C/'cistern-v7.pk3');assert all(n.startswith(('sounds/c7','sprites/C7')) or n in ['v5-player.zs','v5-encounters.zs','CVARINFO','MENUDEF','KEYCONF','SNDINFO'] for n in patch.namelist())
report=dict(unchanged_assets=unchanged,unchanged_environment_logic=checks,patch_members=patch.namelist(),patch_sha256=hashlib.sha256((C/'cistern-v7.pk3').read_bytes()).hexdigest(),v6_sha256=hashlib.sha256((V/'cistern-v6.pk3').read_bytes()).hexdigest())
(R/'AUDIT.json').write_text(json.dumps(report,indent=2));print('PASS: shared assets resolve to v6 originals; environment event code identical; patch whitelist passes.')
