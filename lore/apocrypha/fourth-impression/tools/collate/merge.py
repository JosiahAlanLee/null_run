import re, difflib, pathlib
B = pathlib.Path('/tmp/claude-0/-home-user-null-run/b5c08984-496b-52c5-b337-3ecebe9ada65/scratchpad/book')
OLD = B / 'raw_v2'; NEW = B / 'raw'
def plain(s):
    s = re.sub(r'#\w+\[|[*_\\\]]', '', s); return re.sub(r'\s+', ' ', s).strip().lower()
def blocks(t): return [b.strip() for b in re.split(r'\n\s*\n', t) if b.strip()]
def special(b): return b.startswith(('%%BLOCK', '> ', '#doc', '#dept', '%%NOTE114', '%%CANON', '%%STRATA', '%%GAP', '%%LEXNOTE'))
report = []
for i in range(1, 17):
    mine = [b for b in blocks((OLD / f'{i:02d}.txt').read_text()) if not b.startswith(('%%TITLE', '%%META', '%%PART'))]
    th = blocks(pathlib.Path(f'raw3/{i:02d}.txt').read_text())
    if i == 16:
        k = max(j for j, b in enumerate(th) if 'in the dark' in b); th = th[:k + 1]
    if i == 4:   # the dossier is a list, not a quotation
        out = []
        for b in th:
            if b.startswith('> ') and re.match(r'> \d\. \*', b): out.append(b[2:])
            elif b.startswith('> ') and out and re.match(r'\d\. \*', out[-1]) and not b.startswith('> *'): out[-1] += ' ' + b[2:]
            else: out.append(b)
        th = out
    if i == 10:
        th = [x for b in th for x in (['1. A first name.', '2. The colour of a room.', '3. What snow feels like.'] if b.startswith('> 1. A first name') else [b])]
    th = [re.sub(r'^== \*(.*)\*$', r'== \1', b) for b in th if not b.startswith('> ') and not re.fullmatch(r'(#m\[[^\]]*\]\s*)+', b)]
    thp = [plain(b) for b in th]
    # groups of my specials with the prose paragraph before and after
    groups = []; k = 0
    while k < len(mine):
        if special(mine[k]):
            j = k
            while j < len(mine) and special(mine[j]): j += 1
            prev = next((mine[q] for q in range(k - 1, -1, -1) if not special(mine[q]) and not mine[q].startswith('==')), None)
            nxt = next((mine[q] for q in range(j, len(mine)) if not special(mine[q]) and not mine[q].startswith('==')), None)
            groups.append((mine[k:j], prev, nxt)); k = j
        else: k += 1
    def best(p):
        if p is None: return (0, -1)
        pp = plain(re.sub(r'^%%NARROW \d ', '', p))
        return max(((difflib.SequenceMatcher(None, pp[:400], t[:400], autojunk=False).ratio(), j) for j, t in enumerate(thp)), default=(0, -1))
    ins = {}
    for g, prev, nxt in groups:
        if prev is None: ins.setdefault(-1, []).extend(g); continue
        r, j = best(prev)
        if r >= 0.55: ins.setdefault(j, []).extend(g); continue
        r2, j2 = best(nxt)
        if r2 >= 0.55: ins.setdefault(j2 - 1, []).extend(g); continue
        report.append(f'S-{i:02d}: UNPLACED {g[0][:50]!r} (prev {r:.2f}, next {r2:.2f})')
    out = list(ins.get(-1, []))
    for j, b in enumerate(th):
        out.append(b); out.extend(ins.get(j, []))
    # narrow passages, where the phrases survive
    for b in mine:
        m = re.match(r'%%NARROW (\d) (.{24})', b)
        if m:
            hit = [q for q, x in enumerate(out) if x.startswith(m.group(2)[:18])]
            if hit: out[hit[0]] = f'%%NARROW {m.group(1)} ' + out[hit[0]]
            else: report.append(f'S-{i:02d}: narrow lost {m.group(2)!r}')
    title = (OLD / f'{i:02d}.txt').read_text().split('\n')[0]
    (NEW / f'{i:02d}.txt').write_text(title + '\n\n' + '\n\n'.join(out) + '\n')
    report.append(f'S-{i:02d}: {len(th)} paras, {len(groups)} block groups, words {sum(len(x.split()) for x in out)}')
print('\n'.join(report))
