# SOUND-CUES — the audible pulls, flooded cistern

**Status: PROPOSAL.** Words only; nothing rendered. This is the audible half of the
system in `WAYFINDING.md`: the transom plate says where the exit is, the cue says it is
there before the lamp is in sight. Acoustic targets come from
`nullrun-sound-bible-20261101/ROOMS.md` (vault 4.2 s, bay 2.4 s, corridor 2.0 s, shaft
3.0 s); priority classes follow `SFX-LIST.md`.

**The one rule.** A cue belongs to the exit, not the corridor. It is loudest at the
door and falls off behind the player. The player walks toward a cue that is already
there, never toward a sound that is chasing them.

---

## 1. How this level listens

- **Everything answers twice.** Direct sound, then the room's late bright tail off
  porcelain. The first arrival says *what*; the second, duller arrival says *where* —
  it comes off the far wall, so its delay and stereo image place the source.
- **Water carries high frequencies; masonry carries low.** The cistern floor is water,
  so a low cue reaches the boot before the ear. Use the floor for distance and the
  whistle for bearing.
- **The wayfinding layer owns the edges of the spectrum.** Cues live below 500 Hz
  (body, boom, pump) or above 6 kHz (shimmer, whistle, ballast). Enemy and weapon tells
  live in 1–4 kHz. The cue must survive a fight without becoming a tell.
- **Silence is a cue.** When a pump rests, the room's masking drops and the transom hum
  and gauge clack become audible. The gap is the instruction *listen now*.
- **One cue per threshold.** Layering two exit cues at one door makes both unreadable;
  a secondary room cue belongs deeper in the room.

---

## 2. The cue set

Each cue gives: what it sounds like, what it means, and the bearing it gives. `Bearing`
is the direction cue the level is allowed to rely on.

### T — Transom hum

**Sounds like.** A fluorescent ballast under a steel hood: 100 Hz with a 200 Hz
harmonic, dry, almost no tail. Around a corner the buzz arrives before the light does.
**Means.** A maintained exit, and the code above the door.
**Bearing.** Directly above the door. This is the only cue that is also a visible sign.
Through one wall at 8–12 m; 25 m in a vault.
**Stops when.** The lamp is switched off at the hub. The ballast then ticks for about
forty seconds (cue X).

### P — Pump 2

**Sounds like.** A double thump at 44 bpm: a heavy beat, then a lighter return beat a
dotted eighth later, with a valve tick at the top of the stroke. The return beat is
late by the length of the pipe run, not by a fault.
**Means.** P2 Pump Chapel; the pump is running and the route is wet.
**Bearing.** The thump is felt through the grating — low, omnidirectional, useful for
distance only. The valve tick is the bearing: high, narrow, from the cylinder head.
Follow the tick, not the thump.
**Range.** 60 m through masonry; 120 m through water.
**Stops when.** The 96-second cycle ends; the pump rests eight seconds. The rest is the
listening window.

### U — Pump 4, unlogged

**Sounds like.** The same double thump, half a beat out of phase, from a room with no
pump on the plan. It does not rest.
**Means.** An optional pump chapel and a dead end behind it. Not an exit.
**Bearing.** Same as P, but the tick is duller, as if heard through a door. It is.
**Stops when.** Never. It is still running when the player leaves the level.

### S — Sluice rush

**Sounds like.** A broadband hiss through a part-open gate, with a narrow whistle at
the lip. The whistle rises as the gate closes: a low whistle is a working sluice, a high
one is a door nearly shut. Over a weir crest the hiss gains a slap every four seconds.
**Means.** The S run; the sluice is passable at the low whistle, and the shortcut is
behind the high one. The weir slap is W3.
**Bearing.** The whistle carries; the hiss does not. The whistle's pitch also says which
side is upstream: upstream is quieter and lower.
**Range.** 40 m around two corners; the whistle survives one door.
**Stops when.** The gate is wound shut. The whistle climbs, cuts out, and the hiss
becomes a drip (cue D).

### R — Ringing pipe

**Sounds like.** A length of steel pipe struck once with a spanner, ringing a minor
third — two modes, the upper one slightly flat — with a long, thin tail.
**Means.** The maintenance route. The answer comes from the next plate down the route,
after a delay set by the pipe run.
**Bearing.** The delay is the distance; the pitch of the answer is the branch. The L
branch answers a fifth above; the S branch a fourth below; the hub answers at the same
pitch, dead and immediate, because the pipe is anchored there.
**Range.** The whole works, but only along the pipe.
**Stops when.** One answer. A second strike in the same room gets silence. Do not
explain.

### H1 — Hour bell, the Hymnodyne

