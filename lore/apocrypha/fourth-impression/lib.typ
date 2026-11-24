// NULL RUN: THE UNCOLLECTED EDITIONS — second impression
// Page furniture, the four hands, threads, blocks.

#import "ledger.typ" as lg
#let NP = lg.NP
#let LEAVES = calc.quo(NP, 2)
#let paper = rgb("#f4eddf")
#let rag = rgb("#e6d9bb")
#let ink = rgb("#1c1a17")
#let oxblood = rgb("#8b2a20")
#let ochre = rgb("#a47418")
#let lake = rgb("#1f4e3d")
#let slate = rgb("#3c5261")
#let pencil = rgb("#6d6252")
#let board = rgb("#161513")

#let serif = "EB Garamond 12"
#let serif8 = "EB Garamond 08"
#let scfont = "EB Garamond SC 12"
#let old = "Old Standard TT"
#let typew = "TT2020 Style E"
#let mono = "IBM Plex Mono"
#let cond = "IBM Plex Sans Cond Medm"

#let BODY = 11.3pt
#let LEAD = 0.74em
#let PW = 5.5in
#let PH = 8.5in
#let MIN = 0.7in
#let MOUT = 1.2in
#let TW = PW - MIN - MOUT

// ---------------------------------------------------------------- threads
// Every recurrence of a discrepancy carries an arrow to the page of the next
// one. Most threads return to their first page. Some do not.
#let fam = (
  dust: ochre, leaf: ochre, three: ochre, hand: ochre, dismissal: ochre,
  close: lake, needle: lake, warm: lake, drift: lake, interiors: lake,
  longer: lake, stair: lake, echo: lake, tank: lake,
  seven: oxblood, weight: oxblood, wait: oxblood, blank: oxblood,
  post: oxblood, badge: oxblood, pulse: oxblood, door: oxblood, count: oxblood,
  caller: slate, lamp: slate, letter: slate, knock: slate, toll: slate,
  ninth: slate, name: slate, date: oxblood, play: ochre,
)
#let dead = (wait: NP + 1, blank: NP + 2, count: NP + 1)

#let th(key) = [#metadata(key)<th>#context {
  let col = fam.at(key, default: oxblood)
  let after = query(selector(<th>).after(here())).filter(m => m.value == key)
  let all = query(<th>).filter(m => m.value == key)
  let mk(n) = text(font: mono, size: 5.6pt, fill: col, baseline: -3.4pt, tracking: 0pt)[#h(0.6pt)›#n]
  if after.len() > 0 {
    let t = after.first()
    link(t.location(), mk(counter(page).at(t.location()).first()))
  } else if key in dead {
    mk(dead.at(key))
  } else {
    let t = all.first()
    link(t.location(), mk(counter(page).at(t.location()).first()))
  }
}]

