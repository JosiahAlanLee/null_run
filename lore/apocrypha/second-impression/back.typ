#import "lib.typ": *
#import "extra.typ": clerkcheck

// ============================================================ Concordance of the One Account
#pagebreak(to: "odd", weak: true)
#runtitle.update([Concordance of the One Account])
#[#metadata("concordance")<opener>]
#v(0.5in)
#text(font: serif, size: 19pt)[Concordance of the One Account]
#v(-2pt)
#line(length: 100%, stroke: 0.6pt + ink)
#v(4pt)
#{
  set par(first-line-indent: 0pt, justify: true)
  text(size: 8.6pt, style: "italic")[Drawn up as instructed. Six things said to be found in every record, entered against each.#eh[Seventeen.] The compiler does not hold the view. #text(style: "normal", font: typew, size: 6.6pt)[#amend[ONE ACCOUNT #ns]]]
}
#v(4pt)
#{
  set par(first-line-indent: 0pt, justify: false, leading: 0.4em, spacing: 0.3em)
  set text(size: 7.1pt)
  let k(b) = text(font: scfont, size: 6.6pt, fill: pencil, tracking: 0.3pt, b)
  let card(num, three, paper, stone, over, given, unsaid) = block(width: 100%, breakable: false, below: 9pt, above: 0pt, {
    text(font: mono, size: 6.2pt, fill: oxblood, tracking: 0.6pt, num)
    v(-3pt); line(length: 100%, stroke: 0.3pt + pencil); v(-3pt)
    grid(columns: (0.44in, 1fr), row-gutter: 2.6pt,
      k[three], three, k[a paper], paper, k[a stone], stone, k[one over], over, k[given up], given, k[not said], unsaid)
  })
  move(dx: -0.05in, block(width: TW + 0.95in, columns(2, gutter: 12pt, {
    card([S-01], [Arthur, Martin, Clare], [a pamphlet of 1898; Hymnal 114], [a coulee, open at the top], [0.4 s on forty feet; seven beats for six], [twenty-two years], [the dismissal])
    card([S-02], [Pinchot, Vane, the driver], [a linen plat; a field book], [five pins; a dry cistern], [4.7 chains; a fifth pin], [Vane], [the fifth benchmark, not driven])
    card([S-03], [Clara, Julian, Hester], [Plate XLII; an unsealed envelope], [a chalk hollow; a pier-glass], [a fourth floor of three], [a name, a wallpaper, snow], [what was left at the desk])
    card([S-04], [Crabb, and four, of whom three cross], [galley proofs; a Catalogue], [iron boards over limestone], [four landings for two; half a beat], [a middle name], [the second act, unkeyed])
    card([S-05], [Simeon, Maren, the Chief], [an octavo of hearsay; a notebook], [boards gone to limestone], [eleven pounds in a class of four], [a ninth summer], [the second act, filed])
    card([S-06], [Ray, Varga, the sitter], [a folded programme], [the ridge under the slab], [twenty feet; the W], [a year, offered and declined], [the offer, which was not spoken])
    card([S-07], [Navarro, Veber, J.T.], [File L1-13; a draw slip], [a dry tank], [38 yards in 10 ft 6 in], [nothing; a thumbnail], [1.38 m, not sustained])
    card([S-08], [Marek, and two clerks], [Form 9-B; three petitions], [limestone rated as granite], [206 less one], [the letter M], [the class; the box is blank])
    card([S-09], [a clerk, two Vigils], [the Stores Catalogue at p. 118], [basalt; a stone face over water], [seven beats; 49.0 s], [nothing; a tally card], [the page; the downstroke])
    card([S-10], [the attendant, a petitioner, a caller], [the seventh folder; a property book], [a sealed stair], [pages 213 and 214], [a name, the colour of a room, snow], [the bell; the folder])
    card([S-11], [Paige, Lowe, a boy; Krell, Doyle, a sitter], [a field book; a works order], [warm dolomite; a slab], [3.60 chains; six feet], [Lowe; a crust], [the fifth signature])
    card([S-12], [a binder, a liquidator, a caller], [a folio; leaf 1953-B], [an iron scale], [41 lb 8 oz; 214 pages of notes], [nothing; the binder sews it], [the second act, completed unspoken])
    card([S-13], [a photographer, a man on a stool, a society], [a contact sheet], [limestone past the lamp], [six feet; half a second], [a frame, not taken], [what stands in the six feet])
    card([S-14], [a lexicographer, a later hand, a space], [an octavo of 1931], [a chalk hollow; an iron pin], [an entry omitted; page 214], [a name, a colour, snow; a ninth summer], [the dismissal])
    card([S-15], [an organist, a dean, a nave], [a reel; a leaf sewn in], [a chapel on a bluff], [a seventh beat; 0.40 s], [nothing; the hands lifted], [the dismissal, not yet due])
    card([S-16], [Halvorsen, a man with a box, whoever knocks], [a plat book in calfskin], [a corner post, warm], [3.60 chains; drift nil], [the heel of a rye roll], [nothing is said in this record])
    card([S-17], box(width: 60%, stroke: (bottom: 0.3pt + pencil))[#h(1pt)], box(width: 60%, stroke: (bottom: 0.3pt + pencil))[#h(1pt)], box(width: 60%, stroke: (bottom: 0.3pt + pencil))[#h(1pt)], [itself], box(width: 60%, stroke: (bottom: 0.3pt + pencil))[#h(1pt)], [held closed])
  })))
}

// ============================================================ Schedule F
#pagebreak(to: "odd", weak: true)
#runtitle.update([Schedule F])
#[#metadata("schedf")<opener>]
#v(0.5in)
#dept[Null Run --- Records Office --- Schedule F --- Foreign Leaves in Bound Registers]
#v(-4pt)
#{
  set par(first-line-indent: 0pt, justify: false, leading: 0.46em)
  set text(font: typew, size: 6.8pt)
  let pg(key) = context {
    let o = query(<opener>).filter(m => m.value == key)
    if o.len() > 0 { link(o.first().location())[#counter(page).at(o.first().location()).first()] } else [--]
  }
  table(columns: (1fr, 0.62in, 0.5in, 0.9in), stroke: (x, y) => (bottom: 0.3pt + pencil, top: if y == 0 { 0.6pt + ink } else { none }), inset: (x: 3pt, y: 5pt),
    table.header(text(fill: pencil)[REGISTER], text(fill: pencil)[AT PAGE], text(fill: pencil)[THREAD], text(fill: pencil)[ENTERED]),
    [Hymnal No. 114, after the index of metrical tunes (two leaves)], [not stated], [yellow], [on report],
    [Stores Catalogue, entry 1872-TT1 (two leaves)], [118], [yellow], [on report],
    [Conservatory manuscript, twelve pipes, back of final page], [not stated], [yellow], [on report],
    [Folio of 1898, at Note 114 (leaf 1953-B)], [214], [none: loose], [not a foreign leaf],
    [Staff Index, HALE to HALLAM], [---], [---], [no leaf: a margin#th("blank")],
    [The present volume: _A Book Not Yet Returned_], pg("review"), [yellow], [by the compiler],
    [The present volume: _From the Office Gazetteer_], pg("gazetteer"), [yellow], [by the compiler],
    [The present volume: _Catalogue of Apocryphal Persons_], pg("catalogue"), [yellow], [by the compiler],
    [The present volume: _Three Soundings of One Stair_], pg("soundings"), [yellow], [by the compiler],
    [The present volume, after page 212], text(fill: oxblood)[213], [#box(width: 0.3in, stroke: (bottom: 0.3pt + ink))[#h(1pt)]], [entered in advance#th("leaf")],
  )
  v(3pt)
  [SUCH LEAVES ARE NOT TO BE CUT OUT, COPIED, OR READ ALOUD (INSTRUCTION 18/53). THE COMPILER HAS PRINTED FOUR OF THEM.#n[#A[PRINTING IS COPYING. REFERRED.]][The compiler was instructed to print the volume as received.]]
}

// ============================================================ Register of Discrepancies
#pagebreak(to: "odd", weak: true)
#runtitle.update([Register of Discrepancies])
#[#metadata("register")<opener>]
#v(0.5in)
#text(font: serif, size: 19pt)[Register of Discrepancies]
#v(-2pt)
#line(length: 100%, stroke: 0.6pt + ink)
#v(4pt)
#{
  set par(first-line-indent: 0pt, justify: true)
  text(size: 8.6pt, style: "italic")[Each matter is entered once, with the pages on which an arrow stands for it. In accordance with standing procedure no discrepancy is resolved and no reading is given precedence. A page number in red is a page the volume does not have.]
}
#v(6pt)
#{
  set par(first-line-indent: 0pt, hanging-indent: 0.9em, justify: false, leading: 0.42em, spacing: 0.62em)
  set text(size: 7.9pt)
  let e(key, name, body) = par[#text(font: scfont, tracking: 0.4pt, fill: fam.at(key), name) #h(2pt) #body #h(2pt) #text(font: mono, size: 6pt, fill: pencil, thpages(key))]
  let head(t, c) = block(above: 1.1em, below: 0.6em, sticky: true, text(font: mono, size: 6.2pt, tracking: 1.6pt, fill: c, t))
  head([PAPER, THREAD AND DEPOSIT], ochre)
  e("dust", [Deposit, yellow.], [Damp; sweet as alder; under the nails, in a pawl, along the foot of a leaf. Not to be brushed out.])
  e("leaf", [Leaves, foreign.], [Sewn into finished registers with waxed yellow thread, on paper older than the register.])
  e("play", [Play, in two acts.], [Dated four ways. Written, or only quoted. Three names struck.])
  e("three", [Steward, Chorister, Stranger.], [Three readers; three posting codes; three unmarked lines.])
  e("hand", [Hand, raised.], [Held a beat before the downstroke. The downstroke not entered.])
  e("dismissal", [Dismissal.], [Not said (2004). Not yet due (undated). Fifteen days between two dates for one service.])
  head([MEASURE AND PLACE], lake)
  e("close", [Survey, not closing.], [3.60 chains inward on three runs; 4.7 chains in a county the gazetteer does not hold; a strip of seven-tenths of an inch.])
  e("needle", [Needle.], [Will not settle within twenty-five paces of Monument 3, nor within fifty of the cistern.])
  e("warm", [Rock, warm.], [In January, in February and in December, on a face the sun has not reached since autumn.])
  e("drift", [Drift: nil.], [Every neighbouring section has it. Low banks entered as wash, and as erosion.])
  e("interiors", [Interior, the.], [1,200 metres of fresh water; below the 700 metre line; a sealed cave. None sustained.])
  e("longer", [Rooms, length of.], [Larger within than without. Shorter on measurement by six feet, and by twenty.])
  e("stair", [Stairs.], [Four landings for two; a fourth floor of three; the wrong stairs.])
  e("echo", [Return, late.], [0.4 s on forty feet; half a beat; half a second.])
  e("tank", [Sink, dry.], [9 ft 8 in. Ten feet. 10 ft 6 in. Thirty-eight yards. A hundred yards.])
  head([COUNT, WEIGHT AND DATE], oxblood)
  e("seven", [Seven for six.], [A beat; a second; a post.])
  e("weight", [Weight.], [41 lb 8 oz in a class of four pounds. Nearly eleven; nine or ten; 9 lb 8 oz; 9 lb 7 oz.])
  e("count", [Count, of leaves and records.], [107 certified and 106 counted. Sixteen, and seventeen. 206 less one.])
  e("wait", [Appointment.], [2 June 1936; asked to wait; carried forward sixty-eight times of seventy.])
  e("blank", [Margin, narrow.], [Between Hale and Hallam; between Crampton and Crisp; between D and I.])
  e("post", [Counterweight.], [Seven posts; more than seven persons; a seventh folder held closed, twice.])
  e("badge", [Badge.], [311-M, or 311-R. Equipment and Personnel, both stamped.])
  e("pulse", [Thirty-five; sixty-nine.], [Beats to the minute; cycles to the second.])
  e("door", [Door 44.], [Not an exit. Form 44-B not located. The arrow gives its own page.])
  e("date", [Dates.], [1849 to 2026, received 1953. A sign passed nine days before it was ordered.])
  head([PERSONS AND LAMPS], slate)
  e("caller", [Caller.], [At the outer glass; back to the road; no luggage; nearer.])
  e("lamp", [Lamps.], [Steady; not on any circuit; red sinking to amber. One flicker, not sustained.])
  e("letter", [Letter, unlit.], [W; R; R.])
  e("knock", [Knocks, three.], [Under the slab; the floor six inches down; the end of the loaf.])
  e("toll", [Property, surrendered.], [A name, the colour of a room, and snow, under three bearers.])
  e("ninth", [Summer, ninth.], [One summer; four receipts.])
  e("name", [Names, doubled.], [Pinchot and Paige; Vane and Lowe; Halvorsen; Venn; Martin.])
  v(6pt)
  par(hanging-indent: 0pt)[#text(style: "italic")[Matters entered: thirty-two.] #text(font: typew, size: 6.4pt)[#amend[THIRTY-TWO #ns] COUNTED IN AUDIT: THIRTY-THREE.]]
}

// ============================================================ list of plates
#pagebreak(weak: true)
#runtitle.update([The Plates])
#[#metadata("plates")<opener>]
#v(0.5in)
#text(font: serif, size: 19pt)[The Plates, and the Numbers \ from Which They Were Drawn]
#v(-2pt)
#line(length: 100%, stroke: 0.6pt + ink)
#v(6pt)
#{
  set par(first-line-indent: 0pt, justify: false, leading: 0.42em)
  set text(size: 8pt)
  let r(n, subj, seed, how) = (text(font: mono, size: 6.2pt, fill: oxblood, n), subj, text(font: typew, size: 6.6pt, seed), text(style: "italic", fill: pencil, how))
  grid(columns: (0.34in, 0.95in, 0.42in, 1fr), row-gutter: 6.5pt, column-gutter: 5pt,
    ..r([---], [The boards], [53], [A surface of eighteen waves; a traverse run inward until no section is left.]),
    ..r([I], [Foreign leaf], [1898], [An alphabet of five strokes, set as verse above the rule and as rubric below it.]),
    ..r([II], [Section 16], [1891], [Contours at twenty-four levels on a surface of eighteen waves and one ridge. Drift scattered on eight sections of nine.]),
    ..r([III], [The hotel], [1913], [Nine bays by three floors, and a fourth.]),
    ..r([IV], [The tape], [none], [The cable of the fourth record in the international code, one unit to the dot.]),
    ..r([V], [The stacks], [409], [Eight shelves filled to the upright. One volume is given weight.]),
    ..r([VI], [The sign], [47], [Tube, glow and reflection. The reflection is displaced line by line.]),
    ..r([VII], [Tank 2], [14], [Drawn to the figures of Audit Note L2-18.]),
    ..r([VIII], [The tally], [311], [Two hundred and six cells; four kinds of piece; one withheld.]),
    ..r([IX], [The reel], [1872], [A theme of twelve notes by random walk, four times over, against itself reversed and one beat late.]),
    ..r([X], [The outer glass], [20], [Hatching, omitted where the coat stands.]),
    ..r([XI], [The field book], [none], [The figures of the field book.]),
    ..r([XII], [The beam], [none], [The weights printed at the heads of the records.]),
    ..r([XIII], [Contact sheet], [216], [A corridor of one vanishing point, rendered eleven times, each at six feet less.]),
    ..r([XIV], [Doors], [44], [Four kinds of door in sixteen places. One place is left.]),
    ..r([XV], [Sand figures], [1847], [Sand thrown on twelve figures of a square plate and kept where the plate is still.]),
    ..r([XVI], [Borings], [1872], [Seven columns to one scale.]),
    ..r([XVII], [The record], [17], [Not drawn from the record.]),
  )
  v(6pt)
  text(size: 8.4pt, style: "italic")[The same number draws the same plate. The compiler has drawn each twice and compared them.]
}

#clerkcheck

// ============================================================ colophon
#pagebreak()
#runtitle.update([])
#[#metadata("colophon")<opener>]
#v(1fr)
#block(width: 100%, stroke: (top: 0.6pt + ink), inset: (top: 8pt), {
  set par(first-line-indent: 0pt, justify: false, leading: 0.5em)
  text(font: mono, size: 6.2pt, tracking: 1.6pt, fill: oxblood)[COLOPHON AND DISPOSITION]
  v(2pt)
  text(size: 8.2pt)[Set in EB Garamond; in Old Standard for leaves older than the Office; in TT2020 for the Audit's machine; and in Plex Mono for the registers. The plates were drawn by procedure, each from a fixed number. All lamps steady. Seventeen records compiled; sixteen printed. Interior #withheld. #smallcaps[awaiting assessment].]
})
