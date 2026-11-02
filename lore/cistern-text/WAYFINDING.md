# WAYFINDING — the Descent Works sign system, flooded cistern

**Status: PROPOSAL.** Text only. Every string is original; no real place, person or
organisation is named. Companion to `CISTERN-TEXT.md` (the writing in the rooms) and
`SOUND-CUES.md` (the audible half of the same system).

**The problem.** Playtests lose the exits. The fix is not more signs. It is one sign
system applied without exception, so that a player who has read one door can read the
level. The single rule the rest of this document serves:

> **An exit is a lit transom plate carrying the next zone's code. Nothing else in the
> level is lit that way.**

Everything below exists to make that rule legible, repeatable and cheap for a generator.

---

## 1. Four schemes on one wall

The cistern was signed by four hands, in this order. All four are still on the walls.
The player learns the stack the way they learn a dialect: by seeing the same door
signed twice and noticing which sign the lamp is over.

**Descent Works — oldest, the tank scheme.** Ochre ground, black stencil, 90 mm
letters. Route letters, valve numbers, no room names. Arrows are double-line and point
at the next *fixture* — a valve, a lamp, a plate, a door — never at a destination.
Their stair was removed when the tank was filled; their arrows still point at the
sockets where it hung. Every arrow that appears to point at a blank wall is theirs,
and it is not wrong: the wall is where the next fixture was.

**Works & Descent — current, the office's works department.** White on oxide red, or
black on galvanised plate. Chevrons, route codes, pace plates, transom plates. The
department maintains what it can reach above the line. Below the line it maintains
the record instead, which is why the paperwork is complete and the route is not.

**The Gauge & Sounding Office.** No arrows at all. A staff gauge, a red tide tick, a
brass pointer, a height. Their grammar is positional: the tick is on the side the water
last came from, so the safe side is the side without the tick. They do not name rooms.
They name water.

**Lighting & Fluorescent Fittings.** The transom lamps: the one thing in the level that
signs itself. They do not paint. They light other departments' paint. A Lighting
fitter's entire vocabulary is on, flicker, off.

**How each hand draws an arrow.** The four marks are distinguishable at a glance and
never share a wall without a height difference:

| Hand | Mark | Points at | Height |
| --- | --- | --- | --- |
| Descent Works | double line, 20 mm gap, open head | the next fixture | 1.4 m |
| Works & Descent | solid chevron, 45°, 300 mm long | the next door on the maintained route | 1.2 m |
| Gauge & Sounding | one vertical rule with a single cross-tick | the safe side: the tick points away from the water | gauge height |
| Lighting | no arrow; the hood is deeper on the door side | the door under the lamp | above the transom |

A double-line arrow at 1.2 m is a repaint over an older mark; a chevron at 1.4 m is a
correction hung too high. The height is the tell, not the shape.

Under all four: **the inhabitants.** Grease pencil, scratch, tally, a name written
until the pencil goes flat. Not a scheme. Never lit, never over a transom, never
maintained. The generator must not read it as a route cue. It is the sound of someone
else using the route.

---

## 2. The six sign types

### 2.1 Transom plates — the exits

A transom plate is a stencilled plate on the lintel, under a hooded lamp clamped to the
transom bar. The lamp throws a hard pool of light down the door; the plate is readable
at 30 m in the dark and unreadable when the lamp is out. **The lamp is the sign. The
plate is the detail.**

Four states, and only four:

| State | Reads as | Means |
| --- | --- | --- |
| **Steady** | warm, even, no flicker | maintained route; the department walks it |
| **Flicker** | irregular, ballast-led | contested route; enemies use it too |
| **Dark, clean glass** | no light, no dust | maintained but unfunded; usually optional or dead |
| **Dark, dust on the glass** | no light, grey film | sealed; the plate is a survivor |

No *lit* transom is placed on a dead end, an optional room, or the near face of a
shortcut. A dark-clean plate may survive on any of the three; it is not a pull. If a
player sees a lit transom, they are looking at a way on.

### 2.2 Route codes

Format: **letter + number + optional suffix.** Examples: `L2`, `S-4a`, `G1`.

Letters are *works letters*, assigned by construction, not by compass. The player
learns them as a small vocabulary:

| Letter | Room | Role |
| --- | --- | --- |
| **G** | Gauge Gallery | the hub |
| **L** | Tidal Lightwell | the set piece |
| **S** | Sluice Run | the main loop route |
| **P** | Pump Chapel | optional branch and dead end |
| **D** | Drainheads | vertical connections |
| **W** | Weir Walk | the high route |
| **B** | Basin Stair | the sealed lower route |

Numbers are the order the room was built, not the order the player meets it. A higher
number is not deeper and not further; it is later. The office's own corrections use the
same numbers, which is why a room can be `S-9` in one record and `S-11` in another: the
building was renumbered, the paint was not.

Suffix `a` / `b` is the two ends of one loop. No loop is ever given a new number. A
single route is written solid (`S4`); a loop takes a hyphen before its suffix
(`S-4a`, `S-4b`) so the two ends sort together on a plate and in a ledger.

A code is *valid* if it appears on a transom and on at least one pace plate. A code
that appears only on a wall is a survivor of an older scheme and may point at a room
that has moved, flooded or been renumbered.

### 2.3 Valve codes

`V-07`, `V-12A`. Stencil 60 mm, on the pipe, 300 mm upstream of the wheel. A branch
letter where one valve has two wheels (upstream and downstream). **The wheel is never
tagged.** A tagged wheel is a replacement and will not fit its valve; the tag left on
the pipe is how the player reads a missing wheel.

Valve codes are the only codes that never use a room letter. The pipe does not care
which room it is in.

### 2.4 Sluice numbers

Cast into the frame, 100 mm, upstream face, numbers 1–12 in construction order. The
downstream face repeats the number with a `D` (`7D`) if the door was hung to be passed
both ways.

| What is on the frame | What it means |
| --- | --- |
| Number on both faces | two-way; the door is part of a loop |
| Number on one face only | one-way; the blank face was hung later |
| Two different numbers | the door was rehung in another frame — the shortcut tell |
| No number | not a door, whatever the handle says |

The number is on the frame, never on the leaf. A number on the leaf is a replacement
leaf, and it fits the wrong frame.

Sluice 1 is the datum. **Works Zero is its sill**, not the cistern floor.

### 2.5 Gauges

Four kinds, all read at a glance:

- **Staff gauge.** Painted rule, 2 m, black on white, 0.2 m ticks, figures every metre.
  Zero at the sill of Sluice 1. Marks: `+2.40` high water, painted by hand, never
  repeated; `+1.95` and `+1.60`, scratched and crossed out, labelled by the office but
  not painted over.
- **Float gauge.** Brass scale in a stilling well, wooden float, pointer. It clacks
  when the float hits its stop (cue `G`, `SOUND-CUES.md` §2). The pointer lies by
  10 mm, and the label says so.
- **Tide board.** At the Lightwell. Sliders, a chalk line, a written prediction. The
  prediction is for yesterday. The tide does not use the board.
- **Door gauge.** One red tick at the foot of each sluice for every flood that reached
  it. Ticks are not dated and never removed. A door with three ticks has been under
  three times; the schedule records one.

The office paints heights. The growth scratches them. The office labels the scratches;
it does not paint over them. That is the closest the two recorders come to agreement.

### 2.6 Pace plates

`M-L2 — NEXT PLATE 40 PACES — LAMP 12`. Enamel, green on cream, knee height, three
screws with one missing. Measured at low water. **At high water add one pace per
flooded step.** The plate is accurate; the route is longer.

A missing plate means the route was re-measured and the old plate was taken down, which
means someone still walks it. A plate with a new screw is a plate that was moved
without re-measuring.

---

## 3. Reading order at a junction

The order is fixed, and the level teaches it in the first two rooms:

1. **Lamp.** A lit transom — steady or flickering — is the only thing in the level that
   means *exit*.
2. **Code.** Read the code under it. If the same code appears with another suffix, it
   is the same run: the player has closed a loop, not found a new route.
3. **Datum.** A chevron with `-1 LEVEL` or `+2 LEVEL` is a vertical connection. The
   number is relative to Works Zero, not to the player.
4. **Pace plate.** The only sign that tells the player the route is long. Trust the
   plate, not the count.
5. **Arrow, last.** Identify the scheme before following one. Chevron = works.
   Double-line = Descent Works (old stair, optional room). Tick = Gauge Office (the
   safe side is the side without the tick).