// pages on which a thread occurs, for the Register
#let thpages(key) = context {
  let all = query(<th>).filter(m => m.value == key)
  let seen = ()
  let out = ()
  for m in all {
    let n = counter(page).at(m.location()).first()
    if n not in seen { seen.push(n); out.push(link(m.location())[#n]) }
  }
  out.join(", ")
  if key in dead [, #text(fill: oxblood)[#dead.at(key)]]
}

// ---------------------------------------------------------------- the hands
// C: the compiler (plain).  A: audit.  P: the petitioner.  E: the earlier hand.
#let A(body) = text(font: typew, size: 6.7pt)[#text(fill: oxblood)[AUDIT.] #body]
#let P(body) = [#text(font: scfont, fill: slate)[Petitioner.] #emph(body)]
#let amend(body) = text(fill: oxblood)[\[AMENDED IN AUDIT: #body\]]
#let ns = text(fill: oxblood)[NOT SUSTAINED]
#let struck = box(text(font: typew, size: 0.74em, fill: oxblood)[\[STRUCK: FORM 9-B\]])
#let withheld = text(font: typew, size: 0.8em)[\[WITHHELD PENDING SIGNATURE\]]
#let x(body) = strike(stroke: 0.5pt + ink, body)
#let n(..hands) = footnote(hands.pos().join(linebreak()))

#let eh(body) = context {
  let pos = here().position()
  let odd = calc.odd(pos.page)
  let tx = if odd { MIN + TW + 0.11in } else { 0.13in }
  box(width: 0pt, height: 0pt, place(dx: tx - pos.x, dy: -0.62em,
    block(width: MOUT - 0.26in, {
      set par(justify: false, leading: 0.42em, first-line-indent: 0pt)
      set align(if odd { left } else { right })
      text(size: 6.6pt, style: "italic", font: old, fill: pencil, hyphenate: false, body)
    })))
}

// inline office reference, typescript
#let m(body) = text(font: typew, size: 0.82em, body)

// ---------------------------------------------------------------- blocks
#let q(body) = block(width: 100%, inset: (left: 13pt, right: 6pt, y: 1pt), stroke: (left: 0.5pt + pencil), above: 1em, below: 1em, {
  set par(first-line-indent: 0pt, justify: false)
  text(size: 9.4pt, body)
})
#let doc(body) = block(width: 100%, fill: rgb("#ebe2cc"), stroke: 0.35pt + pencil, inset: (x: 9pt, y: 8pt), above: 1.1em, below: 1.1em, {
  set par(first-line-indent: 0pt, justify: false, leading: 0.5em)
  text(font: typew, size: 7.6pt, body)
})
#let rubric(body) = block(width: 100%, inset: (x: 18pt, y: 2pt), above: 1.1em, below: 1.1em, {
  set par(first-line-indent: 0pt, justify: false, leading: 0.5em)
  set align(center)
  text(font: old, size: 8.8pt, body)
})
#let wire(body) = block(width: 100%, stroke: (y: 0.5pt + ink), inset: (x: 4pt, y: 8pt), above: 1.1em, below: 1.1em, {
  set par(first-line-indent: 0pt, justify: false, leading: 0.55em)
  text(font: mono, size: 6.9pt, tracking: 0.6pt, upper(body))
})
#let notebook(body) = block(width: 100%, inset: (left: 20pt, right: 4pt, y: 6pt), stroke: (left: 0.5pt + oxblood.lighten(40%)), above: 1.1em, below: 1.1em, {
  set par(first-line-indent: 0pt, justify: false, leading: 0.62em)
  text(font: "Junicode", style: "italic", size: 9.2pt, fill: slate.darken(30%), body)
})
#let narrow(i, body) = pad(left: i * 10pt, right: i * 10pt, body)
#let sec(body) = {
  v(1.1em, weak: true)
  block(sticky: true, below: 0.9em, align(center, text(font: scfont, size: 10.2pt, tracking: 0.7pt, fill: ink, body)))
}
#let rule = align(center, block(above: 1em, below: 1em, line(length: 22%, stroke: 0.4pt + pencil)))
#let cap(l) = text(size: 2.5em, fill: oxblood, l)


