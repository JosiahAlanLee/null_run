#!/usr/bin/env python3
"""Fail-closed finite-state routing proof for a chunk/socket composition.
This operates before an emitter, but is not yet wired into build e's emitter.
No geometry reachability is inferred from sector adjacency alone.
"""
from collections import defaultdict,deque
from dataclasses import dataclass,field
import argparse,json,random
from pathlib import Path

class RoutingFailure(ValueError): pass

@dataclass(frozen=True)
class Chunk:
    id:str
    feel:str
    keys:tuple=()
    optional:bool=False
    # Available only while standing in this chunk; persistent across return visits.
    unlocks:tuple=()

@dataclass(frozen=True)
class Link:
    id:str
    source:str
    target:str
    key:str|None=None
    latch:str|None=None
    kind:str='walk'  # walk, stair, lift, drop; all are directed
    source_socket:str='out'
    target_socket:str='in'

@dataclass
class Composition:
    chunks:list
    links:list
    start:str
    exit:str
    placements:dict=field(default_factory=dict)

    def document(self):
        from dataclasses import asdict
        return asdict(self)

def prove(c,max_states=100000):
    nodes={n.id:n for n in c.chunks}
    if len(nodes)!=len(c.chunks) or c.start not in nodes or c.exit not in nodes:raise RoutingFailure('Invalid chunk IDs/start/exit')
    if len({e.id for e in c.links})!=len(c.links):raise RoutingFailure('Duplicate link ID')
    key_names=sorted({k for n in c.chunks for k in n.keys}); latch_names=sorted({k for n in c.chunks for k in n.unlocks})
    kb={k:1<<i for i,k in enumerate(key_names)};lb={k:1<<i for i,k in enumerate(latch_names)}
    adj=defaultdict(list)
    for e in c.links:
        if e.source not in nodes or e.target not in nodes:raise RoutingFailure('Unknown link endpoint')
        if e.key is not None and e.key not in kb:raise RoutingFailure('Lock has no key provider: '+e.id)
        if e.latch is not None and e.latch not in lb:raise RoutingFailure('Latch has no release: '+e.id)
        if e.kind not in ('walk','stair','lift','drop'):raise RoutingFailure('Unknown traversal kind')
        adj[e.source].append(e)
    def enter(node,keys,latches):
        for k in nodes[node].keys:keys|=kb[k]
        return node,keys,latches
    start=enter(c.start,0,0);q=deque([start]);seen={start};reverse=defaultdict(set);moves={};used=set();transitions=0
    while q:
        state=q.popleft();node,keys,latches=state;nexts=[]
        for latch in nodes[node].unlocks:
            if not latches&lb[latch]:nexts.append(((node,keys,latches|lb[latch]),'release:'+latch))
        for e in adj[node]:
            if e.key is not None and not keys&kb[e.key]:continue
            if e.latch is not None and not latches&lb[e.latch]:continue
            nexts.append((enter(e.target,keys,latches),e.id));used.add(e.id)
        moves[state]=nexts
        for dest,label in nexts:
            transitions+=1;reverse[dest].add(state)
            if dest not in seen:
                seen.add(dest);q.append(dest)
                if len(seen)>max_states:raise RoutingFailure('State budget exhausted; no proof emitted')
    exits={s for s in seen if s[0]==c.exit}
    if not exits:raise RoutingFailure('Exit unreachable')
    # Every reachable inventory/latch state must retain a path to the exit.
    # This is stronger than checking one-way edges in the initial key state.
    safe=set(exits);q=deque(exits)
    while q:
        for s in reverse[q.popleft()]:
            if s not in safe:safe.add(s);q.append(s)
    stranded=seen-safe
    if stranded:raise RoutingFailure('Reachable softlock states: '+str(len(stranded)))
    visited={s[0] for s in seen}
    missing={n.id for n in c.chunks if n.optional}-visited
    if missing:raise RoutingFailure('Optional chunks unreachable: '+','.join(sorted(missing)))
    unreachable_keys=[k for k in key_names if not any(s[1]&kb[k] for s in seen)]
    if unreachable_keys:raise RoutingFailure('Keys unreachable: '+','.join(unreachable_keys))
    unused={e.id for e in c.links if e.key is not None or e.latch is not None}-used
    if unused:raise RoutingFailure('Unsatisfiable lock dependency: '+','.join(sorted(unused)))
    drops=[e.id for e in c.links if e.kind=='drop' and e.id in used]
    return dict(status='proved-abstract-routing',states=len(seen),transitions=transitions,reachable_chunks=sorted(visited),
        optional_chunks=sorted(n.id for n in c.chunks if n.optional),satisfiable_locks=sorted(e.id for e in c.links if e.key is not None or e.latch is not None),safe_drops=drops,
        assumptions=['All declared socket traversals are physically valid','Keys are collectible on entry','Far-side releases are operable at their declared chunk','Lifts and doors have unlimited reuse','No consumable keys','No combat locks','Exit is available at every exit state'])

def candidate(seed,harvest_ids):
    """Topology prototype: weighted key placement may fail; rejection is intentional."""
    rng=random.Random(seed)
    key_at=rng.choice(['hub','gallery','sump','exit'])
    chunks=[Chunk('start','tunnel'),Chunk('hub','lightwell'),Chunk('gallery','balcony',keys=('brass',) if key_at=='gallery' else ()),
        Chunk('sump','culvert',keys=('brass',) if key_at=='sump' else ()),Chunk('pump','machinery',unlocks=('shortcut',)),
        Chunk('optional','ward',optional=True),Chunk('exit','stair',keys=('brass',) if key_at=='exit' else ())]
    if key_at=='hub':chunks[1]=Chunk('hub','lightwell',keys=('brass',))
    links=[]
    def directed(a,b,**kw):links.append(Link(a+'>'+b,a,b,**kw))
    def pair(a,b,**kw):directed(a,b,**kw);directed(b,a,**kw)
    pair('start','hub');pair('hub','gallery',kind='stair');pair('hub','sump');pair('gallery','pump',key='brass');pair('sump','pump',key='brass')
    pair('pump','hub',latch='shortcut');pair('gallery','optional');directed('pump','exit',kind='drop')
    placements={'gallery':rng.choice(harvest_ids),'sump':'kit/culvert','hub':'authored/tidal-lightwell','optional':'authored/vacant-ward'}
    return Composition(chunks,links,'start','exit',placements)

def compose(seed,harvest_ids,max_attempts=32):
    rejected=[]
    for attempt in range(max_attempts):
        c=candidate(seed+attempt,harvest_ids)
        try:proof=prove(c)
        except RoutingFailure as e:rejected.append(dict(seed=seed+attempt,reason=str(e)));continue
        return c,dict(seed=seed+attempt,requested_seed=seed,rerolls=len(rejected),rejections=rejected,proof=proof,
            status='topology-only; no production geometry emitted')
    raise RoutingFailure('No valid composition within re-roll budget')

def main():
    p=argparse.ArgumentParser();p.add_argument('--catalog',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--seed',type=int,default=41101);a=p.parse_args()
    if a.out.exists():raise FileExistsError(a.out)
    ids=[c['id'] for c in json.loads(a.catalog.read_text())['chunks']]
    c,proof=compose(a.seed,ids)
    a.out.write_text(json.dumps(dict(composition=c.document(),validation=proof),indent=2));print(json.dumps(proof))
if __name__=='__main__':main()
