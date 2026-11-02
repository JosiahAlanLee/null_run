#!/usr/bin/env python3
"""Offline classic-Doom sector-cluster harvester. No third-party Python dependencies.
Cuts whole sector adjacency edges only. Closed cut lines are declared socket candidates,
not production sockets; SCALE.md and native integration are mandatory next stages.
"""
import argparse, collections, hashlib, json, math, re, shutil, struct
from pathlib import Path

DEFAULT_SOURCE=Path('/home/echevarian/dev/shared/codex/doom-hydrapy-20261030/data/freedoom-0.13.0')

def wad_lumps(path):
    data=path.read_bytes()
    magic,n,offset=struct.unpack_from('<4sII',data)
    if magic not in (b'IWAD',b'PWAD') or offset+n*16>len(data):
        raise ValueError('Invalid WAD directory')
    out=[]
    for i in range(n):
        pos,size,name=struct.unpack_from('<II8s',data,offset+i*16)
        if pos+size>len(data): raise ValueError('Lump outside WAD')
        out.append((name.rstrip(b'\0').decode('ascii'),data[pos:pos+size]))
    return out

def maps(path):
    lumps=wad_lumps(path)
    for i,(name,_) in enumerate(lumps):
        if not re.fullmatch(r'(E[1-4]M[1-9]|MAP\d\d)',name): continue
        table={}
        for k,v in lumps[i+1:]:
            if re.fullmatch(r'(E[1-4]M[1-9]|MAP\d\d)',k): break
            table[k]=v
        yield name,table

def records(blob,fmt):
    if len(blob)%struct.calcsize(fmt): raise ValueError('Partial binary record')
    return list(struct.iter_unpack(fmt,blob))

def decode(table):
    return dict(vertices=records(table['VERTEXES'],'<hh'),
                lines=records(table['LINEDEFS'],'<7H'),
                sides=records(table['SIDEDEFS'],'<hh8s8s8sH'),
                sectors=records(table['SECTORS'],'<hh8s8shhh'))

def geometry(g):
    sectors=g['sectors']; vertices=g['vertices']; bounds=[[] for _ in sectors]
    adjacency=collections.defaultdict(set); edges={}; incident=collections.defaultdict(list)
    for li,(a,b,flags,special,tag,front,back) in enumerate(g['lines']):
        fs=g['sides'][front][-1] if front!=65535 else None
        bs=g['sides'][back][-1] if back!=65535 else None
        for s in {fs,bs}-{None}:
            bounds[s].extend((vertices[a],vertices[b])); incident[s].append(li)
        if fs is not None and bs is not None and fs!=bs:
            adjacency[fs].add(bs); adjacency[bs].add(fs)
            edges.setdefault(tuple(sorted((fs,bs))),[]).append(li)
    bbox=[]
    for pts in bounds:
        bbox.append((min(p[0] for p in pts),min(p[1] for p in pts),max(p[0] for p in pts),max(p[1] for p in pts)) if pts else None)
    return adjacency,edges,bbox,incident

def partitions(g):
    adjacency,edges,bbox,_=geometry(g); seams={}
    for pair,lines in edges.items():
        a,b=pair; sa,sb=g['sectors'][a],g['sectors'][b]
        length=sum(math.dist(g['vertices'][g['lines'][li][0]],g['vertices'][g['lines'][li][1]]) for li in lines)
        narrow=any(bbox[s] and min(bbox[s][2]-bbox[s][0],bbox[s][3]-bbox[s][1])<=128 and max(bbox[s][2]-bbox[s][0],bbox[s][3]-bbox[s][1])>=128 for s in pair)
        closed=any(g['sectors'][s][1]-g['sectors'][s][0]<=8 for s in pair)
        structural=any(g['lines'][li][3] in (1,26,27,28,31,32,33,34,62,88,10,21) for s in pair for li in geometry_incident(g,s))
        # Keep stair runs intact: ordinary 8/16-unit risers are not cut sites.
        stair_head=24<=abs(sa[0]-sb[0])<=64 and narrow and any(len(adjacency[s])>=3 for s in pair)
        reason='door' if closed else 'stair-head' if stair_head else 'lift-or-door' if structural else 'narrow-corridor'
        if 64<=length<=192 and (closed or narrow or stair_head or structural): seams[pair]=reason
    remaining={i for i,b in enumerate(bbox) if b}; clusters=[]
    while remaining:
        seed=min(remaining); todo=[seed]; group={seed}; remaining.remove(seed)
        while todo:
            s=todo.pop()
            for t in sorted(adjacency[s]):
                if t in remaining and tuple(sorted((s,t))) not in seams:
                    remaining.remove(t);group.add(t);todo.append(t)
        clusters.append(sorted(group))
    return clusters,seams

