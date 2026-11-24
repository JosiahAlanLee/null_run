#!/usr/bin/env python3
"""src/rawNN.txt (machine extraction of the first impression) -> raw/NN.txt.
Structural repairs only: block kinds, lists, tables that the extraction garbled.
Wording changes live in notes/NN.txt as @S entries, where they can be seen."""
import re, pathlib
R = pathlib.Path(__file__).resolve().parent.parent
def load(i): return (R / 'src' / f'raw{i:02d}.txt').read_text()
def save(i, t): (R / 'raw' / f'{i:02d}.txt').write_text(t)
def sub1(t, a, b, n=1):
    assert t.count(a) >= 1, a[:50]
    return t.replace(a, b, n)
def para(t, start):
    """return the whole paragraph beginning with `start`"""
    i = t.index(start); j = t.find('\n\n', i)
    return t[i:j if j > 0 else len(t)]
def tag(t, start, k):
    p = para(t, start)
    return t.replace(p, f'%%NARROW {k} ' + p, 1)
def block_before(t, start, name):
    i = t.index(start)
    return t[:i] + f'%%BLOCK {name}\n\n' + t[i:]
def dept(t):
    return re.sub(r'\nN_ull Run — (.*?)_\n', lambda m: '\n#dept[Null Run --- ' + m.group(1).replace('&', '\\&') + ']\n', t, count=1)

for i in range(1, 17):
    t = load(i)
    if i == 1:
        p = para(t, 'D*ocument Ref.:*')
        t = t.replace(p, '#doc[*Document Ref.:* Diocesan Archive, Box 14-C (Restricted --- Parish of St. Jude-in-the-Bluffs, Sauk County, WI) \\\n*Filed by:* Arthur Halvorsen, Parish Archivist \\\n*Date of Deposition:* November 19, 2026 \\\n*Attachments:* Two excised leaves from a choir-school notebook (October 2004); photocopy of title page, _Prolegomena to the Second Masque_ (London, 1898); two unbound rag-paper leaves removed from Hymnal \\#114.]')
        t = block_before(t, '> _PROLEGOMENA', 'rubric')
        t = block_before(t, '> *Coulee above', 'notebook')
        t = block_before(t, '> *ACT II, SCENE iii*', 'rubric')
        t = block_before(t, '> _THE STEWARD:', 'rubric')
        t = t.replace('\n> \\>\n', '\n')  # five empty markers left by the first impression
        t = re.sub(r'(?m)^\\>\n\n', '', t)
    if i == 4:
        p = para(t, 'M*INISTRY OF CANONICAL')
        t = t.replace(p, '#doc[*MINISTRY OF CANONICAL BORDERS --- WHITEHALL (SUB-BASEMENT IV)* \\\n*File Ref.:* 1899-Y / "The Transatlantic Piracy" \\\n*Compiled by:* Edmund Crabb, Assistant Keeper of Printed Books (Seconded) \\\n*Classification:* Apocrypha --- Do Not Index in General Catalogue]')
        t = block_before(t, '> *FROM: NEW YORK', 'wire')
        t = t.replace('> *FROM: NEW YORK STATION (CABLE)*', '> FROM: NEW YORK STATION (CABLE)').replace('> *TO: CANONICAL OFFICE, LONDON*', '> TO: CANONICAL OFFICE, LONDON')
        t = re.sub(r'> \*(ROOK SYNDICATE.*?)\*\n', r'> \1\n', t)
        t = block_before(t, '> *CRABB, EDMUND.*', 'entry')
        t = re.sub(r' (\d)\. \*', r'\n\n\1. *', t)
    if i == 7:
        t = dept(t)
        t = block_before(t, '> _Dry stores tank', 'notebook')
        t = block_before(t, '> _Correction factor', 'doc')
        t = block_before(t, '> _J.T. —', 'notebook')
        t = re.sub(r'(?m)^> _(.*)_$', r'> \1', t)
    if i == 8:
        t = dept(t); t = block_before(t, '> #m[DISPOSITION', 'doc')
        t = t.replace('> #m[DISPOSITION: IN SERVICE — AWAITING ASSESSMENT.]', '> DISPOSITION: IN SERVICE --- AWAITING ASSESSMENT.')
    if i == 9:
        t = dept(t)
    if i == 10:
        t = dept(t)
        t = block_before(t, '> _22:00', 'doc'); t = block_before(t, '> _02:00', 'doc')
        t = re.sub(r'(?m)^> _(.*)_$', r'> \1', t)
        t = t.replace('2. The colour of a room. 3. What snow feels like.', '2. The colour of a room.\n\n3. What snow feels like.')
    if i == 11:
        t = dept(t)
        t = block_before(t, '> _Mon. 4 to Mon. 1', 'notebook')
        t = re.sub(r'(?m)^> _(.*)_$', r'> \1', t)
        for k, s in enumerate(['No fixture in Gallery 9 went dark', 'Krell did not swear.', '"Two hundred and ten feet,"', 'Doyle checked the folded blueprint', '"Enter six feet as found,"'], 1):
            t = tag(t, s, k)
    if i == 6:
        for k, s in enumerate(['The buzzing died.', 'I slammed the plywood door'], 1):
            t = tag(t, s, k)
    if i == 12:
        a = t.index('#m[NOTE 114 (EDITORIAL'); b = t.index('I set it down so hard')
        t = t[:a] + '%%NOTE114\n\n' + t[b:]
    if i == 13:
        for k, s in enumerate(['"You\'re six feet early,"', '"There\'s a lake behind that glass,"', '"So the northern wing claims,"', 'I lifted my Hasselblad', '"I wouldn\'t take that frame,"'], 1):
            t = tag(t, s, k)
    if i == 14:
        def hw(m):
            return '#hw[' + m.group(1).replace('*', '').title().replace(' An ', ' an ') + ']'
        t = re.sub(r'(?m)^(\*[A-Z][^a-z]*?\.\*)', hw, t)
        a = t.index('\\*_\\[ENTRY OMITTED')
        tail = t[a:]
        note = tail[tail.index('_I began this dictionary'):].strip()
        note = note.replace('_Equipment — Not Returnable\\*. The seventh', '_Equipment — Not Returnable_. _The seventh').replace('\\*', '')
        t = t[:a] + '%%LEXNOTE ' + note + '\n'
        t = t.replace('\n\n#hw[IRON PIN', '\n\n%%GAP\n\n#hw[IRON PIN')
        t = re.sub(r'\nS_elected entries(.*?)_\n', lambda m: '\n#dept[Selected entries' + m.group(1) + ']\n', t, count=1, flags=re.S)
    if i == 15:
        a = t.index('#m[FORWARD VOICE'); b = t.index('The chapel was empty and cold.')
        t = t[:a] + '%%CANON\n\n' + t[b:]
    if i == 16:
        a = t.index('#m[1872 — IRONWORKS LOG]'); b = t.find('\n\n', a)
        t = t[:a] + '%%STRATA' + t[b:]
    save(i, t)
print('raw fixed')
