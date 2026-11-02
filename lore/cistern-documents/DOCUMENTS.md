# FOUND DOCUMENTS — the flooded cistern

**Status: PROPOSAL.** Text only. Nothing here is rendered, built, imported, pushed or posted.
Every string is original; no real place, person or organisation is named. Companion to
`nullrun-cistern-text-20261102/CISTERN-TEXT.md` and `WAYFINDING.md`; the water, the datum and the
route codes are the same.

**What is here.** Eight self-writing ledger entries, six inspection tags, four maintenance notices, six
pickup labels, and three two-sided gauge cards. Every item has a placement and a 38-character limit.

**The water, for consistency.** Works Zero is the sill of Sluice 1. High water is `+2.40`; the water
stands at `+1.95`; the old line is `+1.60`; the cistern floor is about `+1.40`. The pump inspection bay
is off the Pump Chapel (`P2`); the Gauge Gallery (`G1`) is the hub. Sump readings are depths in metres,
not heights on the staff gauge; the cards say `M` where that matters.

**The voice.** The office writes as if the works are still staffed and the paperwork is still current.
Nothing here explains the water, the standing figures, the dead tree or the tick. The reader supplies
the horror. No document is written by a person who knows they have stopped being one.

**The length rule.** Every line inside a code block is **38 characters or fewer**, spaces and
punctuation included. If a string needs more, it is not a label or a tag; it is a notice, and notices
go on a hook. The maximum is stated on every item as `38`.

**The placement rule.** One readable document per prop. Wall texts (notices and gauge cards) are limited
to two per room, on different walls or at different heights. Inspection tags are tied to fixtures, not
walls, so a bay may carry several; a stores room may hold several labeled items, but turn the spare
labels away so only the intended two are readable. No document is placed where the player's lamp cannot
reach it.

---

## 1. The self-writing ledger — eight entries

**The prop.** A hinge-hung register on a sloped desk at the foot of the staff gauge in the Gauge
Gallery. Chained at the spine; the chain is long enough to open the book. Ruled pages, a printed date
column, a registry hand. The ink is wet. The ledger writes when the player is not looking: on each
return to the Gauge Gallery, the next entry is present, and the page is dry whenever it is watched.
It writes one entry per visit, in order, never while observed. The date column stays blank in every
entry. The last entry is the only one with a name in the name field.

**The lags.** The ledger is always behind the player. If the player does several things before
returning, the ledger writes only the next entry; the office catches up one visit at a time. The final
entry waits until the first seven are written. It does not skip.

### L1 — the room

```
CISTERN INTAKE — OPENED
ONE PRESENT — UNNUMBERED
HOLD AT THE LINE
```

*Placement: Gauge Gallery, the chained ledger on the gauge-office desk. Trigger: first entry into the
room. Max line: 38.*

### L2 — the first wade

```
DEPTH EXCEEDED AT S-4a
WADING NOT AUTHORISED
CONTINUE — SEE NOTICE
```

*Placement: Gauge Gallery, chained ledger. Trigger: first crossing of the level line, on the S run or any flooded room.
Max line: 38.*

### L3 — the first heap

```
ONE STANDER TESTED
HEAP LEFT AT G1
NOT SALVAGE — DO NOT CUT
```

*Placement: Gauge Gallery, chained ledger. Trigger: first Armature reduced to a heap. Max line: 38.*

### L4 — the first valve

```
VALVE V-9 MOVED
WATER: NO CHANGE
WHEEL: NOT RETURNED
```

*Placement: Gauge Gallery, chained ledger. Trigger: first valve turned, whatever the player believes it did. Max line: 38.*

### L5 — the first stores issue

```
STORES ISSUE — ONE TIN
SIGNATURE: PENDING
BALANCE: OPEN
```

**Pencil, in the margin, a different hand:** `I SIGNED FOR BOTH OF US. — RD`

