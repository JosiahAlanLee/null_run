#import "lib.typ": *

// ============================================================ A Book Not Yet Returned
#let review = leaf[
  #runtitle.update([A Book Not Yet Returned])
  #[#metadata("review")<opener>]
  #set par(first-line-indent: 1em, justify: true)
  #v(0.2in)
  #align(center)[
    #text(size: 7pt, tracking: 1.5pt)[FROM _NOTES & REMAINDERS_, A QUARTERLY FOR THE PROVINCIAL TRADE, No. 47]
    #v(4pt)
    #text(size: 15pt)[A Book Not Yet Returned]
    #v(2pt)
    #line(length: 18%, stroke: 0.5pt + ink)
  ]
  #v(6pt)

  #par(first-line-indent: 0pt)[We have had on the desk for some weeks a volume of sixty-four pages lettered _The Uncollected Editions_, without a publisher's name, and sent to us, so far as we can discover, by nobody. It contains sixteen stories. We say stories; the volume says records, and prints at the foot of every page the words _Disposition: Awaiting Assessment_, as though the reader had been handed something to hold while its owner was looked for.]

  Let us dispose of the printing first, since the printing disposes of a good deal. The text is set in a face designed for the screens of calculating machines. Words such as _hollow_ and _cistern_ are printed in green wherever they fall, and _ochre_ in ochre, a device we believe we have met before in a longer book about a house, and which gains nothing by being used in a shorter one about a county. Page 6 carries five marks like the points of a pen tried on blotting paper, and nothing else. We take these to be the most candid lines in the volume. And every page of our copy is narrower than its sheet by a strip at the fore-edge of some seven-tenths of an inch, which our binder, who has an exact mind, tells us is constant throughout and falls always on the same side.#th("close")

  The stories are of two kinds, and the anthologist appears not to have noticed. The first six are told. A seminarian, a surveyor's boy, three guests at a failing hotel, a clerk of the Museum, a shelver in a library of the unwritten and a man who mends signs each come upon the same yellow pamphlet or its consequences, and each is furnished with someone at the elbow to say what it means. The old surveyor in the second explains for a page and a half why the ice went round the county. He should not. A reader will follow a man a long way into a cold field who says only _We are checking the pins_, and will not follow him an inch once told what the pins hold down. These six have the anthologist's vice of supposing that an explanation is a form of hospitality.

  The remaining ten are another matter and, we suspect, another hand. Nobody explains anything. An auditor lowers a plumb line thirty-eight yards into a tank ten feet deep and, finding that the figures disagree, divides one by the other and files the quotient. A joiner learns that his boots are entered as personnel and his dinner as equipment, and is troubled by the arithmetic. A night attendant keeps a folder shut with the flat of one hand and writes up the log with the other. This is the real thing: a calamity conducted throughout in the passive voice, by persons anxious not to scuff the floor.

  It is also, we must say, one story. By the twelfth we had begun to tick off the properties as they came on---the dust, the lamp with its wires hanging, the letter that will not stay lit, the visitor with their back turned---and by the sixteenth we had a full card. A motif is a fine thing. Sixteen stories that share eleven of them are an inventory.

  And yet the inventory is the interesting part, and we doubt the anthologist knows it. Read as stories, the sixteen repeat one another. Read as depositions they contradict one another, and usefully. One dry sink is nine feet eight, ten feet, ten feet six and a hundred yards deep. One survey fails to close by 3.60 chains and by 4.7. A man who is lost in 1891 is called Vane in December and Lowe in October. A second edition, if there is to be one, should stop printing these as fiction and print them as evidence, with whatever the clerks have written on them. We should read that book.

  We have been asked to return our copy. We do not find that we were sent one.

  #align(right)[H.]
]

