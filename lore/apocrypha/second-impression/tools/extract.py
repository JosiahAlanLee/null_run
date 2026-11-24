import re, sys, unicodedata, xml.etree.ElementTree as ET
X = sys.argv[1]; OUT = sys.argv[2]
tree = ET.parse(X); root = tree.getroot()
fonts = {}
lines = []  # (page, top, left, right, kind, text)
for page in root.iter('page'):
    pn = int(page.get('number'))
    for fs in page.iter('fontspec'):
        fonts[fs.get('id')] = (int(fs.get('size')), fs.get('family').split('+')[1], fs.get('color'))
    for t in page.findall('text'):
        top = int(t.get('top')); left = int(t.get('left')); w = int(t.get('width'))
        if top < 60 or top > 1120 or pn < 3: continue
        fid = t.get('font'); size, fam, col = fonts[fid]
        raw = ''.join(t.itertext())
        raw = unicodedata.normalize('NFKC', raw).replace(' ', ' ')
        ital = t.find('.//i') is not None; bold = t.find('.//b') is not None
        lines.append(dict(p=pn, top=top, left=left, right=left+w, fid=fid, size=size, fam=fam, col=col, i=ital, b=bold, t=raw))
# group runs into physical lines
lines.sort(key=lambda d: (d['p'], d['top'], d['left']))
phys = []
for d in lines:
    if phys and phys[-1][0]['p'] == d['p'] and abs(phys[-1][0]['top'] - d['top']) <= 4:
        phys[-1].append(d)
    else:
        phys.append([d])
for g in phys: g.sort(key=lambda d: d['left'])
def esc(s):
    return re.sub(r'([#$*_@<>`\\~\[\]])', r'\\\1', s)
def render(runs):
    out = ''
    for r in runs:
        s = esc(r['t'])
        if not s.strip():
            out += s; continue
        colored = r['col'] in ('#1f4e3d', '#956a20')
        mono = 'Mono' in r['fam']
        lead = s[:len(s)-len(s.lstrip())]; trail = s[len(s.rstrip()):]; core = s.strip()
        if mono: core = '#m[' + core + ']'
        elif r['i']: core = '_' + core + '_'
        elif r['b'] and not colored: core = '*' + core + '*'
        out += lead + core + trail
    return re.sub(r' {2,}', ' ', out)
out = []; prev = None; cur = None
def flush():
    global cur
    if cur: out.append(cur)
    cur = None
pending_cap = ''
for runs in phys:
    f = runs[0]; size = f['size']; fam = f['fam']
    txt = render(runs).strip()
    if not txt: continue
    kind = 'p'
    if fam == 'DejaVuSans' and size >= 28: kind = 'part'
    elif fam == 'DejaVuSans' and size == 17: kind = 'h'
    elif size == 25: kind = 'title'
    elif size == 34: pending_cap = f['t'].strip(); continue
    elif f['col'] in ('#d1c7b5',): continue  # plate captions
    elif 'Mono' in fam and f['left'] <= 80 and len(runs) <= 2 and (f['col'] in ('#8b2a20','#956a20')): kind = 'meta'
    elif f['left'] >= 100 and size <= 15: kind = 'q'
    if kind in ('part', 'h', 'title', 'meta'):
        if cur and cur[0] == kind and prev and prev['p'] == f['p'] and f['top'] - prev['top'] < 40:
            cur[1] += ' ' + txt
        else:
            flush(); cur = [kind, txt]
        prev = f; continue
    if pending_cap:
        txt = pending_cap + txt.lstrip(); pending_cap = ''
    gap = (f['top'] - prev['top']) if (prev and prev['p'] == f['p']) else None
    join = False
    if cur and cur[0] == kind:
        if gap is None:  # page break: join if previous line looked full
            join = cur[2] > 700 and not re.search(r'[.!?:"”)]$', cur[1].replace('_','').replace('*','')) or (cur[2] > 730)
        elif kind == 'p': join = gap < 30
        else:
            fw = len(txt.split(' ')[0]) * 9
            join = gap < 26 and (cur[2] + fw > 745)
    if join:
        if cur[1].endswith('-') and not cur[1].endswith(' -'): cur[1] += txt
        else: cur[1] += ' ' + txt
        cur[2] = runs[-1]['right']
    else:
        flush(); cur = [kind, txt, runs[-1]['right']]
    prev = f
flush()
with open(OUT, 'w') as fh:
    for o in out:
        k, t = o[0], o[1]
        t = t.replace('_ _', ' ').replace('* *', ' ')
        fh.write({'part': '\n%%PART ', 'title': '\n%%TITLE ', 'h': '\n== ', 'meta': '%%META ', 'q': '> ', 'p': ''}[k] + t + '\n\n')
print(len(out), 'blocks')