def geometry_incident(g,s):
    # Cached once per decoded map; avoids repeated topology construction.
    if '_incident' not in g:g['_incident']=geometry(g)[3]
    return g['_incident'][s]

def emit_udmf(g,group,scale):
    adjacency,edges,bbox,_=geometry(g); selected=set(group)
    minx=min(bbox[s][0] for s in group);miny=min(bbox[s][1] for s in group)
    base=min(g['sectors'][s][0] for s in group)
    d={k:[] for k in ('vertex','sector','sidedef','linedef','thing')};vi={};si={s:i for i,s in enumerate(group)}
    door_openings=[];sockets=[];stripped=0
    for s in group:
        floor,ceil,_,_,light,special,tag=g['sectors'][s]
        if ceil<=floor+8:
            candidates=[g['sectors'][n][1] for n in adjacency[s] if g['sectors'][n][1]>floor+56]
            ceil=min(candidates) if candidates else floor+128
            door_openings.append(s)
        d['sector'].append(dict(heightfloor=(floor-base)*scale,heightceiling=(ceil-base)*scale,
            texturefloor='NR4FLOOR',textureceiling='NR4CEIL',lightlevel=max(96,min(176,light)),special=0))
    def vert(i):
        if i not in vi:
            vi[i]=len(d['vertex']);x,y=g['vertices'][i];d['vertex'].append(dict(x=(x-minx)*scale,y=(y-miny)*scale))
        return vi[i]
    for li,line in enumerate(g['lines']):
        a,b,flags,special,tag,front,back=line
        fs=g['sides'][front][-1] if front!=65535 else None
        bs=g['sides'][back][-1] if back!=65535 else None
        if fs not in selected and bs not in selected:continue
        if special:stripped+=1
        # UDMF requires an existing front side. Reverse boundary edges if necessary.
        if fs not in selected:a,b,front,back,fs,bs=b,a,back,front,bs,fs
        both=bs in selected
        row=dict(v1=vert(a),v2=vert(b),sidefront=len(d['sidedef']),blocking=not both or bool(flags&1),blockmonsters=bool(flags&2),dontpegtop=bool(flags&8),dontpegbottom=bool(flags&16),twosided=both)
        for side,s in [(front,fs)]+([(back,bs)] if both else []):
            xo,yo,*_=g['sides'][side]
            d['sidedef'].append(dict(sector=si[s],offsetx=xo*scale,offsety=yo*scale,
                texturetop='NR4WALL',texturebottom='NR4WALL',texturemiddle='-' if both else 'NR4WALL'))
        if both:row['sideback']=row['sidefront']+1
        elif bs is not None:
            sockets.append(dict(source_line=li,source_sectors=[fs,bs],line=len(d['linedef']),
                width=round(math.dist(g['vertices'][a],g['vertices'][b])*scale,4),
                floor=d['sector'][si[fs]]['heightfloor'],orientation=round(math.degrees(math.atan2(g['vertices'][b][1]-g['vertices'][a][1],g['vertices'][b][0]-g['vertices'][a][0]))+90,4),
                status='sealed-candidate-requires-adapter'))
        d['linedef'].append(row)
    text='namespace="zdoom";\n'+''.join(k+' { '+ ' '.join(f'{a}={json.dumps(b)};' for a,b in row.items())+' }\n' for k,rows in d.items() for row in rows)
    return d,text,sockets,door_openings,stripped

def audit(d):
    # Oriented edge balance per sector, including two-sided boundaries and holes.
    balance=collections.defaultdict(collections.Counter);fail=[]
    for i,l in enumerate(d['linedef']):
        for key,sign in [('sidefront',1),('sideback',-1)]:
            if key not in l:continue
            side=d['sidedef'][l[key]];s=side['sector']
            balance[s][l['v1']]+=sign;balance[s][l['v2']]-=sign
        if l['v1']==l['v2']:fail.append(f'degenerate line {i}')
        if l['twosided'] != ('sideback' in l):fail.append(f'side mismatch {i}')
    for s in range(len(d['sector'])):
        if not balance[s] or any(balance[s].values()):fail.append(f'open sector {s}')
    return fail

