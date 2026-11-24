import json, re, collections, pathlib
pages = {int(k): v for k, v in json.load(open('pages.json')).items()}
BODYCOL = ('#181918', '#2a241e', '#2c2925')
FLOW = (6, 11, 13)
starts = {}
for pn, L in pages.items():
    for d in L:
        m = re.fullmatch(r'S-(\d\d)', d['t'].strip())
        if m and d['fam'] == 'Noto-Sans-Mono' and d['b'] and d['col'] == '#8c2a21' and d['top'] < 400:
            starts.setdefault(int(m.group(1)), pn)
def esc(s): return re.sub(r'([#$*_@<>`\\~\[\]])', r'\\\1', s)
def render(runs):
    o = ''
    for r in runs:
        s = esc(r['t'])
        if not s.strip(): o += s; continue
        lead = s[:len(s) - len(s.lstrip())]; trail = s[len(s.rstrip()):]; core = s.strip()
        if 'STRUCK: FORM 9-B' in r['t']: core = '#struck'
        elif r['fam'] == 'TeX-Gyre-Cursor': core = '#m[' + core + ']'
        elif r['col'] == '#8c2a21' and r['size'] == 18: core = '#x[' + core + ']'
        elif r['i']: core = '_' + core + '_'
        elif r['b']: core = '*' + core + '*'
        o += lead + core + trail
    return re.sub(r' {2,}', ' ', o)
out = pathlib.Path('raw3'); out.mkdir(exist_ok=True)
order = sorted(starts)
for n in order:
    p0 = starts[n]
    p1 = (starts[order[order.index(n) + 1]] if n < 16 else p0 + 6)
    blocks = []; cur = None; cap = ''; prev = None; done = False
    for pn in range(p0, p1):
        L = [d for d in pages[pn] if (d['fam'].startswith('TeX-Gyre-Pagella') and d['size'] in (18, 19) and d['col'] in BODYCOL + ('#8c2a21',)) or d['size'] == 48
             or (d['fam'] == 'TeX-Gyre-Cursor' and d['size'] == 16 and d['col'] in ('#242624', '#8c2a21'))]
        L = [d for d in L if not re.fullmatch(r'\s*\d{1,2}\s*', d['t'])]
        if any('Schola' in d['fam'] and d['size'] >= 17 for d in pages[pn]): continue      # a foreign leaf
        L.sort(key=lambda d: (d['top'], d['left']))
        lines = []
        for d in L:
            if lines and abs(lines[-1][0]['top'] - d['top']) <= 5: lines[-1].append(d)
            else: lines.append([d])
        for runs in lines:
            runs.sort(key=lambda d: d['left'])
            f = runs[0]
            if f['fam'] == 'TeX-Gyre-Cursor' and len(runs) == 1 and f['left'] > 100 and f['col'] == '#8c2a21': continue
            if f['size'] == 48: cap = f['t'].strip(); captop = f['top']; continue
            txt = render(runs).strip()
            if not txt: continue
            kind = 'h' if (f['size'] == 19 and f['b']) else ('q' if f['left'] >= 100 and n not in FLOW and not (cap or (prev and prev.get('capzone'))) else 'p')
            if cap:
                txt = cap + txt; cap = ''; f['capzone'] = True; kind = 'p'
            elif prev is not None and prev.get('capzone') and f['left'] > 95 and f['top'] - prev['top'] < 30 and prev.get('pn') == pn:
                f['capzone'] = True; kind = 'p'
            gap = f['top'] - prev['top'] if (prev is not None and prev.get('pn') == pn) else None
            join = False
            if cur and cur[0] == kind and kind != 'h':
                if gap is None: join = cur[2] > 780 and not re.search(r'[.!?:"”]$', cur[1].replace('_', '').replace('*', ''))
                else: join = gap < 35 and (kind == 'p' or cur[2] + len(txt.split(' ')[0]) * 9 > cur[3] - 8)
            elif cur and cur[0] == 'h' and kind == 'h' and gap is not None and gap < 34: join = True
            if not join and cur and cur[0] == kind == 'p' and (txt[0].islower() or cur[1].endswith('‐')): join = True
            if join:
                if cur[1].endswith('‐'): cur[1] = cur[1][:-1] + txt
                else: cur[1] += ('' if cur[1].endswith('-') and not cur[1].endswith(' -') else ' ') + txt
                cur[2] = runs[-1]['right']; cur[3] = max(cur[3], cur[2])
            else:
                if cur: blocks.append(cur)
                cur = [kind, txt, runs[-1]['right'], max(runs[-1]['right'], 700 if kind == 'q' else 790)]
            f['pn'] = pn; prev = f
    if cur: blocks.append(cur)
    t = ''
    for k, s, _, _ in blocks:
        s = s.replace('‐_ _', '').replace('‐* *', '').replace('‐ ', '').replace('‐', '').replace('_ _', ' ').replace('* *', ' ')
        s = re.sub(r'(?<=[a-z.;:!?”’)—_])\d{1,2}(,\d{1,2})+(?!\d)', '', s)
        s = re.sub(r'(?<!\d[.,:])(?<=[a-z.,;:!?”’)—_])\d{1,2}(?![\d]|[.,:]\d)', '', s)
        s = s.replace('“', '"').replace('”', '"').replace('’', "'").replace('‘', "'")
        t += {'h': '== ', 'q': '> ', 'p': ''}[k] + s + '\n\n'
    (out / f'{n:02d}.txt').write_text(t)
    print(n, p0, p1, len(t.split()), sum(1 for b in blocks if b[0] == 'q'), sum(1 for b in blocks if b[0] == 'h'))
for f, a, b in (('11', '53/119,7 where', '53/119, where'), ('16', 'Section 161,2 with', 'Section 16 with'), ('16', 'stone post,4,5 and', 'stone post, and')):
    q = out / f'{f}.txt'; q.write_text(q.read_text().replace(a, b))
