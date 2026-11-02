#!/usr/bin/env python3
"""validate_library.py - validate chunk_library.json (standard library only).

Checks (per the brief):
  - every socket lies on its footprint boundary with a normal facing out;
  - socket widths >= 128 u; headroom >= 60 u at every socket and in the room;
  - stair risers within the step rules (<= 24 u) and covered vertical links;
  - footprints are simple polygons;
  - pillars/baffles inside the footprint; mechanism/encounter consistency;
  - prints a per-tag census.
"""
import json, math, sys
from pathlib import Path

ALLOWED_TAGS = {"room", "corridor", "tunnel", "stair", "hub",
                "set_piece", "harvested", "junction", "dead-end"}
NORMALS = {0: (1.0, 0.0), 90: (0.0, 1.0), 180: (-1.0, 0.0), 270: (0.0, -1.0)}
MIN_SOCKET_W = 128.0
MIN_HEADROOM = 60.0
MAX_RISER = 24.0
MECH_KEYS = {"valve", "gate", "shortcut", "lift", "one_way_drop", "portal_anchor"}
EPS = 1e-6

# ---------- geometry helpers ----------
def cross(o, a, b):
    return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])

def segs_proper_intersect(a, b, c, d):
    """Proper (interior) intersection of segments a-b and c-d."""
    def on(o, p, q):  # o strictly between p and q (collinear)
        return (min(p[0],q[0]) < o[0] < max(p[0],q[0]) or
                min(p[1],q[1]) < o[1] < max(p[1],q[1]))
    d1, d2, d3, d4 = cross(c, d, a), cross(c, d, b), cross(a, b, c), cross(a, b, d)
    return ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)) and (d1 and d2 and d3 and d4) or (
        d1 == 0 and on(a, c, d) or d2 == 0 and on(b, c, d) or
        d3 == 0 and on(c, a, b) or d4 == 0 and on(d, a, b))

def dist_point_seg(p, a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]
    L2 = dx*dx + dy*dy
    if L2 < EPS:
        return math.hypot(p[0]-a[0], p[1]-a[1])
    t = max(0.0, min(1.0, ((p[0]-a[0])*dx + (p[1]-a[1])*dy) / L2))
    return math.hypot(p[0]-(a[0]+t*dx), p[1]-(a[1]+t*dy))

def point_in_poly(p, poly):
    """Ray cast; boundary counts as inside."""
    x, y = p
    for i in range(len(poly)):
        a, b = poly[i], poly[(i+1) % len(poly)]
        if dist_point_seg(p, a, b) < 0.5:
            return True
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]; xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj-xi)*(y-yi)/(yj-yi) + xi:
            inside = not inside
        j = i
    return inside

# ---------- checks ----------
def check_simple_polygon(poly, ctx):
    n = len(poly)
    if n < 3:
        raise ValueError(f"{ctx}: footprint has fewer than 3 vertices")
    if any(len(v) != 2 or not all(isinstance(c, (int, float)) for c in v) for v in poly):
        raise ValueError(f"{ctx}: bad vertex format")
    # no zero-length or duplicate consecutive edges
    for i in range(n):
        a, b = poly[i], poly[(i+1) % n]
        if math.hypot(b[0]-a[0], b[1]-a[1]) < EPS:
            raise ValueError(f"{ctx}: degenerate edge at {a}")
    for i in range(n):
        for j in range(i+1, n):
            if (j == i+1) or (i == 0 and j == n-1):
                continue
            if segs_proper_intersect(poly[i], poly[(i+1) % n], poly[j], poly[(j+1) % n]):
                raise ValueError(f"{ctx}: edges {i}-{i+1} and {j}-{j+1} intersect; footprint not simple")
    # nonzero area
    area = sum(poly[i][0]*poly[(i+1) % n][1] - poly[(i+1) % n][0]*poly[i][1] for i in range(n))
    if abs(area) < EPS:
        raise ValueError(f"{ctx}: zero-area footprint")

