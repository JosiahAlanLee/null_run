#!/usr/bin/env python3
"""The foot of the last sixty-eight pages: Entry 214 of the Appointments
Ledger, carried forward once per quarter-day from Midsummer 1936."""
Q = ['LADY DAY', 'MIDSUMMER', 'MICHAELMAS', 'CHRISTMAS']
REMARK = {
    1: 'CALLER SHOWN TO THE CHAIR AT THE END OF THE INTAKE GALLERY.',
    5: 'CHAIR NOT TO BE MOVED.',
    12: 'CALLER NOT SEEN. CHAIR SET ASIDE.',
    17: 'LEDGER REBOUND. BINDER CERTIFIES 107 LEAVES.',
    24: 'NEW NIGHT ATTENDANT, START DATE 14 APRIL 1942.',
    25: 'ENTERED IN A SECOND HAND.',
    31: 'INITIALS NOT LEGIBLE.',
    38: 'DEPOSIT AT THE FOOT OF THE PAGE. NOT BRUSHED OUT.',
    45: 'CHAIR FOUND FACING THE WALL. NOT MOVED.',
    52: 'NO APPOINTMENT OF THIS NUMBER IS HELD BY THE APPOINTMENTS OFFICE.',
    59: 'CARRIED FORWARD WITHOUT BEING READ.',
    64: 'PILOT LAMP OVER THE REAR ARCH: AMBER.',
    66: 'ESTABLISHMENT DATED FROM 1953. ENTRY PRE-DATES THE ESTABLISHMENT. CARRIED.',
    67: 'AUDIT: 106 LEAVES. THIS PAGE STANDS ON NO LEAF.',
    68: 'CARRIED FORWARD TO PAGE 213.',
}
INIT = [(1, 'H.K.'), (25, 'R.O.'), (53, '--')]


def lines():
    out = []
    y, q = 1936, 1
    for i in range(1, 69):
        ini = [b for a, b in INIT if i >= a][-1]
        r = REMARK.get(i, '')
        out.append(f'APPOINTMENTS LEDGER, P. 214 --- ENTRY 214: CALLER PRESENTED 2 JUNE 1936; ASKED TO WAIT --- CARRIED FORWARD {Q[q]} {y} ({i} OF 68) --- INIT. {ini}' + (f' --- {r}' if r else ''))
        q += 1
        if q == 4 + 0 and False:
            pass
        if q > 3:
            q = 0; y += 1
    return out


def write(path, lstart):
    body = ',\n'.join('  [' + l.replace('#', '\\#') + ']' for l in lines())
    open(path, 'w').write(f'#let LSTART = {lstart}\n#let ledger = (\n{body},\n)\n')


if __name__ == '__main__':
    import sys
    write(sys.argv[1], int(sys.argv[2]))
    print(lines()[0]); print(lines()[-1])
