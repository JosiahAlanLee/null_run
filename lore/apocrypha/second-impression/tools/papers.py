#!/usr/bin/env python3
"""Lift the cabinet papers (bible C5) and the corpus documents the game does
not carry in full (bible D2) into build/papers.typ, verbatim."""
import re, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
src = (ROOT / 'sources' / 'LORE-BIBLE-20261124.md').read_text().split('\n')


def esc(s):
    s = re.sub(r'([#$*_@<>`\\~\[\]])', r'\\\1', s)
    return s.replace('//', '\\/\\/')


def section(a, b):
    out, i = [], a
    while i < b:
        m = re.match(r'#{3,4} ([A-Z][A-Z0-9]*-\d+): (.*)', src[i])
        if not m:
            i += 1; continue
        pid, title = m.group(1), m.group(2)
        meta, contra, body = '', '', []
        i += 1
        while i < b and not src[i].startswith('```'):
            ln = src[i].strip()
            if ln.startswith('*Layer'):
                meta = re.sub(r'^\*Layer L\d \(([^)]*)\); ', '', ln).rstrip('*')
            elif ln.startswith('*Contradicts'):
                contra = ln.strip('*')
            i += 1
        i += 1
        while i < b and not src[i].startswith('```'):
            body.append(src[i]); i += 1
        i += 1
        while body and not body[-1].strip():
            body.pop()
        lines = ' \\\n'.join(esc(l) if l.strip() else '#v(-0.25em)' for l in body)
        out.append(f'#cabpaper("{pid}", [{esc(title)}], [{esc(meta)}], [{esc(contra)}])[\n{lines}\n]')
    return out


def find(pat, start=0):
    for i in range(start, len(src)):
        if src[i].startswith(pat):
            return i
    raise SystemExit('not found: ' + pat)


c5 = find('## C5. The cabinet papers'); d = find('# Part D.'); d2a = find('### Never placed'); d2b = find('### In the terminals as opening lines only'); d3 = find('## D3.')
A, B, C = section(c5, d), section(d2a, d2b), section(d2b, d3)
t = '#import "../lib.typ": *\n\n'
t += '#let cabinet = [\n' + '\n\n'.join(A) + '\n]\n\n#let unplaced = [\n' + '\n\n'.join(B) + '\n]\n\n#let openings = [\n' + '\n\n'.join(C) + '\n]\n'
(ROOT / 'build').mkdir(exist_ok=True)
(ROOT / 'build' / 'papers.typ').write_text(t)
print('papers:', len(A), len(B), len(C))