The first ninety seconds of the slice should teach this without a tutorial:

- the first door into the hub is lit and says `G1`, so code = destination;
- the first loop shows `S-4a`, then `S-4b`, so suffix = same run;
- the first shortcut shows a near plate, a shut door and a lit far transom through the
  gap, so lit = usable, and the far side can be the lit side;
- the first optional room has a department plate and no code, so absence = optional;
- the first dead end has a dim courtesy lamp and a barred code, so dim ≠ exit.

---

## 4. Rules for the generator (W1–W17)

Each rule is a constraint on placement, not a style note. A level that breaks one of
W1–W6 is unreadable; a level that breaks W7–W17 is merely unfair.

**W1 — Every exit carries a lit transom.** A door with a transom plate and a lit lamp —
steady or flickering — is an exit to the code on the plate. A door without one is not an
exit, even if it opens. The generator may make a non-exit door openable. It may not
light it.

**W2 — The lamp state is the route state.** Steady = maintained. Flicker = contested;
enemies use it too. Dark, clean = maintained but unfunded; usually optional or dead.
Dark, dust = sealed; the plate is a survivor.

**W3 — Loops repeat one code with two suffixes.** The two ends of a loop carry the same
letter and number, suffixed `a` and `b` (`S-4a`, `S-4b`). No loop gets a new number. A
player who sees the same code twice has closed the loop.

**W4 — Shortcuts are plated on both faces, lit on one.** The near face says the door is
shut and where the wheel is; the far face says it is open. Only the far transom is lit.
The near plate is the only sign in the level that tells the player a route exists that
they cannot use yet.

**W5 — Dead ends carry a barred code and a courtesy lamp.** The code is boxed and
struck through (`S-9 ⊘`); one dim lamp at the turn, no transom. The dim lamp is for the
inspection station, not a pull. Dim and steady must never be the same asset.

**W6 — Optional rooms carry no route code.** A department plate only (`GAUGE STATION
3`, `PUMP CHAPEL`). The absence of a code is the signal. Never print the word
OPTIONAL.

**W7 — Vertical connections carry a depth datum.** Chevron plus `-1 LEVEL` / `+2 LEVEL`,
relative to Works Zero, and the gauge height at the landing. Never relative to the
player; never "up" alone.

**W8 — Water depth is measured from the level line, not the floor.** `DEPTH AT THE
LINE 0.6 M`. The tag stays true when the water moves; a repainted tag means the level
has moved.

**W9 — Danger is a red tide tick, not a word.** The Gauge Office's tick on a gauge
means the water has been there; on a door, it means it will be. `DANGER` may accompany
a tick. It never replaces one.

**W10 — Valve codes live on the pipe, not the wheel.** 300 mm upstream, 60 mm stencil.
A tagged wheel is a replacement; it must read as one.

**W11 — Arrows end at fixtures.** Every arrow terminates within 2 m of a valve, lamp,
plate or door. No arrow in open floor. No arrow pointing at a room's far wall.

**W12 — The three arrow grammars disagree on purpose.** Works chevrons follow the
maintained route. Descent Works double-lines point at the old stair sockets, which mark
optional rooms and vertical loops. Gauge Office ticks mark the side the water came
from, which is the safe side. Where they disagree, the older scheme wins (W13).

**W13 — Repaints stack; the old plate outranks the new.** New plates mount above old;
nothing is removed. When two plates disagree, the lower and older one is the true route
and the upper one is the office's correction. The generator may use the correction as a
decoy only in rooms flagged `contested`.

**W14 — Each hub has one painted plan, wrong in one detail.** Per seed, exactly one: a
door that is not there, a route drawn one bay longer, a stair that rises the wrong way.
The error is consistent for the whole run. It is the run's tell, and it is the only
place where the level's own map is allowed to be wrong.

**W15 — Signs name water, routes, valves, hours and the office. Nothing else.** No
threats, no creatures, no failures, no persons. Anything else is graffiti: not lit, not
maintained, never over a transom. The generator must not promote graffiti to signage.

**W16 — One readable sign per 8 m; three deep at a junction, read bottom-up.**
Character budget: 28 per stencil line, 2 lines on a door plate, 4 on a wall plate. If a
string needs more, it is a notice, and notices go on a hook, not a wall.