*Placement: Gauge Gallery, chained ledger; the pencil note is already there when the entry appears.
Trigger: first
labeled stores item taken, the medical tin or any pickup. Max line: 38.*

### L6 — the pump chapel

```
PUMP CHAPEL — ATTENDANCE
ONE — NO RELIEF POSTED
PUMP 4 STILL RUNNING
```

*Placement: Gauge Gallery, chained ledger. Trigger: first entry into the Pump Chapel or the inspection bay. Max line: 38.*

### L7 — the basin stair

```
BASIN STAIR — OPENED
FROM THE FAR SIDE
NO ONE CAME UP
```

*Placement: Gauge Gallery, chained ledger. Trigger: first opening of the basin stair, the slice's gate. Max line: 38.*

### L8 — the last entry

```
CISTERN CLOSED — BALANCE
CARRIED FORWARD
REGISTRY NR-311-R — PRESENT
```

*Placement: Gauge Gallery, chained ledger. Trigger: the next return to the Gauge Gallery after L7; if entries were
skipped, after the first seven are written. Max line: 38.*

**The number.** The last line prints the player's registry number, the case number issued at the
waiting-room desk. `NR-311-R` is the example used across this pack; at build time substitute the run's
number. If the number cannot be drawn at runtime, bake a three-digit strip per seed; this is the only
per-run string in the pack. Do not print the number anywhere else in the level.

**If the slice does not return to the hub.** Place the ledger at the Pump Inspection Bay exit instead,
or put a single loose page of L8 on the basin stair landing. The office keeps a duplicate; it does not
explain why.

---

## 2. Inspection tags — the pump inspection bay

**The props.** Small brass or card tags on tie wire, stamped with a number, a finding and a mark.
The wire is the same wire the Armatures are tied with; nobody in the bay has noticed. Tags are read at
arm's length. The bay is off the Pump Chapel, low, wet, with the sump in one corner and the dead tree
in the other.

### T1 — pump bearing

```
INSPECTION 101 — PUMP 3
BEARING SOUND — OILED
NEXT: 90 DAYS
```

*Placement: wired to the pump 3 discharge pipe, eye height. Max line: 38.*

### T2 — floor settlement

```
INSPECTION 104 — BAY FLOOR
SETTLED 4 MM — RELEVEL
MARKED — NOT LEVELLED
```

*Placement: nailed to the bay threshold beam, knee height, so it is read while wading in. Max line: 38.*

### T3 — sump grate

```
INSPECTION 108 — SUMP GRATE
CLEAR — BOLTS REFITTED
BOLTS: 3 OF 4
```

*Placement: hung on the sump grate's lifting eye, below the line; the player must kneel to read it.
Max line: 38.*

### T4 — the dead tree

```
INSPECTION 112 — "DEAD TREE"
NO GROWTH RINGS — HOLD
REFER TO STRUCTURES
```

*Placement: wired to the lowest branch of the dead tree, chest height. The tree stands in the sump
corner and does not move while read. Max line: 38.*

### T5 — the same tree, later

```
INSPECTION 116 — SAME TREE
MOVED 2 M SINCE 112
DO NOT RE-TAG — OBSERVE
```

*Placement: same tree, a higher branch, a newer wire. The tag is fresh; the tree is not where T4 says.
Max line: 38.*

### T6 — the register

```
INSPECTION 121 — REGISTER
ENTRIES CONTINUE UNSIGNED
LEAVE OPEN — IT FINISHES
```

*Placement: tied to the inspection register's chain on the bench. The register is open; the pen beside
it is dry. Max line: 38.*

**The hint.** T4 is the whole hint: a dead tree has growth rings. T5 is the office's response to the
implication: do not re-tag it, observe it. Neither tag says what the tree is. If the dead tree is the
Hollow, the ReDead spawns with it per `PILLARS.md` §5; no tag mentions the ReDead, because the office
has no form for it.

---

## 3. Maintenance notices — the Armatures

