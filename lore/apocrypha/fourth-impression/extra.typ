#import "lib.typ": *
#import "build/papers.typ": cabinet, unplaced, openings

// ============================================================ the gazetteer (a foreign leaf)
#let gazetteer = leaf[
  #runtitle.update([From the Office Gazetteer])
  #[#metadata("gazetteer")<opener>]
  #set par(first-line-indent: 1em, justify: true)
  #v(0.15in)
  #align(center)[
    #text(size: 7pt, tracking: 1.5pt)[FROM THE OFFICE GAZETTEER, WHICH HOLDS ONE COUNTY]
    #v(3pt)
    #text(size: 15pt)[Hawksmoor]
    #v(2pt)
    #line(length: 18%, stroke: 0.5pt + ink)
  ]
  #v(5pt)
  #par(first-line-indent: 0pt)[#text(tracking: 0.6pt)[HAWKSMOOR.] A county of thirty-six sections, of which the Gazetteer describes one. Its seat is not given. Its population at the last enumeration is entered as _resident_, without a figure.]

  The county is bounded on the north by a section line, on the east by a section line, on the south by a section line, and on the west by low banks entered as wash. It contains no town.#eh[One.] Earlier editions listed a town under each of several names. These were struck when it was found that mail addressed to any of them was delivered at the same lodge.

  _Surface._ Dolomite ridges under thin red clay; lead ore in pockets; no drift.#th("drift") The Gazetteer follows the county survey in recording that the ice of four advances passed to the east and to the north and did not enter. It offers no reason. A reader who requires one is referred to the Geological Department, which refers the reader to the survey.

  _Survey._ The county was laid out from a single section, the sixteenth of Township 5 North, Range 8 West, whose four corners were monumented in October 1891 and whose traverse has not closed since.#th("close") As every other section in the county is run from the lines of the sixteenth, the error is carried into each of them. The county as platted is therefore larger than the ground it stands on, by an amount the Gazetteer has not been able to compute, since the computation requires a section that closes.

  _Works._ An ironworks, 1872, on the east side of the ridge. A pump of 1872, or of 1895. A survey office. A gate lodge at the end of the county road. The road is the only one entered. It ends at the lodge. The Gazetteer does not say where it begins.

  _Interior._ The county has an interior, reached by a stair behind the lodge. It is variously stated to lie under a lake, under ice, and under nothing.#th("interiors") The Gazetteer has printed all three statements in successive editions, and prints all three in the present one. An editor who proposed to print none was reminded that a gazetteer describes what is entered, and that all three are entered.

  _Other counties._ The Gazetteer holds none. Correspondents who write from other counties are entered under Hawksmoor, at the section from which their letter is answered. It has been objected that on this method every place from which anyone has written to the Office lies in Hawksmoor County, in Section 16. The objection has been acknowledged.#n[#A[THIRTY-SIX SECTIONS TO THE COUNTY. THIRTY-SIX MEASUREMENTS TO A ROOM OF 216 FEET. NO CONNEXION IS ENTERED.]]
]

// ============================================================ exhibits
#let exlabel(l, cap) = {
  set par(first-line-indent: 0pt, justify: false, leading: 0.45em)
  text(font: mono, size: 6pt, fill: pencil, tracking: 0.3pt)[#text(fill: oxblood)[EXHIBIT #l] --- #cap]
}
#let field(label, value, w: 100%) = block(width: w, stroke: 0.4pt + ink, inset: (x: 5pt, y: 4pt), above: 0pt, below: 0pt, {
  set par(first-line-indent: 0pt, justify: false, leading: 0.4em)
  text(font: mono, size: 4.8pt, fill: pencil, tracking: 0.5pt, upper(label))
  v(-3pt)
  block(height: 15pt, value)
})
#let hand(b) = text(font: "Junicode", style: "italic", size: 10pt, fill: slate.darken(30%), b)
#let form(body, fill: rgb("#efe7d3")) = block(width: 100%, fill: fill, stroke: 0.7pt + ink, inset: 9pt, {
  set par(first-line-indent: 0pt, justify: false, leading: 0.5em)
  set text(font: typew, size: 7pt)
  body
})

