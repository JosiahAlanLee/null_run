#!/usr/bin/env python3
"""Lift the cabinet papers (bible C5) and the corpus documents the game does
not carry in full (bible D2) into build/papers.typ, verbatim."""
import re, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
src = (ROOT / 'sources' / 'LORE-BIBLE-20261124.md').read_text().split('\n')


def esc(s):
    s = re.sub(r'([#$*_@<>`\\~\[\]])', r'\\\1', s)
    return s.replace('//', '\\/\\/')


CITED = set('L1-01 L1-04 L1-05 L1-06 L1-13 L1-27 L1-41 L1-43 L2-01 L2-18 L2-19 L2-20 L3-01 L3-15 L4-05 L4-15 L4-16 L4-21'.split())
TITLES = re.compile(r'Petition (16|17|20|21|22)-C|53/112|53/118|53/119|18/53|53/4\b|53/6\b|53/9\b|Gate Log|Field Book|Survey Monuments|Boring Log|Appointments Ledger|Acoustic Survey|Printed Office')
def keep(pid, title):
    return pid in CITED or bool(TITLES.search(title))


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
        if not keep(pid, title):
            continue
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