**The props.** Typed paper on a nail, a hook or the back of a door; stamped, initialled in a hand that
has since been reassigned. One corner curled. The notices are official, not graffiti; they are
maintained where the department can still reach.

### N1 — standing rebar

```
NOTICE 69 — STANDING REBAR
FIGURES FOUND STANDING AFTER
A FLOOD ARE NOT RUBBISH.
LOG THE HEIGHT. LEAVE THEM.
```

*Placement: Pump Chapel, on the door frame at eye height, where the player first meets a stander.
Max line: 38.*

### N2 — the tick

```
NOTICE 74 — THE TICK
A STANDER TICKS ONCE.
IF IT KEEPS TIME, IT IS NOT ALONE.
LOG THE INTERVAL AND WITHDRAW.
```

*Placement: Pump Inspection Bay, on the wall above the sump, at the dark end where the tick starts.
The staple is bright; this notice is newer than the others. Max line: 38.*

### N3 — clearance

```
NOTICE 77 — CLEARANCE
STANDING FIGURES ARE IN
SERVICE. DO NOT CUT OUT.
DO NOT ISSUE THEM A NUMBER.
```

*Placement: Store Alcove, on the issue hatch at chest height. The stores clerk would have posted it
where numbers are issued. Max line: 38.*

### N4 — after a flood

```
NOTICE 81 — AFTER A FLOOD
COUNT THE FIGURES BEFORE
THE WATER. COUNT THEM AFTER.
ENTER THE DIFFERENCE AS STAFF.
```

*Placement: Drainheads, on the sump rail above the line, where the count is made. Weathered, with
pencil figures in the margin too rubbed to read. Max line: 38.*

---

## 4. Pickup labels — six physical items

**The props.** Gummed paper labels, stencilled tin lids, a card sleeve, a canvas roll. The label is on
the object, not in the UI. The item rests on a surface with a contact shadow; the player walks to it
and takes it. The label stays with the object if it is dropped.

### P1 — index block tin

```
STORES 12 — INDEX BLOCK
BRASS PINS — COUNT 24
COUNTED: 23 — SEE STORES
```

*Placement: Store Alcove, shelf above the line, lid label. The tin is open; one pin is loose on the
shelf. Max line: 38.*

### P2 — seal case tin

```
STORES 14 — SEAL CASE
SEAL CARTRIDGES — 10
KEEP WAX UP — DO NOT DROP
```

*Placement: Sluice Run, on the dry step of Sluice 4, lid label. The tin is dented at one corner.
Max line: 38.*

### P3 — index strip

```
STRIP — INDEX — 8 PINS
FOR THE COMPTROLLER
DO NOT CUT OR BEND
```

*Placement: Pump Inspection Bay, on the inspection bench, in a paper sleeve. The strip is half drawn
from the sleeve, as if someone stopped mid-issue. Max line: 38.*

### P4 — cell rack

```
CELL RACK — 4 LAMP CELLS
TWO LIT — THIS IS NORMAL
DO NOT RETURN LIT CELLS
```

*Placement: Tidal Lightwell, on the tide-board shelf, in a brass cradle. The two lit cells are the
only warm light in the room. Max line: 38.*

### P5 — stores medical tin

```
STORES MEDICAL TIN — MK 2
FOR INJURY: OPEN THE TIN
FOR PAIN: FILE A FORM
```

*Placement: Store Alcove, in the medical drawer under the counter, sealed with a paper band. The band
is already broken. Max line: 38.*

### P6 — field splint kit

```
FIELD SPLINT KIT — 1
ONE LIMB PER KIT
STRAP: RETURN TO STORES
```

*Placement: Basin Stair, on the dry landing above the line, in a canvas roll. The strap is missing.
Max line: 38.*

---

## 5. Gauge cards — three, before and after

**The props.** Laminated cards on brass hooks beside their gauges, printed both sides. The last hand to
work the valve turned the matching side outward. The player may flip the card after turning the valve;
it is a physical act, like the valve itself. The card is the legend, not the gauge: the needle is a
separate prop and moves with the water.

