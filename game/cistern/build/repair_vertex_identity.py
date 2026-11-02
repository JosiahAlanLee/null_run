from pathlib import Path
import zipfile,json
from generate import make,audit,wad
from udmf import emit
O=Path(__file__).resolve().parent;P=O/'candidate-v3/build.pk3'
z=zipfile.ZipFile(P);r={n:z.read(n) for n in z.namelist()};z.close()
old=O/'pre-vertex-repair-map04.wad'
if old.exists():raise FileExistsError(old)
old.write_bytes(r['maps/map04.wad'])
d,own,sty,opt,cells=make(0);proof=audit(d,own,sty,opt)
proof.update(requested_seed=0,accepted_seed=0,rerolls=0,rejections=[])
r['maps/map04.wad']=wad(emit(d))
with zipfile.ZipFile(P,'w',zipfile.ZIP_DEFLATED) as z:
 for n,b in r.items():z.writestr(n,b)
(O/'cistern.udmf').write_text(emit(d));(O/'geometry-proof.json').write_text(json.dumps(proof,indent=2))
print('Welded vertex identities; retained old map for failure evidence')