#let dept(body) = block(width: 100%, below: 1.3em, {
  set par(justify: false, first-line-indent: 0pt, leading: 0.5em)
  align(center, text(font: typew, size: 6.8pt, fill: pencil, tracking: 0.3pt, upper(body)))
})
#let entry(body) = block(width: 100%, inset: (x: 12pt, y: 6pt), stroke: (y: 0.4pt + ink), above: 1.1em, below: 1.1em, {
  set par(first-line-indent: 0pt, justify: true, leading: 0.5em)
  text(font: old, size: 8.2pt, body)
})
#let hw(body) = text(font: scfont, tracking: 0.6pt, body)
#let lexgap = block(width: 100%, height: 8.2em, stroke: (left: (paint: pencil, thickness: 0.3pt, dash: "dotted")))[#h(1fr)#th("blank")]
#let lexnote(body) = block(width: 100%, above: 1.6em, inset: (left: 0pt), {
  set par(first-line-indent: 0pt, hanging-indent: 0pt)
  text(font: scfont, size: 8.6pt, tracking: 0.4pt)[A note added in pencil at the foot of the final page, directly above a thin line of damp yellow dust#th("dust")]
  parbreak()
  text(fill: pencil.darken(25%), body)
})
#let note114 = {
  doc[NOTE 114 (EDITORIAL APPARATUS --- 1898 / 1953) \ Three incompatible locations are cited for the same stage: (a) 1,200 m of fresh lake water over silt; (b) below the 700 m line in the East Antarctic subglacial range; (c) a sealed limestone cavern with no surface outlet.#th("interiors") #amend[NONE SUSTAINED]]
  align(center, rotate(180deg, reflow: true, block(width: 84%, doc[NOTE 114-b (LOOSE LEAF 1953-B --- INVERTED MARGINALIUM) \ Measured on the stores beam scale against two one-pound brass tares: 41 lb 8 oz. Do not brush the lower margin.])))
}
#let canon = block(width: 100%, above: 1.3em, below: 1.3em, breakable: false, {
  set par(first-line-indent: 0pt, justify: false, leading: 0.5em)
  set text(size: 8.4pt)
  let f = ([1. Twelve principal pipes, dry reed stop.], [2. Forty-foot limestone nave.], [3. Cross at the twenty-fourth second.], [4. Six beats written in the closing bar.], [5. Hands lifted cleanly from the manuals.], [6. Silence.])
  let r = ([6. Silence answered from the nave.], [5. Hands still resting on the stone.], [4. Six beats counted in the dark.], [3. Cross missed by one half-breath.], [2. Forty-foot wall returning 0.40 s late.], [1. Seventh beat enters alone.])
  let cells = ()
  for i in range(6) {
    cells.push(f.at(i))
    cells.push(align(right, box(scale(x: -100%, text(fill: lake, style: "italic", r.at(i))))))
  }
  grid(columns: (1fr, 1fr), column-gutter: 8pt, row-gutter: 0.62em,
    text(font: typew, size: 6.2pt, fill: oxblood)[FORWARD VOICE \ 00.0 s to 48.0 s],
    align(right, text(font: typew, size: 6.2pt, fill: lake)[RETROGRADE VOICE \ 49.0 s back to 01.0 s]),
    grid.hline(stroke: 0.4pt + ink),
    ..cells)
})
#let strata = block(width: 100%, above: 1.3em, below: 1.3em, breakable: false, {
  set par(first-line-indent: 0pt, justify: false, leading: 0.5em)
  let row(yr, src, body) = (text(font: typew, size: 7.4pt, fill: oxblood)[#yr \ #text(fill: pencil, size: 5.8pt, src)], text(font: typew, size: 7.2pt, body))
  grid(columns: (0.9in, 1fr), inset: (x: 5pt, y: 6pt), stroke: (x, y) => (top: 0.5pt + ink, bottom: 0.5pt + ink),
    ..row([1872], [IRONWORKS LOG], [Boring 1 through 5, west of works: dolomite, red clay, a little lead ore. Drift: nil. Low banks entered as wash. We do not cut there. --- W. Harris]),
    ..row([1892], [FIELD BOOK], [E 80.00 ch · S 80.00 ch · W 77.12 ch · N 77.84 ch. Closure error: 3.60 ch inward. Needle will not settle near Mon. 3.]),
    ..row([1953], [WORKS ORDER], [Gallery 9 re-measures 210 ft against 216 ft drawings after feeder isolation. Difference (6 ft) entered as found. AWAITING ASSESSMENT.]))
})

#let cabpaper(id, title, meta, contra, body) = block(width: 100%, breakable: true, below: 15pt, above: 0pt, {
  set par(first-line-indent: 0pt, justify: false, leading: 0.55em, spacing: 0.6em)
  block(sticky: true, below: 3.5pt, {
    text(font: mono, size: 6.2pt, fill: oxblood, tracking: 0.4pt, id)
    h(4pt)
    text(font: scfont, size: 7.6pt, tracking: 0.2pt, title)
    linebreak()
    text(size: 6.3pt, style: "italic", fill: pencil, meta)
    if contra != [] { linebreak(); text(size: 6.3pt, style: "italic", fill: oxblood.lighten(15%), contra) }
    v(-3pt)
    line(length: 100%, stroke: 0.3pt + pencil)
  })
  text(font: typew, size: 7.4pt, body)
})

// ---------------------------------------------------------------- record opener
#let runtitle = state("runtitle", [])
#let record(num, loc, title, weight: [], recd: [], short: none) = {
  pagebreak(weak: true)
  counter(footnote).update(0)
  runtitle.update(if short != none { short } else { title })
  [#metadata(num)<opener>]
  v(0.42in)
  grid(columns: (auto, 1fr), align: (left, right),
    text(font: mono, size: 7pt, fill: oxblood, tracking: 1pt, num),
    text(font: mono, size: 6.6pt, fill: pencil, tracking: 0.8pt, eval(loc, mode: "markup")))
  v(3pt)
  {
    set par(justify: false, leading: 0.5em)
    show heading: it => text(font: serif, size: 19pt, weight: "regular", it.body)
    heading(level: 2, title)
  }
  v(-2pt)
  line(length: 100%, stroke: 0.6pt + ink)
  v(-5pt)
  text(font: mono, size: 5.4pt, fill: pencil, tracking: 0.5pt)[RECD #recd #h(1fr) CLASS: FOUR POUNDS AND UNDER #h(1fr) ON THE SCALE: #weight]
  v(13pt)
}

#let part(num, title, sub) = { pagebreak(to: "odd", weak: true); page(header: none, footer: none)[
  #runtitle.update([])
  #v(1.9in)
  #text(font: mono, size: 7pt, fill: oxblood, tracking: 2.5pt)[PART #num]
  #v(2pt)
  #{
    set par(justify: false)
    show heading: it => text(font: serif, size: 25pt, weight: "regular", tracking: 0.5pt, it.body)
    heading(level: 1, title)
  }
  #v(2pt)
  #line(length: 34%, stroke: 0.6pt + ink)
  #v(4pt)
  #set par(justify: false)
  #text(style: "italic", size: 10pt, fill: pencil, sub)
] }