### GC1 — pump 3 discharge

**Before — valve V-3 shut**
```
V-3 SHUT — HEAD 0.0
PUMP 3 OFF — LINE HOLDS
IF THE NEEDLE MOVES, LOG IT
```

**After — valve V-3 open**
```
V-3 OPEN — HEAD +0.4
PUMP 3 ON — LINE RISES
DO NOT STAND IN THE BAY
```

*Placement: Pump Chapel, brass hook beside the discharge gauge above pump 3. The corners are curled;
the after side is cleaner. Max line: 38.*

### GC2 — sluice 9 head

**Before — sluice 9 shut**
```
SLUICE 9 SHUT — HEAD 0.0
DOOR DRY — COUNT THE TICKS
ONE TICK PER FLOOD
```

**After — sluice 9 open**
```
SLUICE 9 OPEN — HEAD 1.2
DOOR WET — DO NOT STAND
DOWNSTREAM OF THE SILL
```

*Placement: Sluice Run, on the door frame of Sluice 9 at gauge height, hung from a wire. The after
side is brighter because it has been wiped. Max line: 38.*

### GC3 — basin stair sump

**Before — basin stair shut**
```
BASIN STAIR SHUT — SUMP 1.9 M
STAIR DRY — ONE AT A TIME
REPORT THE SECOND SET
```

**After — basin stair open**
```
BASIN STAIR OPEN — SUMP 2.4 M
STAIR FLOODING — DO NOT
DESCEND ALONE
```

*Placement: Basin Stair, on the bulkhead beside the sump gauge, above the line, on a chain. The after
side is stamped `OPEN` in red. Max line: 38.*

---

## 6. Placement manifest

| ID | Kind | Room / prop | Trigger or state |
| --- | --- | --- | --- |
| L1 | ledger entry | Gauge Gallery / chained register | first entry |
| L2 | ledger entry | Gauge Gallery / chained register | first level-line crossing |
| L3 | ledger entry | Gauge Gallery / chained register | first Armature heap |
| L4 | ledger entry | Gauge Gallery / chained register | first valve turned |
| L5 | ledger entry | Gauge Gallery / chained register | first stores item taken |
| L6 | ledger entry | Gauge Gallery / chained register | first Pump Chapel entry |
| L7 | ledger entry | Gauge Gallery / chained register | first basin stair opening |
| L8 | ledger entry | Gauge Gallery / chained register | next return after L7 |
| T1 | inspection tag | Pump Inspection Bay / pump 3 pipe | static |
| T2 | inspection tag | bay threshold beam | static |
| T3 | inspection tag | sump grate lifting eye | static |
| T4 | inspection tag | dead tree, low branch | static |
| T5 | inspection tag | dead tree, high branch | static; tree has moved |
| T6 | inspection tag | inspection register chain | static |
| N1 | notice | Pump Chapel / door frame | static |
| N2 | notice | Pump Inspection Bay / sump wall | static |
| N3 | notice | Store Alcove / issue hatch | static |
| N4 | notice | Drainheads / sump rail | static |
| P1 | pickup label | Store Alcove / index block tin | static |
| P2 | pickup label | Sluice Run / seal case tin | static |
| P3 | pickup label | Pump Inspection Bay / index strip | static |
| P4 | pickup label | Tidal Lightwell / cell rack | static |
| P5 | pickup label | Store Alcove / medical tin | static |
| P6 | pickup label | Basin Stair / splint kit | static |
| GC1 | gauge card | Pump Chapel / discharge gauge | shut / open |
| GC2 | gauge card | Sluice Run / sluice 9 frame | shut / open |
| GC3 | gauge card | Basin Stair / sump gauge | shut / open |

Counts: **8 ledger entries, 6 inspection tags, 4 notices, 6 pickup labels, 3 gauge cards** (27 documents,
two sides on each gauge card).