**Sounds like.** A struck bronze note, once, from the transit above; it arrives through
the shaft with the highs gone and a long, dull tail.
**Means.** Up. The transit is connected to this shaft.
**Bearing.** Up the nearest shaft, not along the corridor. The note arrives slightly
late and from above.
**Range.** Everywhere below the transit; faintest in the Lightwell.
**Stops when.** One strike per hour.

### H2 — Second bell

**Sounds like.** The same note a fifth lower, arriving after the first, with a longer
tail and a slow beat against the first bell's tail.
**Means.** Down. The Lightwell or the basin stair is connected to this shaft.
**Bearing.** Down. The delay is one second per level on the seed's tuning, so the
interval is the depth. It is the level's metronome.
**Stops when.** One strike. On flagged seeds it answers *before* the first bell; that is
the run's single allowed lie, fixed at generation, never random.

### L — Lightwell surge

**Sounds like.** Water entering the well compresses the air above it: a low boom
(20–40 Hz) that is felt rather than heard, then a shimmer as the surface breaks under
the light. Period about ninety seconds.
**Means.** L; the well is filling and the column is about to move.
**Bearing.** The boom is omnidirectional. The shimmer's stereo image gives the bearing;
the air movement in the reverb tells you when the well is inhaling.
**Range.** The whole cistern; faintest at the basin stair.
**Stops when.** The well reaches its mark. The boom stops; the shimmer continues for six
seconds.

### G — Gauge clack

**Sounds like.** A wooden float in a stilling well hitting its stop: a dry clack, minor
third, once every twelve seconds.
**Means.** G1, the hub. The gauge gallery is the only room with a float well.
**Bearing.** Through the floor; the hub is above the water line, so the clack arrives
from below and to the side of the stair.
**Range.** 30 m; two rooms.
**Stops when.** The water is still. In a surge the float rides and the clack stops,
which is itself a warning.

### D — Drip

**Sounds like.** A bright plink into water with a short tail, or a duller plink onto
stone with a long tail.
**Means.** The room's volume and whether the floor is flooded. Not a route cue by
itself; a room-reader.
**Bearing.** The ratio of plink to tail tells you the size of the room before you enter
it. The pitch tells you the water's distance below the drip.
**Range.** One room.
**Stops when.** Never. It is the room.

### W — Wind in a dry shaft

**Sounds like.** A low tone at the shaft's standing wave, with a slow beat as the air
moves. A wet shaft adds a gurgle at the bottom.
**Means.** The D route; a dry shaft is an exit above the water, a wet shaft is a dead
end below it.
**Bearing.** Up is a rise in pitch as you climb; down is a fall. The pitch is the
shaft's length.
**Range.** The shaft and the room at its foot.
**Stops when.** The air stills. Then the shaft is closed somewhere above.

### F — Far door clang

**Sounds like.** A sluice leaf closing somewhere else: a flat metal clang with a short,
bright tail.
**Means.** A loop. The same clang heard from both sides with different delay is the same
door.
**Bearing.** None. It is a map cue, not a bearing.
**Range.** Two rooms.
**Stops when.** One clang per close.

### X — Dead ballast tick

**Sounds like.** A fluorescent ballast ticking as its capacitor discharges, with no hum.
**Means.** The transom is off. The door is real; the route is not maintained.
**Bearing.** Above the door, exactly where a live hum would be.
**Range.** 6 m.
**Stops when.** The capacitor empties, after about forty seconds.

### Q — The stop

**Sounds like.** The pump's rest, the gauge's still water, the sluice's gate wound shut.
The room's tail lengthens and the transom hum arrives.
**Means.** Listen now. The exit cue is audible in the gap.
**Bearing.** It removes masking; it adds no source.
**Stops when.** The pump restarts and the hum is masked again.

---

## 3. The four pulls, staged

### 3.1 The pump — P2

Place the pump so the player hears it two rooms before the chapel door: the thump
through the floor, the tick through the wall. The chapel transom is `P2`, flickering.
The pump rests every 96 seconds; in the rest, the gauge clack and the hub's hum arrive.
That alternation teaches the player to use the silence, which is the level's main
listening skill.

The unlogged Pump 4 is placed behind the optional chapel, half a beat out of phase.
It is never used to pull a player toward an exit. It is true — there is a room — and
that is enough.

### 3.2 Flowing water — the sluice run and the shortcut

At a working sluice, the gate stands a hand's width open: low whistle, steady hiss.
The player learns the whistle's pitch as a door state before they learn it as a
direction.

At the locked shortcut, water moves on the far side. The near side is silent. The player
hears the far-side rush through the door, low-passed and slightly late; the door is the
only thing between them and a running route. That asymmetry is the pull, and it agrees
with the near plate (`DOOR OPENS FROM THE FAR SIDE`). When the shortcut is opened from
the far side, the rush comes through the open door at full band, and the near room's
tail changes. The change is the reward.