def run(source,out,scale=1):
    if out.exists():raise FileExistsError(f'Refusing to overwrite {out}')
    if shutil.disk_usage(out.parent).free<15_000_000_000:raise RuntimeError('Disk under 15 GB')
    out.mkdir();catalog=[];rejected=[];map_stats=[]
    for wad in ['freedoom1.wad','freedoom2.wad']:
        source_hash=hashlib.sha256((source/wad).read_bytes()).hexdigest()
        for mapname,table in maps(source/wad):
            g=decode(table);clusters,seams=partitions(g);accepted=0
            for group in clusters:
                # Preserve complete clusters; reject large clusters instead of carving rectangles.
                if not 2<=len(group)<=64:continue
                d,text,sockets,opened,stripped=emit_udmf(g,group,scale)
                if not sockets:continue
                ident=f'{Path(wad).stem}-{mapname}-s{group[0]:04d}'
                failures=audit(d)
                if failures:rejected.append(dict(id=ident,failures=failures));continue
                p=out/(ident+'.udmf');p.write_text(text);accepted+=1
                xs=[v['x'] for v in d['vertex']];ys=[v['y'] for v in d['vertex']]
                heights=sorted({s['heightfloor'] for s in d['sector']})
                n=len(group); internal=sum(1 for a,b in geometry(g)[1] if a in group and b in group)
                feel='loop-cluster' if internal>=n else 'stepped-cluster' if len(heights)>2 else 'gallery' if max(xs)-min(xs)>2*(max(ys)-min(ys)) else 'junction-cluster'
                catalog.append(dict(id=ident,source_wad=wad,source_map=mapname,source_sectors=group,
                    source_sha256=source_hash,file=p.name,
                    bounds=[max(xs)-min(xs),max(ys)-min(ys)],floor_levels=heights,verticality=max(heights)-min(heights),
                    feel=feel,sockets=sockets,door_sectors_frozen_open=opened,line_actions_stripped=stripped,
                    seams=[dict(sectors=list(pair),kind=reason) for pair,reason in seams.items() if any(s in group for s in pair)],
                    audit='edge-balanced-closed',production_ready=False))
            map_stats.append(dict(wad=wad,map=mapname,clusters=len(clusters),accepted=accepted))
    (out/'catalog.json').write_text(json.dumps(dict(schema=1,coordinate_scale=scale,scale_status='source Doom units; production SCALE.md pending',chunks=catalog,maps=map_stats,rejected=rejected),indent=2))
    shutil.copyfile(source/'COPYING.txt',out/'FREEDOOM-COPYING.txt')
    shutil.copyfile(source/'CREDITS.txt',out/'FREEDOOM-CREDITS.txt')
    (out/'CREDITS.md').write_text('# Layout source credits\n\nFreedoom 0.13.0, contributors to the Freedoom project.\nSee FREEDOOM-COPYING.txt and FREEDOOM-CREDITS.txt.\n\n'+ '\n'.join(f"- {c['id']}: {c['source_wad']} {c['source_map']}, sectors {c['source_sectors']}" for c in catalog)+'\n')
    (out/'THIRD_PARTY.md').write_text('# Third party\n\nThese modified layout candidates derive from Freedoom 0.13.0.\nThe complete BSD-style notice is retained verbatim in FREEDOOM-COPYING.txt.\nPer-chunk source attribution appears in CREDITS.md and catalog.json.\nNo Freedoom monsters, items, sprites, textures, music or line actions are included.\nNR4 material names are integration references; these candidates are not loadable production maps.\n')
    return dict(chunks=len(catalog),maps=len(map_stats),rejected=len(rejected))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,default=DEFAULT_SOURCE);p.add_argument('--out',type=Path,required=True);p.add_argument('--scale',type=float,default=1);a=p.parse_args()
    if not math.isfinite(a.scale) or a.scale<=0:p.error('scale must be finite and positive')
    print(json.dumps(run(a.source,a.out,a.scale)))