#let plate(file, num, caption, w: 100%) = { pagebreak(to: "even", weak: true); page(header: none, margin: (inside: 0.5in, outside: 0.5in, top: 0.55in, bottom: 0.95in))[
  #set par(first-line-indent: 0pt, justify: false, leading: 0.45em)
  #v(1fr)
  #align(center, image(file, width: w))
  #v(7pt)
  #text(font: mono, size: 6pt, fill: pencil, tracking: 0.3pt)[#text(fill: oxblood)[PLATE #num] --- #caption]
  #v(1.2fr)
] }

// a foreign leaf: older paper, sewn in with yellow thread
#let leaf(body) = page(fill: rag, header: none,
  background: context {
    let odd = calc.odd(here().page())
    let xx = if odd { 0.2in } else { PW - 0.2in }
    for i in range(15) {
      place(top + left, dx: xx, dy: 0.5in + i * 0.52in, line(angle: 90deg, length: 0.3in, stroke: (paint: ochre, thickness: 1.1pt, cap: "round")))
    }
    place(bottom + left, image("art/dust-3.png", width: PW))
  })[
  #set text(font: old, size: 9.1pt)
  #set par(leading: 0.56em, spacing: 0.56em)
  #show footnote.entry: set text(font: old, size: 7.2pt)
  #body
]

// ---------------------------------------------------------------- page
#import "ledger.typ": ledger, LSTART
#let book(body) = {
  set document(title: "Null Run: The Uncollected Editions", author: "Null Run Receiving Office, Records Office")
  set page(width: PW, height: PH, fill: paper,
    margin: (inside: MIN, outside: MOUT, top: 0.95in, bottom: 1.12in),
    header-ascent: 0.3in, footer-descent: 0.34in,
    header: context {
      let p = counter(page).get().first()
      let phys = here().page()
      if query(<opener>).any(o => o.location().page() == phys) { return }
      set text(font: scfont, size: 7.6pt, tracking: 0.8pt, fill: pencil)
      if calc.odd(phys) [#runtitle.get() #h(1fr) #text(font: serif, size: 9pt, number-type: "old-style", fill: ink)[#p]]
      else [#text(font: serif, size: 9pt, number-type: "old-style", fill: ink)[#p] #h(1fr) the uncollected editions]
    },
    footer: context {
      let p = counter(page).get().first()
      if p >= LSTART and p - LSTART < ledger.len() {
        set par(leading: 0.4em, justify: false)
        line(length: 100%, stroke: 0.3pt + pencil)
        v(-7pt)
        text(font: typew, size: 5.7pt, fill: pencil, ledger.at(p - LSTART))
      }
    },
    background: context {
      let phys = here().page()
      let p = counter(page).get().first()
      let marks = query(<th>).filter(m => m.value == "dust" and m.location().page() == phys)
      if marks.len() > 0 {
        let k = calc.min(5, 1 + calc.quo(p, 44))
        place(bottom + left, image("art/dust-" + str(k) + ".png", width: PW))
      }
    })
  set text(font: serif, size: BODY, fill: ink, lang: "en", number-type: "old-style", hyphenate: true)
  set par(justify: true, leading: LEAD, spacing: LEAD, first-line-indent: 1.15em)
  set footnote.entry(separator: line(length: 22%, stroke: 0.35pt + ink), gap: 0.42em, indent: 0em, clearance: 0.9em)
  show footnote.entry: it => {
    set text(font: serif8, size: 7.9pt, number-type: "old-style")
    set par(leading: 0.42em, first-line-indent: 0pt, justify: true)
    it
  }
  show link: it => it
  show heading: set block(above: 0pt, below: 0pt)
  body
}