### 3.3 The ringing pipe — the player's own cue

Hang a striker at the hub: a spanner on a chain, worn bright at the head. The pipe runs
the length of the works on bronze clips (Margins reuse; the clips are older than the
cistern). Strike it and it answers from the next plate down the route.

Placement rule: the pipe is available wherever the transom system is ambiguous — a
junction with a flickering lamp, a dark-clean optional branch, the near face of a
shortcut. It is never required. A player who never strikes it still has the transom
system; a player who does gets a second reading of the same level.

The answer is generated from the route graph, not from a fixed sound: delay is authored
per pipe run (0.4–1.2 s, longer run longer delay, rounded to 50 ms), pitch is the
branch interval. The pipe answers once per room. A second strike is silence. The
silence is not a bug and is never explained in text.

### 3.4 Distant bells — up and down

The hour bell is the transit's; the second bell is the cistern's answer. The interval
between them is the depth, one second per level on the seed's tuning. The player learns
the interval at the hub, where both are audible, and then uses it in the shafts, where
only the tails survive.

At the Lightwell, the second bell and the surge coincide on the hour. That coincidence
is the set piece's downbeat: the bell, the boom, the shimmer, then the water moves. Do
not add music; the coincidence is the music.

On flagged seeds the second bell answers first. The lie is fixed at generation and
never varies within a run. It is the only cue allowed to be wrong, and it is wrong in
the same direction every hour, so a player can learn it.

---

## 4. Direction table

The question the player is actually asking, the cue that answers it, and what the cue
gives.

| Player's question | Cue | What it gives |
| --- | --- | --- |
| Where is the nearest exit? | T, lit | bearing within 8 m, through one wall |
| Which way is the hub? | G + T | the hub is the only float well; follow the clack |
| Which way is down? | H2, W | down; the wind shaft's pitch falls as you descend |
| Which way is the Lightwell? | L shimmer | bearing; the boom gives distance |
| Is this the loop I was on? | F, heard twice | map confirmation, no bearing |
| Is that door a shortcut? | S on the far side | yes, and it is open from there |
| Is that door sealed? | X, no hum | the lamp is off; the route is not maintained |
| Is this room optional? | no exit cue, only room tone | yes; the absence is the sign |
| Is the water rising? | G rate, S whistle pitch | time, not direction |
| Where did the masking go? | Q: the pump's rest | listen now; the transom hum is audible |

---

## 5. Placement rules

1. **One exit cue per exit, at the door.** Never a cue in the middle of a corridor.
2. **Audible from the room, not only from the threshold.** Test at the room's centre
   with combat at full level: if the cue is inaudible, move it onto the threshold.
3. **Never a lure into an unavoidable fight.** If the route crosses a fight, the cue
   ducks during combat and returns on the last kill. The return is the reward.
4. **Cues do not lie**, except H2's phase on flagged seeds. U is not a lie: there is a
   room.
5. **R is the only cue the player can operate.** It must never be required.
6. **Every route has one silent stretch of 6–10 m before its exit**, so the transom hum
   arrives as a change, not a constant.
7. **Space pipe strikes at least one tail apart.** The vault tail is 4.2 s; a strike
   closer than 8 m to its own answer smears both.
8. **Low cues are for distance, high cues for bearing.** Do not try to make a 40 Hz boom
   directional; do not try to make a 9 kHz shimmer carry through a wall.

---

## 6. What not to do

- **No whispered directions.** The inhabitants do not give directions, and their
  writing is never a route cue.
- **No music sting on entering a route.** The route cue is the music.
- **No sound behind an unopenable door that the player is meant to follow.** A sound
  behind a sealed door is a promise; if the door never opens, it is a broken one.
- **No random variation that changes meaning.** Timbre and timing are fixed per route
  per seed. A player must be able to learn the level's ear.
- **No cue that only exists in the mix.** If it cannot be heard on a television speaker
  at the target loudness, it is not a wayfinding cue; it is decoration.

---

## 7. Cue sheet by route

| Route | Primary exit cue | Secondary | Silent approach |
| --- | --- | --- | --- |
| **G1** Gauge Gallery | G clack | T hum | 6 m |
| **L2** Tidal Lightwell | L shimmer | H2 | 8 m |
| **S4** Sluice Run | S whistle | F clang | 6 m |
| **P2** Pump Chapel | P tick | U, off the optional branch | 10 m |
| **D1** Drain Head | W shaft tone | D drip | 6 m |
| **W3** Weir Walk | S rush + four-second slap | H1 above | 8 m |
| **B1** Basin Stair | H2, late | none (sealed route) | 10 m |
