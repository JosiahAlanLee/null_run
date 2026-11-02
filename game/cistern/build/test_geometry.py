"""Negative tests: fail on physical faults previously absent from abstract graph."""
from pathlib import Path
from copy import deepcopy
import json
from generate import make,audit
from routing import RoutingFailure
O=Path(__file__).resolve().parent
base=make();checks=[]
def run(name,edit):
 d,own,sty,opt,cells=deepcopy(base);edit(d,own)
 try:audit(d,own,sty,opt)
 except (RoutingFailure,ValueError) as e:checks.append(dict(test=name,result='rejected',reason=str(e)));return
 raise AssertionError('Accepted invalid geometry: '+name)
run('floor seam +32 u',lambda d,o:d['sector'][next(s for s,n in o.items() if n=='gallery')].update(heightfloor=96))
run('head clearance 40 u',lambda d,o:d['sector'][next(s for s,n in o.items() if n=='culvert')].update(heightceiling=40))
run('exterior wall nonblocking',lambda d,o:next(l for l in d['linedef'] if 'sideback' not in l).update(blocking=False))
run('unclosed sector',lambda d,o:d['linedef'].pop(next(i for i,l in enumerate(d['linedef']) if 'sideback' not in l)))
# Removing the only release provider must reject exit and optional reachability.
run('release provider removed',lambda d,o:o.update({s:'gallery' for s,n in list(o.items()) if n=='pump'}))
proof=audit(*base[:4]);(O/'geometry-negative-tests.json').write_text(json.dumps(dict(valid=proof['status'],negative_tests=checks),indent=2))
print('Valid blockout passes; five deliberately broken geometries rejected')
