#import "lib.typ": *
#import "ledger.typ": LSTART

// The seventeenth record is held closed. Its page carries no text: only the
// places at which notes were made, from the outside.
#let at(x, y, body) = place(top + left, dx: x, dy: y, body)
#let ghost(w) = box(width: w, height: 0.5pt, fill: rgb("#d9cfb8"))
#let lines(n, short: ()) = {
  for i in range(n) {
    at(0%, i * 14.6pt + 6pt, ghost(if i in short { 46% } else { 100% }))
  }
}

#block(width: 100%, height: 3.05in, {
  lines(15, short: (5, 11, 14))
  at(31%, 0pt, n[The seventeenth record is held closed. It was brought to the compiler's desk on request and has not been opened there. Everything that follows was noted from the outside.#th("count")])
  at(78%, 14.6pt, n[Wrapper: pale grey manila, tied with cotton tape. The tape has not been untied. The compiler is not able to state that it has ever been tied.])
  at(12%, 43.8pt, n[#A[ON THE SCALE: 9 LB 8 OZ. BY DIFFERENCE FROM THE CERTIFICATE: 9 LB 7 OZ. BY THE WEIGHT LEFT IN THE DRAWER: 9 LB. THREE WEIGHTS FOR ONE FOLDER.#th("weight") ALL THREE ARE THE FOLDER'S.]])
  at(58%, 73pt, n[Thickness at the fore-edge, by brass rule: one inch and one-eighth. The compiler has measured it once.][#A[MEASURED AGAIN IN AUDIT: ONE INCH AND ONE-SIXTEENTH. SEE CIRCULAR 53/121, CLAUSE 10.]])
  at(40%, 102.2pt, n[The leaves cannot be counted at the fore-edge without parting them. The binder's certificate allows this record one leaf: the leaf that would carry pages 213 and 214.][#A[A LEAF OF 9 LB 8 OZ. COMPARE LEAF 1953-B: 41 LB 8 OZ. #amend[ONE LEAF #ns]]])
  at(88%, 131.4pt, n[A corner of one leaf stands proud of the wrapper at the head. It carries the ends of four lines, which are printed here because they can be read without opening the record: _---at the outer glass / ---not on any circuit / ---said / ---ed to wait._#th("wait")])
  at(22%, 175.2pt, eh[It is not closed. It is facing away.])
  at(22%, 175.2pt, n[On the cover, in a Records Office hand, the number 17, and the class. The class is stamped twice, #smallcaps[equipment] and #smallcaps[personnel], one over the other.#th("badge")])
})

#pagebreak()

#block(width: 100%, height: 2.6in, {
  lines(13, short: (2, 8, 12))
  at(46%, 0pt, n[The foot of the wrapper carries the deposit, damp. It has not been brushed out.#th("dust") Under the glass the grains are all of one size.])
  at(9%, 29.2pt, n[The record smells of alder and of a closed drawer; and faintly of lake water; or of ice; or of nothing, as stone does. The compiler has asked three colleagues and has three answers.#th("interiors")])
  at(70%, 58.4pt, n[Laid flat on the desk, the record gives a low note that can be felt in the wood and cannot be heard. The Instruments Section puts it at sixty-nine cycles.#th("pulse")])
  at(27%, 87.6pt, n[#A[DATE OF RECEIPT: NOT ENTERED. THE GATE LOG FOR 20 DECEMBER ENDS AT 02:00. THE RECORD WAS ON THE DESK AT 02:00.]])
  at(84%, 102.2pt, n[#P[I ask whether the seventeenth record is mine. I do not ask to see it. I ask only whether, if it were opened, the first name in it would be the name on my receipt.#th("toll")]][#A[ACKNOWLEDGED. NUMBERED 31-C. DEFERRED.]])
  at(52%, 131.4pt, eh[Sixteen were sent. One was here.])
  at(52%, 131.4pt, n[The holder of the seventh post is not to be shown their own folder.#th("post") The compiler has asked whether the same rule applies to the seventeenth record, and to whom. The question has been acknowledged.])
  at(18%, 175.2pt, n[The record is to be held until it is called for. The appointment is carried forward at the foot of this page, as it has been at the foot of every page since page #LSTART, and it is next carried forward to a page on which there is nothing to carry it.#th("wait")])
})