// ============================================================ Catalogue of Apocryphal Persons
#let catalogue = leaf[
  #runtitle.update([Catalogue of Apocryphal Persons])
  #[#metadata("catalogue")<opener>]
  #set par(first-line-indent: 0pt, hanging-indent: 0.9em, justify: true, spacing: 0.72em)
  #set text(size: 8.3pt)
  #let e(name, body) = par[#text(tracking: 0.5pt, size: 7.6pt, upper(name)) #h(2pt) #body]
  #v(0.1in)
  #align(center)[
    #text(size: 13pt)[Catalogue of Apocryphal Persons \ Retained as Counterweights]
    #v(1pt)
    #text(size: 7pt, tracking: 1pt)[LONDON, 1885--1900, AND CONTINUED #h(1em) EXTRACT, pp. 42--43]
    #v(1pt)
    #line(length: 18%, stroke: 0.5pt + ink)
  ]
  #v(3pt)
  #e[Bram.][Stagehand (_fict._). No surname entered. Casts no shadow under gas. Not tested under electric light.]
  #e[Breuer, Otto.][Alienist. Clinic removed from the street map with the patient, 1884. Believes the valise to be his own.]
  #e[Cole, Hester.][Widow. Entered from a hotel register that shows three floors. Last seen on a stair. Not retained; not released.]
  #e[Crabb, Edmund.][As printed in the fourth record. The subject has since consulted the Suffolk registers.]
  #e[Delacroix, Henriette.][Minor figure in a drowned anthology. Sharper in gaslight than at noon.]
  #e[Hale, Edmund.][Priest. Estate of 2004. The only person in this Catalogue who is also in the Staff Index.#th("blank")]
  #block(height: 3.4em, width: 100%, stroke: (left: (paint: pencil, thickness: 0.3pt, dash: "dotted")))[]
  #e[Hallam.][No forename. No record. Entered as a boundary.]
  #e[Halvorsen.][One entry; two forenames, Arthur and Martin, in the same ink. Query whether one man at two dates, or two men at one.#eh[Three.]#th("name")]
  #e[Kowalski, Martin.][Reader (Stranger). Entered as "already on".]
  #e[Lindholm, Clare.][Organist (Chorister). Since 2005, binder. See the certificate at the head of the present volume, which is not signed.#th("leaf")]
  #e[Lowe, C. R.; Vane, Thomas.][Chainman; draftsman. One folder.]
  #e[Marek, K.][Joiner, Provisional. Badge 311-M. Not apocryphal. Entered in error. #text(font: typew, size: 6.2pt)[#amend["IN ERROR" #ns]]#th("badge")]
  #e[Maren.][No surname given. Typist of other people's diagnoses. Released, lighter by one summer.]
  #e[Marsh, Julian.][Dealer in miniatures. Holds no receipt.#th("toll")]
  #e[#x[Navarro, M. K.]][#x[Auditor.] The Bureau does not retain its own officers as counterweight. Entry struck.]
  #e[Paige, E. T.; Pinchot, Ezra.][Surveyor. One folder.]
  #e[Ray.][Sign-fitter. No surname. Declined a chair.]
  #e[Simeon.][Assistant Shelver; 412 years' service. The Catalogue cannot retain as counterweight a person employed in retaining counterweights. Referred.]
  #e[Trevithick, Tamsin.][Belongs to folklore rather than print. Outside the Catalogue's powers. Entered for completeness.#th("knock")]
  #e[Varga.][Proprietor. Several proper names, of which three are known.]
  #e[Veber, M.][Petitioner. Personnel on one ledger, Resident on another.]
  #e[Venn, Clara; Venn, Mr.][Two folders. The keeper of this Catalogue is a Mr. Venn. This entry is in another hand.]
  #v(3pt)
  #par(hanging-indent: 0pt)[#text(style: "italic")[Persons entered, twenty-five. Posts kept as counterweight, seven.#th("post")] #text(font: typew, size: 6.2pt)[#amend[TWENTY-FIVE #ns] COUNTED IN AUDIT: TWENTY-SIX NAMES, TWENTY-TWO ENTRIES, ONE SPACE.]]
]

