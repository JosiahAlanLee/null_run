#import "lib.typ": *

// ------------------------------------------------------------ boards
#page(margin: 0pt, fill: board, header: none, footer: none, background: image("art/cover.jpg", width: 100%, height: 100%))[
  #set par(justify: false, first-line-indent: 0pt, leading: 0.5em)
  #pad(x: 0.55in, top: 0.6in)[
    #text(font: mono, size: 7pt, fill: rgb("#c9a45c"), tracking: 2.4pt)[NULL RUN #h(0.5em) RECEIVING OFFICE #h(0.5em) RECORDS]
    #v(0.16in)
    #text(font: serif, size: 33pt, fill: rgb("#efe7d5"), tracking: 0.4pt)[The \ Uncollected \ Editions]
    #v(0.08in)
    #line(length: 1.1in, stroke: 0.6pt + rgb("#c9a45c"))
    #v(0.04in)
    #text(font: serif, style: "italic", size: 11pt, fill: rgb("#cfc6b4"))[Sixteen records, with the apparatus \ of four hands]
  ]
  #place(bottom + left, dx: 0.55in, dy: -0.5in, text(font: mono, size: 6.2pt, fill: rgb("#b5aca0"), tracking: 1pt)[
    FOURTH IMPRESSION, COLLATED \
    SEC. 16, T5N R8W #h(1em) SURVEY CLOSURE: 3.60 CH INWARD \
    DISPOSITION: AWAITING ASSESSMENT])
]
#page(margin: 0pt, fill: board, header: none, footer: none)[
  #place(bottom + left, dx: 0.7in, dy: -0.7in, text(font: typew, size: 6.6pt, fill: rgb("#6d6252"))[RECEIVED OUTER GATE LODGE \ 14 -- 20 DEC 1953 \ SIXTEEN PARCELS. ONE CALLER. NO LUGGAGE.])
]
#counter(page).update(1)

// ------------------------------------------------------------ half-title
#page(header: none, footer: none)[
  #v(2.2in)
  #align(center)[
    #text(font: scfont, size: 13pt, tracking: 2.5pt)[The Uncollected Editions]
    #v(0.5in)
    #image("art/pin.svg", width: 0.7in)
  ]
]

// ------------------------------------------------------------ binder's certificate
#page(header: none, footer: none)[
  #v(0.9in)
  #doc[
    #align(center)[RECORDS OFFICE \ BINDER'S CERTIFICATE AND WEIGHT RETURN 53/6-b]
    #v(6pt)
    I certify that the volume lettered THE UNCOLLECTED EDITIONS has been sewn on five tapes and cased, and that it contains #(LEAVES + 1) leaves, being #(NP + 2) pages.#th("count")
    #v(4pt)
    Weight as bound, on the stores beam scale, checked against two one-pound brass tares: 41 lb 8 oz.#th("weight")
    #v(4pt)
    Class: four pounds and under.
    #v(4pt)
    Thread: #box(width: 1.1in, stroke: (bottom: 0.4pt + ink))[#h(1pt)]
    #v(4pt)
    Signed: #box(width: 1.1in, stroke: (bottom: 0.4pt + ink))[#h(1pt)] #h(1fr) Binder to the Office
  ]
  #v(4pt)
  #doc[
    #amend[LEAVES COUNTED ON THE TROLLEY: #LEAVES. PAGES: #NP. PAGES #(NP + 1) AND #(NP + 2) STAND ON NO LEAF. CERTIFICATE #ns. WEIGHT SUSTAINED. THREAD NOT STATED. SIGNATURE NOT SUPPLIED.]
  ]
  #v(1fr)
  #set par(justify: false, first-line-indent: 0pt)
  #text(size: 8.6pt, style: "italic", fill: pencil)[The compiler is required to print the certificate as received and the amendment as made. Both are in force.]
]