def socket_on_boundary(pos, width, normal, poly, ctx):
    nvec = NORMALS[normal]
    # the socket opening runs perpendicular to the normal
    tdir = (-nvec[1], nvec[0])
    half = width / 2.0
    a = (pos[0] - half*tdir[0], pos[1] - half*tdir[1])
    b = (pos[0] + half*tdir[0], pos[1] + half*tdir[1])
    best = None
    for i in range(len(poly)):
        e1, e2 = poly[i], poly[(i+1) % len(poly)]
        d = dist_point_seg(pos, e1, e2)
        if best is None or d < best[0]:
            best = (d, i, e1, e2)
    d, i, e1, e2 = best
    if d > 0.5:
        raise ValueError(f"{ctx}: socket centre {pos} is {d:.2f} u from the nearest footprint edge; must lie on the boundary")
    # centre must be interior to the edge (not a vertex)
    ex, ey = e2[0]-e1[0], e2[1]-e1[1]
    elen = math.hypot(ex, ey)
    t = ((pos[0]-e1[0])*ex + (pos[1]-e1[1])*ey) / (elen*elen)
    if t < 0.02 or t > 0.98:
        raise ValueError(f"{ctx}: socket centre sits at/near a polygon vertex")
    # the whole 128 u opening must stay on this edge
    for p in (a, b):
        tt = ((p[0]-e1[0])*ex + (p[1]-e1[1])*ey) / (elen*elen)
        if tt < -0.5/elen or tt > 1.0 + 0.5/elen:
            raise ValueError(f"{ctx}: socket opening overhangs the wall edge")
        if dist_point_seg(p, e1, e2) > 0.5:
            raise ValueError(f"{ctx}: socket opening leaves the wall line")
    # edge must be axis-aligned (all socket walls are)
    if abs(ex) > EPS and abs(ey) > EPS:
        raise ValueError(f"{ctx}: socket on a diagonal wall edge {e1}->{e2}; sockets must sit on axis-aligned walls")
    # normal must be perpendicular to the edge and point OUT of the footprint
    cand1 = (ey/elen, -ex/elen)
    cand2 = (-ey/elen, ex/elen)
    def close(u, v):
        return math.hypot(u[0]-v[0], u[1]-v[1]) < 1e-6
    if not (close(nvec, cand1) or close(nvec, cand2)):
        raise ValueError(f"{ctx}: socket normal {normal} deg is not perpendicular to its wall edge")
    probe = (pos[0] + 8.0*nvec[0], pos[1] + 8.0*nvec[1])
    if point_in_poly(probe, poly):
        raise ValueError(f"{ctx}: socket normal {normal} deg points INTO the footprint (probe is inside)")
    return True