// ============================================================ The Property Book
#let property = [
  #pagebreak(weak: true)
  #runtitle.update([The Property Book])
  #[#metadata("property")<opener>]
  #v(0.4in)
  #dept[Null Run --- Outer Gate Lodge --- Property Book --- Extract]
  #v(-4pt)
  #{
    set par(first-line-indent: 0pt, justify: false, leading: 0.46em)
    set text(font: typew, size: 6.7pt)
    let r(no, what, who, cls) = (text(fill: oxblood, no), what, who, cls)
    table(columns: (0.5in, 1fr, 0.82in, 0.92in), stroke: (x, y) => (bottom: 0.3pt + pencil, top: if y == 0 { 0.6pt + ink } else { none }), inset: (x: 3pt, y: 5pt),
      table.header(text(fill: pencil)[RECEIPT], text(fill: pencil)[SURRENDERED AT THE GATE], text(fill: pencil)[BEARER], text(fill: pencil)[CLASS]),
      ..r([53-G17], [A first name. The colour of a room. What snow feels like.#th("toll")#n[#P[This is my line.]]], [Bearer], [EQUIPMENT. NOT RETURNABLE.]),
      ..r([---], [A mother's Christian name. The colour of a wallpaper. What snow felt like. The name of a girl who sold pomegranates.], [J. Marsh, 1913], [EQUIPMENT]),
      ..r([---], [Four winters, one orchard.], [C. Venn], [EQUIPMENT]),
      ..r([---], [Three summers, entered as six hours.], [H. Cole], [EQUIPMENT]),
      ..r([---], [One summer, the ninth. A porch. Cedar after rain. The third step.#th("ninth")], [Maren ---], [EQUIPMENT. HELD IN A DRY WING.]),
      ..r([---], [One middle name.], [A printer. Did not present.], [EQUIPMENT]),
      ..r([---], [A signature, the fifth.], [C. R. Lowe, chainman], [NOT RETURNED FROM FIELD DUTY]),
      ..r([---], [The letter M.#th("badge")], [K. Marek], [EQUIPMENT / PERSONNEL (BOTH STAMPED)]),
      ..r([---], [Twenty-two years.], [A. Halvorsen], [HELD. NOT SURRENDERED.]),
      ..r([---], [The year he drove in from.], [Ray, sign-fitter], [OFFERED. NOT TAKEN. NO ENTRY.]),
      ..r([---], [The ends of the bread ration.], [Krell; M. Halvorsen], [COURTESY (NO SUCH COLUMN). EQUIPMENT.]),
      ..r([---], [#withheld], [T. Vane], [---]),
    )
    v(2pt)
    [LINES: TWELVE. RETURNED: NIL. THE BOOK HAS ONE COLUMN FOR CLASS.#n[#A[TWELVE LINES. ELEVEN BEARERS. ONE LINE HAS NO BEARER AND ONE BEARER HAS NO LINE. THE TWO ARE NOT THE SAME LINE.]]]
  }
  #v(8pt)
  #text(size: 8.6pt, style: "italic", fill: pencil)[The compiler prints the extract because five of the records refer to it. The book itself is kept on the shelf beside the Appointments Ledger and is not lent.]
]

// ============================================================ Three Soundings of One Stair
#let soundings = leaf[
  #runtitle.update([Three Soundings of One Stair])
  #[#metadata("soundings")<opener>]
  #set par(first-line-indent: 0pt, justify: false, leading: 0.6em, spacing: 0.8em)
  #v(0.15in)
  #align(center)[
    #text(size: 14pt)[Three Soundings of One Stair]
    #v(1pt)
    #line(length: 18%, stroke: 0.5pt + ink)
  ]
  #v(4pt)
  #let L(b) = text(fill: lake, b)
  #let I(b) = text(fill: slate, b)
  #let K(b) = text(fill: oxblood, b)
  #move(dx: -0.34in, block(width: TW + 0.68in, {
    set text(size: 7.7pt)
    let col(head, a, b, c, d) = [
      #text(size: 6pt, tracking: 0.4pt, upper(head))
      #v(-2pt)
      #line(length: 100%, stroke: 0.4pt + ink)
      #v(-2pt)
      The stair goes down from the lodge by eleven landings. At the foot there is a window. #a The gauge beside it gives #b. The clerk who reads it is asked to enter what the gauge gives, and has done so. On the sill there is #c. Above the ceiling there is #d. Knowing which has not helped anyone up the stair.#th("interiors")
    ]
    grid(columns: (1fr, 1fr, 1fr), column-gutter: 11pt,
      col([Station 53-N \ 1,620 m freshwater silt, 4.2 deg C], L[It stands green to the sill, and the silt lies one hand below the glass.], L[1,200 metres of fresh water], L[a line of fine grey silt], L[a lake]),
      col([Station 78-S \ 3,840 m accretion ice, minus 43.0 deg C], I[Its third row of louvres is sealed with rime, and the thermometer on the frame reads minus two.], I[700 metres of ice], I[frost, which dries without leaving water], I[a range under the ice]),
      col([Vent 00-Closed \ smoke test, three hours: no draught], K[It is a blind frame. No daylight has fallen on it at any hour.], K[no figure, and no draught], K[nothing; the sill is limestone, with three small shells in it], K[rock, and no outlet]),
    )
  }))
  #v(8pt)
  #par(justify: true)[#text(size: 8pt, style: "italic")[The heading over each column is chosen by a number drawn at the start of a descent. The same stair, on another number, is headed otherwise. The compiler has been assured that the number never selects the true one, and has asked how that is known.]#n[#A[THREE COLUMNS. SEVENTY-ONE WORDS IN COMMON. THE WORDS NOT IN COMMON ARE PRINTED IN COLOUR, CONTRARY TO THE COMPILER'S NOTE ON THE DISCONTINUED PRACTICE.]]]
]

// ============================================================ The Measurement of Rooms
#let circular = [
  #pagebreak(weak: true)
  #runtitle.update([The Measurement of Rooms])
  #[#metadata("circular")<opener>]
  #v(0.4in)
  #dept[Null Run --- Survey Bureau --- Circular 53/121 --- The Measurement of Rooms]
  #{
    set par(first-line-indent: 0pt, justify: false, leading: 0.5em)
    set text(font: typew, size: 7.5pt)
    let cl = (
      [A room is to be measured once, at survey, and the figure entered on the drawings.],
      [A room found on a later occasion to differ from its drawings is to be entered as found. The drawings are not to be amended.],
      [It has been observed in Gallery 9 (Works Order 53/112) that a room measured after the isolation of its feeder is shorter than its drawings by six feet.#th("longer")],
      [It has been reported from an address outside the establishment that a corridor of the same drawn length loses six feet at each measurement, whether by tape or by photograph.],
      [Until the Bureau has determined whether clauses 3 and 4 describe one occurrence or two, no room is to be measured more than once in a quarter.],
      [A room of 216 feet permits thirty-six measurements. Officers will keep a tally on the door.],
      [The tally is a measurement of the number of measurements. It does not count against the room.],
      [Pacing is measurement. Counting tiles is measurement. An estimate by eye, if spoken aloud, is measurement.],
      [Reading the length of a room from this circular is not measurement.],
      [An officer who finds that a room has been measured in their absence will not measure it again to make sure.],
      [The Bureau is not able to say what stands in the six feet.],
      [This circular has been measured.],
    )
    for (i, c) in cl.enumerate() {
      block(width: 100%, above: 0.7em, below: 0.7em, pad(left: i * 6.5pt, right: i * 6.5pt, grid(columns: (1.6em, 1fr), text(fill: oxblood)[#(i + 1).], c)))
    }
  }
  #v(6pt)
  #align(center, image("art/plan.svg", width: 82%))
  #v(-2pt)
  #{
    set par(first-line-indent: 0pt, justify: false, leading: 0.45em)
    text(font: mono, size: 6pt, fill: pencil)[#text(fill: oxblood)[FIG.] --- Sixteen links entered on the drawings of a maze of five areas. No sheet has been found on which all sixteen can be drawn to scale.]
  }
]