**W17 — The shortcut's far light is visible before the near plate is readable.** The
player sees the lit transom through the gap or under the door before they can read why
the near side is shut. The light is the pull; the plate is the explanation. A shortcut
whose far light is not visible from the near side is a secret, not a wayfinding object.

### Generator contract

Fields the level generator needs to guarantee the rules. Strings come from §5 plus code
substitution; the generator does not invent stencil text.

```
exit:        { code, transom: steady|flicker|dark_clean|dark_dust }
loop:        { code, ends: [ {edge, suffix: a}, {edge, suffix: b} ] }
shortcut:    { near_plate, far_plate, far_transom: lit, near_transom: none }
dead_end:    { code, barred: true, courtesy_lamp: dim }
optional:    { department_plate, route_code: null }
vertical:    { datum: -2..+2, landing_gauge, chevron }
valve:       { code, pipe_offset_mm: 300, wheel_tagged: false }
sluice:      { number: 1..12, faces: [U,D] | [U], moved: false }
gauge:       { kind: staff|float|tide|door, zero: sluice_1_sill, marks: [...] }
pace_plate:  { code, paces, lamp_no, missing_screw: true }
plan_error:  { type: door|length|stair, detail, seed_fixed: true }
```

Placement guarantees the solver must also hold:

- no dead end within two rooms of the hub;
- every loop's two ends are both reachable before the shortcut opens;
- every optional room hangs off a route that already has a lit transom;
- every vertical connection has a gauge at its top landing, not its bottom;
- the first exit from any room is never a dead end.

---

## 5. Forty sign strings

Tags are for the generator, not for the wall. `▸` is the works chevron; `⊘` is the
barred box. Both are decals, not characters. Split at the em dash for two-line plates.

### Exit (7)

| # | String | Function |
| --- | --- | --- |
| 1 | `▸ L2 — TIDAL LIGHTWELL — -1 LEVEL` | exit |
| 2 | `▸ G1 — GAUGE GALLERY — HUB` | exit |
| 3 | `▸ S4 — SLUICE RUN — KEEP TO THE WALL` | exit |
| 4 | `▸ P2 — PUMP CHAPEL — DO NOT STOP THE PUMP` | exit |
| 5 | `▸ D1 — DRAIN HEAD — MIND THE LINE` | exit |
| 6 | `▸ W3 — WEIR WALK — UP AND OVER` | exit |
| 7 | `▸ L1 — LIGHTWELL FOOT — FOLLOW THE RINGING` | exit |

### Hub (6)

| # | String | Function |
| --- | --- | --- |
| 8 | `G1 — ALL ROUTES — THE GAUGE IS CORRECT` | hub |
| 9 | `HUB — FOUR WAYS — ONE IS SHUT` | hub |
| 10 | `G1 — STAND STILL — THE FLOOR IS A FLOAT` | hub |
| 11 | `G1 — NO SCHEDULE AFTER THE HOUR` | hub |
| 12 | `ALL DEPARTMENTS REPORT AT G1` | hub |
| 13 | `G1 — DRY LANDING — LAMPS AT 12` | hub |

### Shortcut (7)

| # | String | Function |
| --- | --- | --- |
| 14 | `B1 — BASIN STAIR — SHUT THIS SIDE — WORKS ONLY` | shortcut |
| 15 | `SEALED FROM THE LOWER LANDING — GO ROUND` | shortcut |
| 16 | `DOOR OPENS FROM THE FAR SIDE — NOT FROM HERE` | shortcut |
| 17 | `V-9 BYPASS — SHUT — THE WHEEL IS BELOW` | shortcut |
| 18 | `DROP SHAFT — ONE WAY — LANDING 2` | shortcut |
| 19 | `S-4a THIS FACE — S-4b THE OTHER — ONE RUN` | shortcut |
| 20 | `SHORT ROUTE TO L2 — MAINTENANCE — LAMP 12` | shortcut |

### Dead end (6)