---

## 7. Continuity and use notes

- **The registry number is the only per-run string.** `NR-311-R` is the example seed. The ledger's last
  line must be generated from the run's case number; if it is baked, the ledger is just a prop. Do not
  print the number on any other document.
- **The ledger lags.** One entry per return to the Gauge Gallery, in order. It never writes while
  watched, and the date column is always blank. The office is behind the player; that is the point.
- **R.D.** appears once, in pencil, in the ledger's margin. It is the same set of initials as the earlier
  cistern text. It is never a name and never explained. If the requester drops R.D. from the cistern,
  drop the pencil note with it; do not replace it with another name.
- **The dead tree.** T4 is the first hint that the tree is not a tree: no growth rings. T5 is the
  second: it moved, and the inspector is told not to re-tag it. Neither says what it is. If the Hollow's
  sheet arrives and contradicts "no growth rings", change the finding, not the form: the office can be
  wrong about the detail, but it must not explain the creature.
- **The tick.** N2 is the only document that states the free/controlled distinction in the office's
  terms: a stander ticks once; if it keeps time, it is not alone. The office does not name the Spindle.
  The notice is a warning, not a taxonomy.
- **No gore.** The heap is a tangle of bars; the splint kit is a canvas roll; the medical tin is a tin.
  Nothing here describes a body or a wound.
- **The trade word.** The ledger and N2 use "stander" once each. The office's formal class is standing
  reinforcement; the floor word is what the paper picks up. Do not standardise it.
- **The one joke per prop.** The jokes are dry and institutional: `COUNTED: 23 — SEE STORES`,
  `BOLTS: 3 OF 4`, `FOR PAIN: FILE A FORM`, `ENTER THE DIFFERENCE AS STAFF`. Keep them apart; none
  shares a wall with a heap.
- **The 38-character check.** The build should reject any line over 38 characters at import. The
  strings are sized for a 512 px card at 12 px per character, with margins.
- **Wall texts and fixtures.** Notices and gauge cards are wall texts: two per room at most, on
  different walls. Tags and labels are fixtures: one per prop, and a stores room may hold several
  labeled items. The Pump Chapel carries N1 and GC1 on different fixtures; the Store Alcove carries N3
  and two labeled items; the inspection bay carries N2 and its six tags.

---

## 8. Open for Josiah

1. **The registry number.** `NR-311-R` is the example run seed and also the Armature intake number in
   `nullrun-lore-armature-20261101/ARMATURE.md`. If that collision is unwanted, substitute a neutral
   seed; the line is a token. If it is wanted, it is the strongest quiet horror in the pack: the office
   files the case and the creature under one number. Decide before the number is baked.
2. **The ledger's home.** It is placed in the Gauge Gallery because the hub is the only room the player
   reliably re-crosses. If the slice's route does not return to the hub after the basin gate, move the
   ledger to the Pump Inspection Bay exit or add the duplicate L8 page on the stair landing.
3. **The dead tree.** T4/T5 assume the tree does not attack while read. If the Hollow's sheet says it
   moves when approached, the tags must be readable from outside its reach, or the player will read
   them once, at cost. That is a level-layout decision, not a text one.
4. **R.D.** is a callback to `CISTERN-TEXT.md`. Keep or cut; if kept, the pencil note is the only
   human handwriting in the pack.
5. **The gauge card flip.** The cards assume the player can flip them after turning the valve. If that
   interaction is too costly, print both states on one card as two columns and let the player read the
   matching column. The before/after text does not change.
6. **The number of documents per room.** The manifest gives the Gauge Gallery the ledger alone, the
   Pump Chapel two wall texts on different fixtures (N1 and GC1), the Store Alcove one wall text and
   two labeled items, and the inspection bay one wall text plus its tags. If the earlier pack's "one
   text per room" rule is binding, move N1 to the bay door; the ledger and the store labels stay.
