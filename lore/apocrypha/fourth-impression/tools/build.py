#!/usr/bin/env python3
"""Assemble the second impression.

raw/NN.txt   the sixteen records as extracted from the first impression
notes/NN.txt the apparatus: substitutions, footnotes by hand, marginalia, threads
-> build/sNN.typ, then main.typ is compiled to PDF.

Apparatus file format, one entry per '@' line:
  @S old text            substitution; the following lines up to the next '@'
  => new text            are the replacement (after '=>')
  @C anchor              compiler footnote placed after the anchor
  @A anchor              audit footnote
  @P anchor              petitioner footnote
  @CA anchor             compiler, then audit after a line holding only '||'
  @E anchor              earlier hand, in the margin
  @T key anchor          thread arrow
The anchor must occur in the record. The first occurrence is used unless the
kind carries a number, as in @T2 dust anchor (second occurrence).
"""
import re, sys, pathlib, typst

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW, NOTES, OUT = ROOT / 'raw', ROOT / 'notes', ROOT / 'build'
OUT.mkdir(exist_ok=True)
problems = []
SPECIAL = {'%%NOTE114': '#note114', '%%CANON': '#canon', '%%STRATA': '#strata', '%%GAP': '#lexgap'}


def convert(raw):
    blocks = [b.strip() for b in re.split(r'\n\s*\n', raw) if b.strip()]
    out, quote = [], []

    def flushq():
        if quote:
            out.append('#' + kind[0] + '[\n' + ' \\\n'.join(quote) + '\n]')
            quote.clear()
            kind[0] = 'q'
    kind = ['q']
    for b in blocks:
        if b.startswith('%%BLOCK '):
            flushq()
            kind[0] = b.split()[1]
            continue
        if b.startswith('%%NARROW '):
            flushq()
            _, k, rest = b.split(' ', 2)
            out.append(f'#narrow({k})[{rest}]')
            continue
        if b.startswith('%%LEXNOTE '):
            flushq()
            out.append('#lexnote[' + b[10:] + ']')
            continue
        if b in SPECIAL:
            flushq()
            out.append(SPECIAL[b])
            continue
        if b.startswith('%%'):
            continue
        if b.startswith('> '):
            quote.append(b[2:])
            continue
        flushq()
        if b.startswith('== '):
            out.append('#sec[' + b[3:] + ']')
        else:
            out.append(b)
    flushq()
    text = '\n\n'.join(out)
    text = text.replace('//', '\\/\\/')
    text = re.sub(r"(?<![A-Za-z])'(\d\d)\b", r'’\1', text)
    return text


def nth_index(text, anchor, n):
    i = -1
    for _ in range(n):
        i = text.find(anchor, i + 1)
        if i < 0:
            return -1
    return i


def apply(text, notes, name):
    entries = re.split(r'(?m)^@', notes)
    for e in entries[1:]:
        head, _, body = e.partition('\n')
        mt = re.match(r'([A-Z]+)(\d*)\s+(.*)', head)
        if not mt:
            problems.append(f'{name}: bad head {head!r}')
            continue
        kind, num, rest = mt.group(1), int(mt.group(2) or 1), mt.group(3).strip()
        body = body.strip()
        if kind == 'S':
            new = body[2:].lstrip(' ') if body.startswith('=>') else body
            if new.startswith('\n'):
                new = new[1:]
            c = text.count(rest)
            if c != 1:
                problems.append(f'{name}: S anchor x{c}: {rest[:60]!r}')
                if c == 0:
                    continue
            text = text.replace(rest, new, 1)
            continue
        if kind == 'T':
            key, _, rest = rest.partition(' ')
            ins = f'#th("{key}")'
        elif kind == 'E':
            ins = f'#eh[{body}]'
        elif kind == 'C':
            ins = f'#n[{body}]'
        elif kind == 'A':
            ins = f'#n[#A[{body}]]'
        elif kind == 'P':
            ins = f'#n[#P[{body}]]'
        elif kind in ('CA', 'CP', 'CAP', 'AP', 'PA', 'CPA', 'PC', 'AC'):
            segs = [s.strip() for s in re.split(r'(?m)^\|\|\s*$', body)]
            wrap = {'C': '[{}]', 'A': '[#A[{}]]', 'P': '[#P[{}]]'}
            ins = '#n' + ''.join(wrap[k].format(s) for k, s in zip(kind, segs))
        else:
            problems.append(f'{name}: unknown kind {kind}')
            continue
        i = nth_index(text, rest, num)
        if i < 0:
            problems.append(f'{name}: {kind} anchor missing: {rest[:70]!r}')
            continue
        j = i + len(rest)
        text = text[:j] + ins + text[j:]
    return text


def dropcap(text):
    # raised initial on the first plain paragraph
    paras = text.split('\n\n')
    for k, p in enumerate(paras):
        if p and p[0].isalpha() and not p.startswith('#'):
            words = p.split(' ')
            lead = ' '.join(words[:3])
            if any(c in lead for c in '*_#['):
                lead = words[0]; words = [words[0], '', ''] + words[1:]
            rest = ' '.join(words[3:])
            paras[k] = f'#cap[{lead[0]}]#smallcaps[{lead[1:]}] {rest}'
            break
    return '\n\n'.join(paras)


def main():
    for raw in sorted(RAW.glob('[0-9][0-9].txt')):
        name = raw.stem
        text = convert(raw.read_text())
        nf = NOTES / f'{name}.txt'
        if nf.exists():
            text = apply(text, nf.read_text(), name)
        if '%%NOCAP' not in text:
            text = dropcap(text)
        text = text.replace('%%NOCAP', '')
        (OUT / f's{name}.typ').write_text('#import "../lib.typ": *\n\n' + text + '\n')
    for p in problems:
        print('!!', p)
    fmt = sys.argv[1] if len(sys.argv) > 1 else 'pdf'
    if fmt == 'none':
        return
    try:
        res, warns = typst.compile_with_warnings(str(ROOT / 'main.typ'), format='pdf')
    except typst.TypstError as e:
        print('TYPST ERROR:', e)
        for a in ('diagnostic', 'trace', 'hints', 'message'):
            if hasattr(e, a):
                print(' ', a, ':', str(getattr(e, a))[:1500])
        sys.exit(1)
    for w in warns[:12]:
        print('warn:', getattr(w, 'message', w))
    import subprocess
    sys.path.insert(0, str(ROOT / 'tools'))
    import ledger
    pdf = ROOT / 'out' / 'null-run-uncollected-editions-fourth-impression.pdf'
    pdf.parent.mkdir(exist_ok=True)
    for _ in range(3):   # the foot-of-page ledger must end on the last page
        pdf.write_bytes(res)
        n = int(re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo', str(pdf)], capture_output=True, text=True).stdout).group(1)) - 2
        want = n - 67
        cur = int(re.search(r'LSTART = (\d+)', (ROOT / 'ledger.typ').read_text()).group(1))
        curnp = re.search(r'NP = (\d+)', (ROOT / 'ledger.typ').read_text())
        if cur == want and curnp and int(curnp.group(1)) == n:
            break
        ledger.write(str(ROOT / 'ledger.typ'), want, n)
        res = typst.compile(str(ROOT / 'main.typ'), format='pdf')
    print('folios:', n)
    pdf.parent.mkdir(exist_ok=True)
    pdf.write_bytes(res)
    print('wrote', pdf, len(res) // 1024, 'KB')


if __name__ == '__main__':
    main()