// ------------------------------------------------------------ title
#page(header: none, footer: none)[
  #set par(justify: false, first-line-indent: 0pt, leading: 0.55em)
  #v(0.9in)
  #align(center)[
    #text(font: mono, size: 7pt, fill: oxblood, tracking: 3pt)[NULL RUN]
    #v(0.2in)
    #text(font: serif, size: 27pt)[The Uncollected \ Editions]
    #v(0.18in)
    #line(length: 24%, stroke: 0.6pt + ink)
    #v(0.14in)
    #block(width: 86%, text(size: 10.5pt, style: "italic")[Sixteen records received at the Outer Gate Lodge, with the notes of the compiler, the corrections of the Audit, the objections of an earlier hand, and certain petitions])
    #v(1fr)
    #text(font: scfont, size: 9pt, tracking: 1.6pt)[Fourth Impression, Collated]
    #v(0.1in)
    #text(font: mono, size: 6.4pt, fill: pencil, tracking: 1pt)[NULL RUN RECEIVING OFFICE #sym.dot.c RECORDS OFFICE \ SECTION 16, TOWNSHIP 5 NORTH, RANGE 8 WEST]
    #v(0.3in)
  ]
]

// ------------------------------------------------------------ the impressions
#page(header: none, footer: none)[
  #set par(justify: false, first-line-indent: 0pt, spacing: 0.9em)
  #set text(size: 8.8pt)
  #v(1.6in)
  #text(font: scfont, tracking: 1pt)[The impressions]

  _First impression._ Sixty-four pages; sixteen records; seven plates; an index of two pages.

  _Second impression._ Two hundred and twelve pages. The four hands, the sewn leaves, the plates and sixty-six papers were added. The records were left as found.

  _Third impression._ One hundred and forty pages, collated elsewhere from the second and from a reading proof the Office has not seen. It cut what the early narrators explained and supplied what was done with dividers, wire and tares.

  _Fourth impression._ The present volume. The text of the sixteen records is the third's. The page, the plates, the notes and the schedules are the second's. Notes that referred to passages no longer in the records have been withdrawn with them. The papers at the end are reduced to those which a record or a note cites. Three names remain struck.

  The plates were drawn by procedure and not by hand. Each is drawn from a number, and the same number draws the same plate.

  No part of this volume has been read aloud.

  The Office does not hold a copy of the first impression.
  #v(1fr)
  #text(font: mono, size: 6pt, fill: pencil, tracking: 0.6pt)[DISPOSITION: AWAITING ASSESSMENT]
]

// ------------------------------------------------------------ note on the second impression
#runtitle.update([Note on the Fourth Impression])
#[#metadata("front")<opener>]
#v(0.5in)
#text(font: mono, size: 7pt, fill: oxblood, tracking: 1pt)[RECORDS OFFICE]
#v(2pt)
#text(font: serif, size: 19pt)[Note on the Fourth Impression]
#v(-2pt)
#line(length: 100%, stroke: 0.6pt + ink)
#v(10pt)

#cap[T]#smallcaps[he sixteen records] in this volume were received at the Outer Gate Lodge between the fourteenth and the twentieth of December 1953, in sixteen parcels, each in the class of four pounds and under. The gate log for those nights enters one caller, who carried no luggage.#th("caller") The parcels are entered as received.

A first impression was made, of sixty-four pages. It printed the records in the order of their receipt, with seven plates and an index, and it printed certain words in green and certain others in ochre wherever they occurred. The compiler has discontinued the practice. The colour was found to transfer to the facing page, and after some weeks a reader could no longer say on which page a word had first been coloured.

The present impression adds what the first left out, which is everything that was written on the records after they arrived. The text of the records themselves is taken from a later collation, which removed from the first six what their narrators explained and put in its place what their narrators did. The compiler has compared the two texts and prefers the shorter.

There are four hands. The compiler's notes stand at the foot of the page and say what can be checked: a date against a date, a weight against a scale, a name against an index. The Audit has gone through the compiler's notes, and through the records where it saw fit, and has entered its corrections under them in typescript. It is the practice of the Audit that a correction is carried through. The compiler observes, without complaint, that each correction carried through this volume has left a figure somewhere else that no longer agrees.

The third hand is older than either. It is in pencil, in the outer margin, and it has been on some of these leaves longer than the leaves have been in the Office. The compiler has traced two of its notes to paper of 1872 and cannot say how they come to stand on a deposition dated 2026. It writes as a tenant writes of a later tenant.