| # | String | Function |
| --- | --- | --- |
| 21 | `NO THROUGH ROUTE — GAUGE STATION ONLY` | dead end |
| 22 | `DEAD END — INSPECTION — DO NOT CALL` | dead end |
| 23 | `ROUTE ENDS — RETURN BY THE WAY YOU CAME` | dead end |
| 24 | `NO OUTLET — SUMP — SOUND ONCE` | dead end |
| 25 | `THE OLD STAIR IS NOT HERE — THE SOCKETS ARE` | dead end |
| 26 | `S-9 ⊘ — INSPECTION ONLY — 20 PACES` | dead end |

### Optional (6)

| # | String | Function |
| --- | --- | --- |
| 27 | `PUMP CHAPEL — NOT ON THE ROUTE` | optional |
| 28 | `GAUGE STATION 3 — UNMANNED — LAMP BURNING` | optional |
| 29 | `STORE ALCOVE — ISSUE BY PLATE ONLY` | optional |
| 30 | `INSPECTION GALLERY — NO SCHEDULE` | optional |
| 31 | `ORGAN LOFT — WORKS PERMISSION REQUIRED` | optional |
| 32 | `FLOOD MARK ROOM — READ ONLY — DO NOT SWEEP` | optional |

### Danger (4)

| # | String | Function |
| --- | --- | --- |
| 33 | `DANGER — FLUME DISCHARGE — DO NOT SOUND` | danger |
| 34 | `DANGER — LIVE VALVE — WHEEL UNDER PRESSURE` | danger |
| 35 | `DANGER — WATER RISES UNANNOUNCED — KEEP THE LINE` | danger |
| 36 | `DANGER — GRATE 6 — BOLTS UNDERNEATH` | danger |

### Water depth (4)

| # | String | Function |
| --- | --- | --- |
| 37 | `DEPTH AT THE LINE 0.6 M — SUMP 1.9 M` | water depth |
| 38 | `DEPTH 0.6 M — TIDE MARK BELOW KNEE` | water depth |
| 39 | `DEPTH 1.1 M — DO NOT CARRY THE LAMP LOW` | water depth |
| 40 | `DEPTH 2.9 M — SOUNDING PEG AT THE THIRD RING` | water depth |

Longest string: #35, 48 characters. It is a wall plate, which allows 32 characters per
line; #15 and #40 also need the wall-plate line. Door plates allow 28 and take the first
clause only (`DANGER — WATER RISES`). The `shortcut` tag covers loop markers and locked
bypasses; the generator reads the string, not the tag, to know which is which.

---

## 6. Worked room — G1, the Gauge Gallery

The hub, signed to the rules, as a check on the system:

- **Stair mouth, 1.2 m painted plan.** Four routes out. This seed's error: the S route
  is drawn one bay longer than it is. The plan is repainted, never corrected.
- **Four exits, four transoms, all lit.** `L2` steady, `S4` steady, `P2` flicker, `W3`
  steady. The flicker is the pump chapel: the route is maintained, and something else
  uses it too.
- **Four pace plates.** `M-L2 — 40 PACES — LAMP 12`; `M-S4 — 22 — LAMP 12`;
  `M-P2 — 60 — LAMP 9`; `M-W3 — 34 — LAMP 12`. The P2 transom flickers; the plate still
  says 9, because plates are not lamps.
- **One dark-clean plate, no code.** On the store alcove door off the S run: maintained,
  unfunded, not an exit. It is the example the player learns the fourth state from.
- **North wall, staff gauge.** Painted `+2.40`; scratched `+1.95` and `+1.60`, both
  crossed out. Water at `+1.95`, so the current line covers the bottom of the middle
  scratch and leaves the cross above it dry.
- **Hook beside the gauge, notice 51.** The gauge is correct. If the gauge disagrees
  with the water, report the water.
- **No optional plate in the hub.** The optional room hangs off S4; its department
  plate is at the branch, not here. The hub is for routes.
- **The B stair is not signed here.** Its plate is at the bottom of the S run, on the
  near face of a sealed door, and the near face is unlit. The far side is lit. The
  player will see the light before they can reach it (W17).

A player who can read this room can read the level. That is the test.

---

## 7. What this system refuses

- It never prints the word EXIT on a dead end.
- It never lights a door that does not go anywhere.
- It never uses a different lamp colour for "objective"; all transoms are the same
  warm white, and the only distinction is state.
- It never puts a sign where the player's lamp cannot reach it and the transom cannot
  light it.
- It never explains the water. The gauges record it; the signs route around it.