#let exhibits = [
  #pagebreak(to: "odd", weak: true)
  #runtitle.update([Exhibits])
  #[#metadata("exhibits")<opener>]
  #v(0.5in)
  #text(font: serif, size: 19pt)[Exhibits]
  #v(-2pt)
  #line(length: 100%, stroke: 0.6pt + ink)
  #v(8pt)
  #form[
    #grid(columns: (1fr, auto), [NULL RUN RECEIVING OFFICE \ STORES DEPARTMENT], align(right, text(size: 11pt)[FORM 9-B]))
    #v(2pt)
    RECEIPT FOR ARTICLE RETURNED
    #v(5pt)
    #grid(columns: (1fr, 1fr),
      field([Article], [Thrust bearing, tarnished; shimmed]), field([Part No.], [214-Q]),
      field([Returned on], [3 SEP 1953]), field([Under badge], [NR-311-#box(width: 0.62em, { place(text(fill: ink.lighten(35%))[M]); text(fill: ink)[R] })]),
      field([Name of bearer], hand[K. Marek]), field([Class of article], []))
    #v(5pt)
    #text(fill: slate.darken(10%))[FOR YOUR COMFORT. DISPOSITION: IN SERVICE --- AWAITING ASSESSMENT.]
  ]
  #v(2pt)
  #exlabel([A], [Form 9-B as returned through the bars at Counter 2. One box is filled.#th("badge")])
  #v(18pt)
  #form(fill: rgb("#e9e4d6"))[
    #grid(columns: (1fr, auto), [OUTER GATE LODGE \ PROPERTY BOOK --- BEARER'S COPY], align(right, text(size: 11pt, fill: oxblood)[53-G17]))
    #v(5pt)
    CLASS: EQUIPMENT
    #v(3pt)
    1. A first name. \
    2. The colour of a room. \
    3. What snow feels like.
    #v(3pt)
    #text(fill: oxblood, size: 9pt, tracking: 1pt)[NOT RETURNABLE]
    #v(4pt)
    #hand[The first is a name, not an object.]
  ]
  #v(2pt)
  #exlabel([B], [Receipt 53-G17, carbon. The pencil is the bearer's.#th("toll")])

  #pagebreak()
  #v(0.2in)
  #form[
    #align(center)[ESTABLISHMENT SCHEDULE 53/4 \ POSTS KEPT AS COUNTERWEIGHT]
    #v(4pt)
    #table(columns: (0.4in, 1fr, 1fr, 1.2in), stroke: 0.3pt + ink, inset: 4pt,
      [POST], [DUTIES], [ALLOWANCE], [FOLDER],
      ..range(1, 7).map(i => ([#i], [none], [none], [in the lower drawer])).flatten(),
      [7], [none], [none], [brought on request; held closed])
    #v(3pt)
    NOT TO BE STRUCK OFF. NOT TO BE FILLED.#th("post")
    #v(8pt)
    STAFF INDEX (EXTRACT)
    #v(2pt)
    #grid(columns: (auto, 1fr, auto), row-gutter: 5pt, column-gutter: 4pt,
      [HALE], box(width: 100%, stroke: (bottom: (paint: pencil, dash: "dotted", thickness: 0.4pt)))[#h(1pt)], [folder 1],
      [#h(2em)], [#h(1pt)#th("blank")], [],
      [HALLAM], box(width: 100%, stroke: (bottom: (paint: pencil, dash: "dotted", thickness: 0.4pt)))[#h(1pt)], [folder 2])
  ]
  #v(2pt)
  #exlabel([C], [The schedule, with the index page. The foot of the page is not reproduced.])
  #v(16pt)
  #{
    let card(name, col, tc, lock, opens) = block(width: 100%, height: 0.95in, fill: col, stroke: 0.6pt + ink, radius: 4pt, inset: 7pt, {
      set par(first-line-indent: 0pt, justify: false, leading: 0.45em)
      set text(font: mono, size: 5.6pt, fill: tc, tracking: 0.5pt)
      [CLEARANCE]
      v(-2pt)
      text(font: serif, size: 13pt, tracking: 0pt, name)
      v(1fr)
      [LOCK #lock \ #opens]
    })
    grid(columns: (1fr, 1fr, 1fr), column-gutter: 8pt,
      card([Ivory], rgb("#efe6cf"), ink, [191], [EAST SERVICE; UPPER PIPE DOORS]),
      card([Slate], rgb("#55626b"), rgb("#f1ece0"), [192], [VALVE HALL; PUMP SLUICE SWITCH]),
      card([Oxblood], oxblood, rgb("#f1ece0"), [193], [SEALED BASIN STAIR; UNDERCROFT VAULT]))
  }
  #v(2pt)
  #exlabel([D], [Clearance cards, three. No card is issued for the fourth floor.#th("stair")])
  #v(16pt)
  #block(width: 100%, height: 1.25in, stroke: (paint: pencil, dash: "dashed", thickness: 0.5pt))[]
  #v(2pt)
  #exlabel([E], [Form 44-B (Room Undelivered). No copy has been located in Stores.#th("door")])
]

// ============================================================ the petitions
#let petitions = [
  #pagebreak(to: "odd", weak: true)
  #runtitle.update([The Petitions])
  #[#metadata("petitions")<opener>]
  #v(0.5in)
  #text(font: serif, size: 19pt)[The Petitions of the Bearer of Receipt 53-G17]
  #v(-2pt)
  #line(length: 100%, stroke: 0.6pt + ink)
  #v(2pt)
  #dept[Null Run --- Counter 2 --- Petitions 23-C to 31-C, with replies]
  #{
    set par(first-line-indent: 0pt, justify: true, spacing: 0.5em)
    let pet(no, body, reply) = block(width: 100%, breakable: false, above: 0pt, below: 13pt, {
      text(font: mono, size: 6.4pt, fill: oxblood, tracking: 0.8pt)[PETITION #no]
      v(-2pt)
      text(style: "italic", size: 10pt, body)
      v(-1pt)
      pad(left: 14pt, text(font: typew, size: 6.8pt)[#text(fill: oxblood)[REPLY.] #reply])
    })
    pet([23-C], [I am the bearer of Receipt 53-G17. Three items were taken in at the gate under my number: a first name, the colour of a room, and what snow feels like. I have been given a volume to read while I wait. In its third record the same three items are entered against a Mr. Marsh. I ask which of us is the bearer.#th("toll")], [ACKNOWLEDGED. NUMBERED. DEFERRED.])
    pet([24-C], [I withdraw the word #x[same] in Petition 23-C. Mr. Marsh's name was his mother's; mine was my own. His room had a wallpaper, and I am not able to say that mine had. I ask that the two lines be compared by someone who can read mine.], [THE PROPERTY BOOK IS NOT LENT.])
    pet([25-C], [I ask how long I have been waiting. I do not ask it as a complaint; the chair is #x[comfortable] adequate. I ask because the volume refers to an appointment of 2 June 1936, and I should like to rule it out.#th("wait")], [THE APPOINTMENTS LEDGER IS NOT A REGISTER OF PERSONS WAITING. PERSONS WAITING ARE NOT REGISTERED.])
    pet([26-C], [I ask that the following be entered as a fact and not as a petition: that there is a window at the end of the gallery; that on some days it stands green to the sill; that on others its third row is iced; and that today it is a wall. I have not moved the chair.#th("interiors")], [ENTERED AS A PETITION.])
    pet([27-C], [In the tenth record a caller stands at the outer glass with their back to the road, on the nights the parcels came. I ask whether I came in by the gate. I ask because I do not remember luggage.#th("caller")], [THE GATE LOG ENTERS ONE CALLER. THE CALLER IS NOT ENTERED AS ADMITTED.])
    pet([28-C], [I find in the fourteenth record a third bearer of my three items, who writes that there is a folder with their handwriting on the cover and that they are leaving it closed. I have compared the handwriting, so far as print allows. I ask to be told that it is not mine. I will accept this at any counter.], [HANDWRITING IS NOT COMPARED AT THE COUNTER.])
    pet([29-C], [I ask for the first name only. The room and the snow may stand. I am asked for a name each time I petition, and I have signed each of these with my receipt number, which the form accepts. I should like to sign one of them.], [A NAME ENTERED AS EQUIPMENT IS NOT RETURNABLE. THE BEARER MAY APPLY TO HAVE IT ENTERED AS A NAME. THE APPLICATION IS MADE BY PETITION, SIGNED WITH THE NAME.])
    pet([30-C], [I have read the reply to 29-C four times. I make no petition under this number. I ask that the number be kept for me.], [KEPT.])
    pet([31-C], [I ask whether the seventeenth record is mine. I do not ask to see it.], [ACKNOWLEDGED. NUMBERED. DEFERRED.])
  }
  #text(size: 8.6pt, style: "italic", fill: pencil)[The volume was returned at Counter 2 on a date that was not stamped. The chair at the end of the intake gallery remains set aside.]
]

// ============================================================ the clerk check
#let clerkcheck = [
  #pagebreak(weak: true)
  #runtitle.update([Clerk Check])
  #[#metadata("check")<opener>]
  #v(0.5in)
  #dept[Null Run --- Clerk Check --- To be completed by any officer drawing this volume]
  #{
    set par(first-line-indent: 0pt, justify: false, leading: 0.5em)
    set text(font: typew, size: 7.3pt)
    let qs = (
      ([the closure error of the traverse of Section 16], [3.60 ch inward], [4.7 ch inward], [nil]),
      ([the depth of the dry stores tank], [10 ft 6 in], [38 yd], [9 ft 8 in]),
      ([the duration of Reel 1872-TT1], [48 s], [49 s], [48 s and one beat]),
      ([the number of floors of the hotel], [three], [four], [three, when checked in]),
      ([the badge of K. Marek, Joiner, Provisional], [311-M], [311-R], [the box is blank]),
      ([the number of leaves in this volume], [#LEAVES], [#(LEAVES + 1)], [both are in force]),
      ([what stands above the ceiling], [a lake], [ice], [rock]),
      ([the bearer of Receipt 53-G17], [J. Marsh], [a lexicographer], [the petitioner]),
      ([the letter that will not stay lit], [W], [R], [M]),
      ([the number of records], [sixteen], [seventeen], [one]),
      ([the weight of this volume], [41 lb 8 oz], [32 lb 0 oz], [it is not heavy]),
      ([the closing line], box(width: 0.6in, stroke: (bottom: 0.4pt + ink))[#h(1pt)], box(width: 0.6in, stroke: (bottom: 0.4pt + ink))[#h(1pt)], box(width: 0.6in, stroke: (bottom: 0.4pt + ink))[#h(1pt)]),
    )
    for (i, q) in qs.enumerate() {
      block(width: 100%, breakable: false, above: 0pt, below: 9.5pt, {
        [#text(fill: oxblood)[#(i + 1).] CITE #upper(q.at(0)):]
        v(-3pt)
        pad(left: 14pt, grid(columns: (1fr, 1fr, 1fr), [\[Z\] #q.at(1)], [\[X\] #q.at(2)], [\[C\] #q.at(3)]))
      })
    }
    v(2pt)
    line(length: 100%, stroke: 0.4pt + ink)
    v(-2pt)
    [KEY. FOR EACH QUESTION, EVERY OPTION IS ENTERED IN AT LEAST ONE RECORD. THE KEY IS #withheld. \
    ISSUED FROM STORES ON A CORRECT PAPER: 1872 VULCANISED FELT HEEL DAMPER (SLOT 12).]
  }
]

// ============================================================ the papers
#let papers = [
  #pagebreak(to: "odd", weak: true)
  #set page(margin: (inside: 0.62in, outside: 0.62in, top: 0.95in, bottom: 1.12in))
  #runtitle.update([The Papers Preferred])
  #[#metadata("papers")<opener>]
  #v(0.5in)
  #text(font: serif, size: 19pt)[The Papers Preferred]
  #v(-2pt)
  #line(length: 100%, stroke: 0.6pt + ink)
  #v(4pt)
  #{
    set par(first-line-indent: 0pt, justify: true)
    text(size: 8.8pt, style: "italic")[Where a record and its paper disagree, the paper is to be preferred. The compiler therefore prints the papers which a record or a note in this volume cites: twenty-six from the cabinets, and two of which only the opening lines are shown at the terminals. They are printed as filed, with the date, the signing office and the interior each one reports. A reader checking a record against them will find that the papers do not agree with one another either.#th("interiors")]
  }
  #v(8pt)
  #columns(2, gutter: 14pt, cabinet + openings)
]