The fourth hand is a petitioner's: the bearer of Receipt 53-G17, who was given the volume to read while waiting and has returned it with petitions. They are printed where they were written. Each has been acknowledged, numbered and deferred.

The compiler has resolved nothing. Where two records disagree both are printed, and a small arrow with a page number stands after the word, thus.#th("count") The arrow gives the next page on which the same matter is entered. A reader who follows any arrow will be brought in time to the page from which they set out, since the last entry of each matter points to the first. There are three exceptions, listed in the Register at the end of the volume, in which the last arrow gives a page the volume does not have.

_The dates._ The records carry dates from 1849 to 2026. Their wrappers carry the Lodge stamp of December 1953.#th("date") The compiler has been asked how a deposition dated 2026 came to be received in 1953, and has replied that it came in a parcel.

_The county._ Several records name towns, a river and a highway in a county that is not in the Office gazetteer, which holds one county. The names are printed as found. The compiler would observe only that the section, the township and the range do not change from record to record, whatever the county is called, and that a letter addressed to either would be delivered at the Lodge.

_The count._ There are sixteen records. The contents give seventeen, the seventeenth being entered by its weight. The binder certifies #(LEAVES + 1) leaves and the trolley count is #LEAVES. The sixteen weights printed at the heads of the records come to thirty-two pounds; the volume as bound is returned at forty-one pounds eight ounces.#th("weight") The compiler does not explain these figures and is not required to.

One view of the records must be entered here, because it has been put to the compiler more than once: that they are not sixteen records but one, set down sixteen times by persons who were not all present. On this view three people, a paper, a stone that answers late, a count that runs one over, something given up at a threshold and a closing line that is not said are to be found in every record, and the names, the years and the county are the part that varies. A concordance on these lines is printed at the end of the volume. The compiler drew it up as instructed and does not hold the view. The Audit has not sustained it. The earlier hand has written one word in its margin, which is printed there.

Nothing in this volume is to be brushed out.#th("dust")

#v(10pt)
#align(right, text(font: mono, size: 6.4pt, fill: pencil, tracking: 0.8pt)[RECORDS OFFICE \ SECTION 16, T5N R8W \ AWAITING ASSESSMENT])

