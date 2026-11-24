import pathlib, re
B = pathlib.Path('/tmp/claude-0/-home-user-null-run/b5c08984-496b-52c5-b337-3ecebe9ada65/scratchpad/book'); R = B / 'raw'
def sub(f, a, b):
    p = R / f; s = p.read_text(); assert a in s, (f, a[:40]); p.write_text(s.replace(a, b, 1))
sub('04.txt', '—abuilding', '—a building')
old4 = (B / 'raw_v2' / '04.txt').read_text()
entry = old4[old4.index('%%BLOCK entry'):]; entry = entry[:entry.index('\n\n', entry.index('> '))]
s = (R / '04.txt').read_text(); k = s.index('Retained as Counterweights'); k = s.index('\n\n', k)
(R / '04.txt').write_text(s[:k] + '\n\n' + entry + s[k:])
s = (R / '14.txt').read_text()
s = re.sub(r'(?m)^\*([A-Z][^*]*?\.)\*', r'#hw[\1]', s).replace('\n\n#hw[Iron Pin', '\n\n%%GAP\n\n#hw[Iron Pin')
(R / '14.txt').write_text(s)
def narrow(f, pairs):
    p = R / f; s = re.sub(r'%%NARROW \d ', '', p.read_text())
    for k, a in pairs:
        assert ('\n\n' + a) in s, (f, a); s = s.replace('\n\n' + a, f'\n\n%%NARROW {k} ' + a, 1)
    p.write_text(s)
narrow('11.txt', [(1, 'The unplugged lamp above the far booth burned on'), (2, 'Doyle held the zero mark on the jamb.'), (3, '"Two hundred and ten feet," Krell said.')])
narrow('13.txt', [(1, '"There\'s a lake behind that glass,"'), (2, 'I lifted my Hasselblad'), (3, '"Leave the shutter,"'), (4, 'I lowered the camera.')])
narrow('06.txt', [(1, 'Somewhere behind the ticket booth a motor ran down.')])
print('postfix ok')
for f in sorted(R.glob('[0-9][0-9].txt')):
    s = f.read_text(); o = None
    while o != s:
        o = s; s = re.sub(r'#m\[([^\]]*)\] ?#m\[([^\]]*)\]', r'#m[\1 \2]', s)
    for a, b in (('PERSON NEL', 'PERSONNEL'), ('EQUIP MENT', 'EQUIPMENT'), ('AWAIT ING', 'AWAITING'), ('ASSESS MENT', 'ASSESSMENT')):
        s = s.replace(a, b)
    f.write_text(s)
print('mono merged')
def blocks(f): return [b for b in re.split(r'\n\s*\n', (R / f).read_text()) if b.strip()]
def save(f, bl): (R / f).write_text('\n\n'.join(bl) + '\n')
bl = []
for b in blocks('04.txt'):
    if b.startswith('FROM: NEW YORK STATION (CABLE) '):
        b = b[b.index('IMMEDIATELY') + len('IMMEDIATELY'):].strip()
        if not b: continue
    bl.append(b)
save('04.txt', bl)
bl = blocks('07.txt')
for k, b in enumerate(bl):
    if b.startswith('Navarro entered the figure in the field notebook in pencil:'): bl[k] = 'Navarro entered the figure in the field notebook in pencil:'
save('07.txt', bl)
for f in ('08.txt', '10.txt'):
    bl = blocks(f); out = []
    for b in bl:
        if b == '%%BLOCK doc' or (b.startswith('> ') and out is not None and (b.startswith('> DISPOSITION') or b.startswith('> 22:00') or b.startswith('> 02:00'))): continue
        out.append(b)
    save(f, out)
print('duplicates removed')
for f, a, b in (('04.txt', '1842.1', '1842.'), ('04.txt', "'93.2 Rook", "'93. Rook"), ('10.txt', '1953.1 I have', '1953. I have')):
    sub(f, a, b)
for f, a, b in (('06.txt', 'Exit 471 on', 'Exit 47 on'), ('08.txt', 'pH 7.23 for', 'pH 7.2 for'), ('09.txt', '06:004 for', '06:00 for'), ('09.txt', 'page 1195 were', 'page 119 were')):
    sub(f, a, b)
