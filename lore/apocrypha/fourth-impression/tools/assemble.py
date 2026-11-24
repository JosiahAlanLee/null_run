#!/usr/bin/env python3
"""Write main.typ: the order of the volume."""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from records import RECORDS
ROOT = pathlib.Path(__file__).resolve().parent.parent
PL = {
 1: ('p01-leaf.svg', 'I', 'Foreign leaf, page nineteen. The verse breaks off at the rule; three columns of rubric follow. Sewn at the left with waxed yellow thread; deposit along the foot. (Ref. L1-33, L4-16.)'),
 2: ('p02-plat.svg', 'II', 'Section 16, with the five monuments and the traverse as run. Drift is stippled on every neighbouring section. (Ref. L4-18, L4-19, L4-20.)'),
 3: ('p03-hotel.svg', 'III', 'Lake elevation of the hotel: three floors as registered, a fourth as keyed. Below, the stair from ground to first, with the landings counted. (Ref. L1-37.)'),
 4: ('p04-tape.svg', 'IV', 'Cable tape as recovered from the repeater. The first act is on the tape.'),
 5: ('p05-stacks.svg', 'V', 'Aisle 409, bay 14. One volume has brought its shelf down by an inch and a quarter. The stain is in its neighbours.'),
 6: ('p06-neon.jpg', 'VI', 'The sign, from the lot, and what the wet blacktop returns of it.'),
 7: ('p07-tank.svg', 'VII', 'Tank 2 in section. Ten feet six inches by tape; thirty-eight yards by line. (Ref. L2-18, L1-41.)'),
 8: ('p08-tally.svg', 'VIII', 'Marking-plate tally of the Lower Forge. Two hundred and five pieces, and a space.'),
 9: ('p09-score.svg', 'IX', 'Reel 1872-TT1. Forward voice above; retrograde below, entering one count late. (Ref. L1-27, L2-20.)'),
 10: ('p10-caller.svg', 'X', 'The outer glass, 20 December. Below, the pilot lamp over the rear arch at seven readings. (Ref. L1-42.)'),
 11: ('p11-fieldbook.svg', 'XI', "Deputy Surveyor's field book, 19 February 1892, with the closure worked as squares. (Ref. L4-18.)"),
 12: ('p12-beam.svg', 'XII', 'The stores beam, with one leaf against two tares. Below, the sixteen weights laid end to end, and the remainder.'),
 13: ('p13-contact.jpg', 'XIII', 'Contact sheet, third-floor east corridor. Eleven frames, each six feet shorter than the last. The twelfth was not taken.'),
 14: ('p14-doors.svg', 'XIV', 'Sixteen doors, to one scale. One elevation is omitted.'),
 15: ('p15-chladni.png', 'XV', 'Sand figures on the plate. In the eighth the sand has gathered where the figure has no line. (Ref. L1-26.)'),
 16: ('p16-borings.svg', 'XVI', 'Borings west of the works, with two from neighbouring sections for comparison. (Ref. L4-20.)'),
}
PARTS = {
 1: ('I', 'The Unchaperoned Masque', 'Archival deposition, choir-school notebooks, and the unguarded hollow.'),
 2: ('II', 'Inside Out', 'Psychogeographic plats, adult thresholds, apocryphal committees, sleeping stacks, and roadside pantheons.'),
 7: ('III', 'The Receiving Office', 'Five records from inside the Office: contradictory interiors, deferred petitions, and steady lamps.'),
 12: ('IV', 'Between the Registers', 'Five records in which another library and the Receiving Office come through the same paper.'),
}
BEFORE = {7: '#soundings'}
AFTER = {1: '#review', 2: '#gazetteer', 4: '#catalogue', 5: '#property', 11: '#circular'}

o = ['#import "lib.typ": *', '#import "inter.typ": *', '#import "extra.typ": *', '#show: book', '', '#include "front.typ"', '']
for i, (num, loc, title, short, w, d) in enumerate(RECORDS, 1):
    if i in PARTS:
        n, t, s = PARTS[i]
        o.append(f'#part("{n}", [{t}], [{s}])')
    if i in BEFORE:
        o.append(BEFORE[i])
    f, rn, cap = PL[i]
    o.append(f'#plate("art/{f}", "{rn}", [{cap}])')
    sh = f', short: [{short}]' if short else ''
    loc = loc.replace('//', '\\\\/\\\\/')
    o.append(f'#record("{num}", "{loc}", [{title}], weight: [{w}], recd: [{d}]{sh})')
    if i == 14:
        o.append('#[\n#set par(hanging-indent: 1.1em, first-line-indent: 0pt, spacing: 0.85em)\n#include "build/s14.typ"\n]')
    else:
        o.append(f'#include "build/s{i:02d}.typ"')
    if i in AFTER:
        o.append(AFTER[i])
    o.append('')
o.append('#plate("art/p17-withheld.svg", "XVII", [The seventeenth record, from above.])')
o.append('#record("S-17", "HELD \\\\/\\\\/ CLOSED", [#box(width: 2.7in, height: 14pt, stroke: (bottom: 0.6pt + ink))[#h(1pt)]], weight: [9 lb 8 oz], recd: [NOT ENTERED], short: [The Seventeenth Record])')
o.append('#include "s17.typ"')
o.append('')
o.append('#exhibits')
o.append('#petitions')
o.append('#papers')
o.append('#include "back.typ"')

(ROOT / 'main.typ').write_text('\n'.join(o) + '\n')
print('main.typ written')