// ------------------------------------------------------------ table of hands
#pagebreak()
#runtitle.update([The Hands])
#[#metadata("hands")<opener>]
#v(0.5in)
#text(font: serif, size: 19pt)[The Hands, and How to Follow Them]
#v(-2pt)
#line(length: 100%, stroke: 0.6pt + ink)
#v(8pt)
#{
  set par(first-line-indent: 0pt, justify: false, spacing: 1em)
  let row(name, where, sample) = (
    [#text(font: scfont, tracking: 0.6pt, name) \ #text(size: 7.6pt, style: "italic", fill: pencil, where)], sample)
  grid(columns: (1.15in, 1fr), row-gutter: 13pt, column-gutter: 8pt,
    ..row([The Compiler], [foot of the page], text(font: serif8, size: 8.2pt)[The shelf mark given is 14-C. The compiler has not been able to draw Box 14-C.]),
    ..row([The Audit], [under the compiler, in typescript], [#A[14 + 22 = 36. THE SUM CLOSES.] \ #text(font: typew, size: 6.7pt)[#amend[A FIGURE #ns] #h(4pt) #struck #h(4pt) #withheld]]),
    ..row([The Earlier Hand], [outer margin, in pencil], text(size: 7.6pt, style: "italic", font: old, fill: pencil)[Not wash.]),
    ..row([The Petitioner], [foot of the page; strikes their own words], text(font: serif8, size: 8.2pt)[#P[I do not ask for the items #x[back] at this stage.]]),
    ..row([Arrows], [after a word], [
      #text(size: 8.6pt)[The next page on which the matter is entered. \
      #text(fill: ochre)[#sym.square.filled.tiny] paper, thread and deposit #h(1fr) #text(fill: lake)[#sym.square.filled.tiny] measure and place \
      #text(fill: oxblood)[#sym.square.filled.tiny] count, weight and date #h(1fr) #text(fill: slate)[#sym.square.filled.tiny] persons and lamps]]),
    ..row([Foreign Leaves], [between records], text(size: 8.6pt)[On older paper, sewn in with yellow thread. They are not to be cut out, copied or read aloud. Listed on Schedule F.]),
    ..row([The Foot of the Page], [the last sixty-eight pages], text(size: 8.6pt)[Entry 214 of the Appointments Ledger, carried forward once on each page.]),
  )
}

// ------------------------------------------------------------ contents
#pagebreak()
#runtitle.update([Contents and Catalogue])
#[#metadata("contents")<opener>]
#v(0.5in)
#text(font: serif, size: 19pt)[Contents and Catalogue]
#v(-2pt)
#line(length: 100%, stroke: 0.6pt + ink)
#v(6pt)
#{
  set par(first-line-indent: 0pt, justify: false, leading: 0.45em)
  set text(size: 8.6pt)
  let pg(key) = context {
    let o = query(<opener>).filter(m => m.value == key)
    if o.len() > 0 { link(o.first().location())[#counter(page).at(o.first().location()).first()] } else [--]
  }
  let rec(key, title, wt) = (text(font: mono, size: 6.4pt, fill: oxblood, key), title, text(font: typew, size: 6.6pt, fill: pencil, wt), align(right, pg(key)))
  let leafrow(key, title) = ([], text(style: "italic", fill: pencil, title), [], align(right, text(fill: pencil, pg(key))))
  let parthead(t) = grid.cell(colspan: 4, inset: (top: 7pt, bottom: 1pt), text(font: mono, size: 6.2pt, tracking: 1.4pt, fill: pencil, t))
  grid(columns: (0.36in, 1fr, 0.62in, 0.26in), row-gutter: 5.2pt, column-gutter: 5pt,
    ..leafrow("front", [Note on the Fourth Impression]),
    ..leafrow("hands", [The Hands, and How to Follow Them]),
    ..leafrow("stemma", [Descent of the Text]),
    ..leafrow("errata", [Errata]),
    parthead[PART I --- THE UNCHAPERONED MASQUE],
    ..rec("S-01", [The Unchaperoned Masque], [3 lb 12 oz]),
    ..leafrow("review", [_sewn in:_ A Book Not Yet Returned]),
    parthead[PART II --- INSIDE OUT],
    ..rec("S-02", [The Four-Dimensional Plat of Hawksmoor County], [2 lb 9 oz]),
    ..leafrow("gazetteer", [_sewn in:_ From the Office Gazetteer]),
    ..rec("S-03", [The Mineral Springs at Intermission], [2 lb 6 oz]),
    ..rec("S-04", [The Society of Uncollected Editions], [2 lb 4 oz]),
    ..leafrow("catalogue", [_sewn in:_ Catalogue of Apocryphal Persons]),
    ..rec("S-05", [The Clerk of Unwritten Drafts], [2 lb 11 oz]),
    ..leafrow("property", [_extract:_ The Property Book]),
    ..rec("S-06", [Roadside Pantheon (Exit 47)], [2 lb 8 oz]),
    parthead[PART III --- THE RECEIVING OFFICE],
    ..leafrow("soundings", [_sewn in:_ Three Soundings of One Stair]),
    ..rec("S-07", [The Calibration of Sounding Line 14], [1 lb 12 oz]),
    ..rec("S-08", [Part 214-Q, Returned Under Another Hand], [1 lb 13 oz]),
    ..rec("S-09", [Seven Beats in a Six-Beat Bar], [1 lb 9 oz]),
    ..rec("S-10", [The Seventh Post, Held Closed], [1 lb 9 oz]),
    ..rec("S-11", [Traverse Error: 3.60 Chains Inward], [1 lb 12 oz]),
    ..leafrow("circular", [_circular:_ The Measurement of Rooms]),
    parthead[PART IV --- BETWEEN THE REGISTERS],
    ..rec("S-12", [The Footnote That Outweighed the Folio], [3 lb 15 oz]),
    ..rec("S-13", [The Unfinished Room at the End of the Corridor], [13 oz]),
    ..rec("S-14", [A Small Dictionary of Unclaimed Doors], [14 oz]),
    ..rec("S-15", [The Twelve-Pipe Fugue in Retrograde], [15 oz]),
    ..rec("S-16", [The Man Who Kept the Ledger for the Glaciers], [14 oz]),
    grid.cell(colspan: 4, inset: (top: 3pt), line(length: 100%, stroke: 0.3pt + pencil)),
    [], text(style: "italic")[Sixteen records], text(font: typew, size: 6.6pt)[32 lb 0 oz], [],
    text(font: mono, size: 6.4pt, fill: oxblood)[S-17], [#box(width: 1.5in, stroke: (bottom: 0.4pt + ink))[#h(1pt)] #text(style: "italic", fill: pencil)[held closed]], text(font: typew, size: 6.6pt, fill: oxblood)[9 lb 8 oz], align(right, text(fill: oxblood)[#(NP + 1)]),
    [], text(style: "italic")[As bound], text(font: typew, size: 6.6pt)[41 lb 8 oz], [],
    parthead[AT THE END],
    ..leafrow("exhibits", [Exhibits]),
    ..leafrow("petitions", [The Petitions of the Bearer of Receipt 53-G17]),
    ..leafrow("papers", [The Papers Preferred]),
    ..leafrow("concordance", [Concordance of the One Account]),
    ..leafrow("schedf", [Schedule F: Foreign Leaves]),
    ..leafrow("register", [Register of Discrepancies]),
    ..leafrow("plates", [The Plates, and Their Numbers]),
    ..leafrow("check", [Clerk Check]),
  )
}

// ------------------------------------------------------------ stemma
#pagebreak()
#runtitle.update([Descent of the Text])
#[#metadata("stemma")<opener>]
#v(0.5in)
#text(font: serif, size: 19pt)[Descent of the Text]
#v(-2pt)
#line(length: 100%, stroke: 0.6pt + ink)
#v(6pt)
#move(dx: -0.12in, image("art/stemma.svg", width: TW + 0.9in))
#v(-4pt)
#{
  set par(first-line-indent: 0pt, justify: true)
  set text(size: 8.4pt)
  [The compiler was instructed to show from what each record was copied. Records 1 and 3 to 6 descend from a pamphlet; records 2 and 7 to 16 from the paper of a county, an ironworks and an office. Both lines are drawn from one evening, which has no date and for which no witness is entered.#n[#A[A SOURCE WITH NO WITNESS IS ENTERED AS "THIS ENTRY HAS NO SECOND WITNESS". IT IS NOT ENTERED AS A CIRCLE WITH A LETTER IN IT.]] The seventeenth record has no exemplar. The broken line at the left was added in a later ink: it makes the present volume the source of the pamphlet from which it descends. The compiler has left it in.]
}

// ------------------------------------------------------------ errata
#pagebreak()
#runtitle.update([Errata])
#[#metadata("errata")<opener>]
#v(1.1in)
#rotate(-1.6deg, block(width: 100%, fill: rgb("#efe6d0"), stroke: 0.4pt + pencil, inset: 14pt, {
  set par(first-line-indent: 0pt, justify: false, spacing: 0.8em, leading: 0.55em)
  set text(font: old, size: 8.6pt)
  align(center, text(tracking: 3pt, size: 9.5pt)[ERRATA])
  v(2pt)
  [The reader is asked to make the following corrections.]
  [_Certificate._ For #(LEAVES + 1) leaves read #LEAVES. For #LEAVES read #(LEAVES + 1).]
  [_Second record._ For 4.7 chains read 3.60. For Township 7 North read 5 North. For December read October. For Pinchot read Paige; for Vane read Lowe. For Paige read Pinchot.]
  [_Seventh record._ For 1,200 metres read 800. For 800 read 1,620. For 1,620 read 110.52.]
  [_Ninth record._ For forty-eight seconds read forty-nine. For seconds read beats.]
  [_Tenth record._ For 1953 read 1942. For 1942 read 1936.]
  [_Fifteenth record._ For "not yet due" read "not said".]
  [_Throughout._ For sixteen read seventeen.]
  [_This slip._ For "corrections" read "discrepancies". No discrepancy is corrected by this slip.]
}))