def check_library(data, out=sys.stdout):
    errors = []
    def err(msg):
        errors.append(msg)
    if not isinstance(data, dict) or "templates" not in data:
        print("FATAL: library must be an object with a 'templates' list")
        return 1
    tpls = data["templates"]
    if not 24 <= len(tpls) <= 32:
        err(f"template count {len(tpls)} outside 24..32")
    ids = set()
    tag_census = {}
    connector_kinds = {}
    for t in tpls:
        ctx = t.get("id", "<?>")
        if t.get("id") in ids:
            err(f"{ctx}: duplicate id")
        ids.add(t.get("id"))
        if t.get("template_id") != t.get("id"):
            err(f"{ctx}: template_id must equal id")
        tags = t.get("tags")
        if not tags or not set(tags) <= ALLOWED_TAGS:
            err(f"{ctx}: tags {tags} empty or outside {sorted(ALLOWED_TAGS)}")
        for tag in tags:
            tag_census[tag] = tag_census.get(tag, 0) + 1
        ck = t.get("connector_kind")
        if ck:
            connector_kinds[ck] = connector_kinds.get(ck, 0) + 1
        for key in ("floor_z_u", "ceiling_z_u", "headroom_u", "light_level", "rarity_weight", "material"):
            if key not in t or t[key] is None:
                err(f"{ctx}: missing {key}")
        if not t.get("rarity_weight") or t["rarity_weight"] <= 0:
            err(f"{ctx}: rarity_weight must be > 0")
        lb = t.get("light_band")
        if not lb or len(lb) != 2 or lb[0] > lb[1]:
            err(f"{ctx}: light_band must be [min,max]")
        if t["ceiling_z_u"] - t["floor_z_u"] < MIN_HEADROOM - EPS:
            err(f"{ctx}: room headroom {t['ceiling_z_u']-t['floor_z_u']} < {MIN_HEADROOM}")
        poly = t.get("footprint_local_u")
        try:
            check_simple_polygon([tuple(v) for v in poly], ctx)
        except ValueError as e:
            err(str(e))
        poly = [tuple(v) for v in poly]
        # pillars inside
        for i, (x, y, r) in enumerate(t.get("pillars_local_xy_r") or []):
            if r <= 0:
                err(f"{ctx}: pillar {i} radius must be > 0")
            if not point_in_poly((x, y), poly):
                err(f"{ctx}: pillar {i} at {(x,y)} outside footprint")
        baff = t.get("baffle_local_seg")
        if baff:
            if len(baff) != 2 or any(len(p) != 2 for p in baff):
                err(f"{ctx}: baffle_local_seg must be [p1, p2]")
            else:
                for p in baff:
                    if not point_in_poly(tuple(p), poly):
                        err(f"{ctx}: baffle endpoint {p} outside footprint")
        # sockets
        sockets = t.get("sockets") or []
        if not sockets:
            err(f"{ctx}: template has no sockets")
        sids = set()
        for s in sockets:
            sctx = f"{ctx}.{s.get('id','<?>')}"
            if s["id"] in sids:
                err(f"{sctx}: duplicate socket id")
            sids.add(s["id"])
            pos = tuple(s["pos"]); normal = s["normal_deg"]; width = s["width_u"]
            if normal not in NORMALS:
                err(f"{sctx}: normal_deg {normal} not in 0/90/180/270")
            if width < MIN_SOCKET_W - EPS:
                err(f"{sctx}: width {width} < {MIN_SOCKET_W}")
            if not (t["floor_z_u"] - 0.5 <= s["floor_z_u"] <= t["ceiling_z_u"] + 0.5):
                err(f"{sctx}: floor_z {s['floor_z_u']} outside room floor..ceiling")
            try:
                socket_on_boundary(pos, width, normal, poly, sctx)
            except ValueError as e:
                err(str(e))
            ceil_at = s.get("ceiling_z_u", t["ceiling_z_u"])
            if ceil_at - s["floor_z_u"] < MIN_HEADROOM - EPS:
                err(f"{sctx}: headroom at socket {ceil_at - s['floor_z_u']} < {MIN_HEADROOM}")
        fl = {s["id"]: s["floor_z_u"] for s in sockets}
        # stairs
        stairs = t.get("stairs") or []
        for st in stairs:
            sctx = f"{ctx}.stairs({st.get('from_socket')}->{st.get('to_socket')})"
            for k in ("from_socket", "to_socket", "risers", "rise_per_riser_u"):
                if k not in st:
                    err(f"{sctx}: missing {k}")
                    continue
            if st["from_socket"] not in fl or st["to_socket"] not in fl:
                err(f"{sctx}: unknown socket")
                continue
            if not isinstance(st["risers"], int) or st["risers"] < 1:
                err(f"{sctx}: risers must be a positive integer")
                continue
            if st["rise_per_riser_u"] > MAX_RISER + EPS:
                err(f"{sctx}: riser {st['rise_per_riser_u']} exceeds {MAX_RISER}")
            total = st["risers"] * st["rise_per_riser_u"]
            diff = abs(fl[st["to_socket"]] - fl[st["from_socket"]])
            if abs(total - diff) > 0.5:
                err(f"{sctx}: total rise {total} != socket floor delta {diff}")
        # vertical links
        vlinks = t.get("vertical_links") or []
        covered = set()
        for vl in vlinks:
            sctx = f"{ctx}.vlink({vl.get('from_socket')}->{vl.get('to_socket')})"
            if vl.get("kind") not in ("stair", "lift", "drop"):
                err(f"{sctx}: kind must be stair|lift|drop")
            if vl["from_socket"] not in fl or vl["to_socket"] not in fl:
                err(f"{sctx}: unknown socket")
                continue
            delta = fl[vl["to_socket"]] - fl[vl["from_socket"]]
            if abs(delta - vl.get("delta_z_u", 0)) > 0.5:
                err(f"{sctx}: declared delta {vl.get('delta_z_u')} != socket floor delta {delta}")
            covered.add(frozenset((vl["from_socket"], vl["to_socket"])))
            if vl["kind"] == "stair" and not stairs:
                err(f"{sctx}: stair vertical link with no stairs entries")
        # any socket pair whose floor differs by more than a step needs a vertical link
        for i in range(len(sockets)):
            for j in range(i+1, len(sockets)):
                a, b = sockets[i], sockets[j]
                if abs(a["floor_z_u"] - b["floor_z_u"]) > MAX_RISER + EPS:
                    if frozenset((a["id"], b["id"])) not in covered:
                        err(f"{ctx}: sockets {a['id']}/{b['id']} differ by "
                            f"{abs(a['floor_z_u']-b['floor_z_u'])} u with no stair/lift/drop link")
        # mechanisms
        mechs = t.get("mechanisms") or {}
        if not set(mechs) <= MECH_KEYS:
            err(f"{ctx}: unknown mechanism keys {set(mechs)-MECH_KEYS}")
        if "lift" in mechs and not any(v.get("kind") == "lift" for v in vlinks):
            err(f"{ctx}: lift mechanism without a lift vertical link")
        if "one_way_drop" in mechs and not any(v.get("kind") == "drop" for v in vlinks):
            err(f"{ctx}: one_way_drop mechanism without a drop vertical link")
        # encounter consistency
        enc = t.get("encounter") or {}
        suit = enc.get("suitability")
        if suit == "hollow_redead_bay":
            if not enc.get("convergence") or len(sockets) < 3:
                err(f"{ctx}: hollow_redead_bay must sit at a convergence (>= 3 sockets)")
        if suit == "armature_ambush":
            if not enc.get("sound_before_sight") or not baff:
                err(f"{ctx}: armature_ambush needs sound_before_sight and a baffle bend")
    # census
    out.write("=== per-tag census ===\n")
    for tag in sorted(tag_census):
        out.write(f"  {tag:12s} {tag_census[tag]}\n")
    set_pieces = tag_census.get("set_piece", 0)
    connectors = tag_census.get("corridor", 0) + tag_census.get("tunnel", 0) + tag_census.get("stair", 0)
    junctions = tag_census.get("junction", 0)
    out.write(f"  templates: {len(tpls)}  set_pieces: {set_pieces}  connectors: {connectors}  junctions: {junctions}\n")
    if connector_kinds:
        out.write(f"  connector kinds: {dict(connector_kinds)}\n")
    if set_pieces < 6:
        err(f"fewer than 6 set pieces ({set_pieces})")
    if connectors < 6:
        err(f"fewer than 6 connectors ({connectors})")
    if junctions < 4:
        err(f"fewer than 4 junctions ({junctions})")
    out.write("=== result ===\n")
    if errors:
        for e in errors:
            out.write("FAIL: " + e + "\n")
        out.write(f"VALIDATION FAILED with {len(errors)} error(s)\n")
        return 1
    out.write("VALIDATION PASSED\n")
    return 0

def main():
    path = Path(__file__).resolve().parent / "chunk_library.json"
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
    data = json.loads(path.read_text())
    sys.exit(check_library(data))

if __name__ == "__main__":
    main()
