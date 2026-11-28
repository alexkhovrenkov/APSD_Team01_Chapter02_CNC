"""2.5D (prismatic) analysis of an evaluated Onshape B-rep for milling (APSD-MILLING).

Input: the getPartStudioBodyDetails response (``07_bodydetails.json``) saved by the
vendored Chapter 1 extractor. Documented unit: metres; everything here is reported in mm.

What is CAD_EXTRACTED (read directly from the B-rep, only converted m -> mm):
  plane origins/normals, cylinder radii/axes/origins, torus radii, edge arcSweep,
  edge start/quarter/mid/end points, face areas and face bounding boxes.
What is GEOMETRICALLY_INFERRED (computed by this module from those values):
  the tool axis, height levels and the side they face, the section loops of every height
  band, the void/material side of each loop, feature types (hole, bore with slot,
  window/pocket, pin, boss, outer contour), circular patterns, distances, thicknesses.

Observed conventions (checked on the live APSD-MILLING response of 2026-11-26):
  * face ``orientation`` (undocumented field): for a PLANE the outward normal is
    ``normal`` when true and ``-normal`` when false (top face z=+10 true, bottom face
    z=-10 false); for a CYLINDER true = convex (boss, pin), false = concave (bore).
    The Chapter 1 parser observed the same rule on 12/12 lathe cylinders.
  * circle edges carry ``geometry.arcSweep`` (radians); every edge carries start,
    quarter, mid and end points.

Method (the way a 2.5D CAM system builds machining regions):
  1. Tool axis = the direction shared by the largest area of planes (by normal) and
     cylinders/tori (by axis). The part is "2.5D" if every curved face is parallel to it
     and every plane is perpendicular or parallel to it.
  2. Levels = planes perpendicular to the axis, grouped by height and facing side
     (up-facing -> reachable from the +axis setup, down-facing -> from the other side).
  3. The heights of the levels split the part into BANDS. Each band is sliced at its
     mid-height: for every wall face (cylinder parallel to the axis, plane containing it)
     the face's edge loops are mapped to its (angle, height) or (length, height)
     parameter space and intersected with the slice line (even-odd rule). This gives
     the exact arcs/segments of that face at that height, even when one face (a boss
     cylinder) bounds several regions.
  4. The section curves are chained into closed loops by matching end points.
     Containment depth decides the side: even depth = material boundary, odd = void.
  5. Loop typing: single full circle (material) = pin/boss; single full circle (void)
     = hole; void with a >=300 deg arc plus planar walls = bore with slot/keyway; other
     void = window or pocket (floor/ceiling checked against the level faces); other
     material = outer contour. Identical loops in neighbouring bands are merged.
"""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any

FILE = "07_bodydetails.json"
ANALYTIC = {"PLANE", "CYLINDER", "CONE", "TORUS", "SPHERE"}
COS_TOL = 1e-6
PT_TOL_M = 1e-5  # 0.01 mm: end-point matching when chaining section curves
TWO_PI = 2 * math.pi

LIMITATIONS = [
    "Only tool axes parallel to a world axis are analysed (true for the current model); an inclined axis "
    "is reported as an error, not guessed.",
    "Feature types (hole, bore with slot, window, pin, boss) are inferred from topology and geometry; the "
    "B-rep carries no manufacturing semantics (no tolerances, fits, surface finish, material, thread "
    "callouts). Those stay UNKNOWN unless a human annotation supplies them.",
    "Face 'orientation' is an undocumented Onshape field; its meaning is an observed convention.",
    "Curved edges are represented by their start, quarter, mid and end points when mapped to a face's "
    "parameter space; sections are exact for vertical side edges and approximate (piecewise linear) where a "
    "side edge is a blend curve. Slices are taken at band mid-heights, away from the R2 blends.",
    "Blends (tori) are reported separately as fillets and are not part of the section loops.",
    "Contour elements are CAD geometry, not toolpaths: entry points, direction, step-downs and cutter "
    "compensation are process decisions for the AI proposal and the human gates.",
]


# ---------------------------------------------------------------- helpers
def _v(d: dict | None) -> tuple[float, float, float] | None:
    if not d:
        return None
    return (float(d.get("x", 0.0)), float(d.get("y", 0.0)), float(d.get("z", 0.0)))


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _norm(a):
    return math.sqrt(_dot(a, a))


def _unit(a):
    n = _norm(a)
    return tuple(x / n for x in a) if n > 0 else a


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _parallel(a, b) -> bool:
    return abs(abs(_dot(_unit(a), _unit(b))) - 1.0) < COS_TOL


def _perp(a, b) -> bool:
    return abs(_dot(_unit(a), _unit(b))) < COS_TOL


def _mm(x_m: float) -> float:
    v = round(x_m * 1000.0, 4)
    return 0.0 if v == 0 else v


def _close2(a, b, tol=PT_TOL_M) -> bool:
    return abs(a[0] - b[0]) < tol and abs(a[1] - b[1]) < tol


class Frame:
    """World-aligned machining frame: h = height along the tool axis, (u, v) = the other two
    world axes in cyclic order (X, Y for a +Z axis). Coordinates stay in the Part Studio frame."""

    NAMES = "xyz"

    def __init__(self, axis):
        k = max(range(3), key=lambda i: abs(axis[i]))
        if abs(abs(axis[k]) - 1.0) > 1e-9:
            raise ValueError("tool axis is not parallel to a world axis")
        self.k, self.sign = k, (1.0 if axis[k] > 0 else -1.0)
        self.iu, self.iv = (k + 1) % 3, (k + 2) % 3
        self.axis = tuple(self.sign if i == k else 0.0 for i in range(3))
        self.axis_name = ("+" if self.sign > 0 else "-") + self.NAMES[k].upper()
        self.plane_names = (self.NAMES[self.iu].upper(), self.NAMES[self.iv].upper())

    def h(self, p) -> float:
        return self.sign * p[self.k]

    def uv(self, p) -> tuple[float, float]:
        return (p[self.iu], p[self.iv])


def _edge_samples(e: dict) -> list:
    g = e.get("geometry") or {}
    pts = [_v(g.get("startPoint"))]
    if str((e.get("curve") or {}).get("type")).upper() != "LINE":
        pts += [_v(g.get("quarterPoint")), _v(g.get("midPoint"))]
    pts.append(_v(g.get("endPoint")))
    return [p for p in pts if p]


def _is_full_circle(e: dict) -> bool:
    g = e.get("geometry") or {}
    return (str((e.get("curve") or {}).get("type")).upper() == "CIRCLE" and g.get("arcSweep") is not None
            and abs(float(g["arcSweep"]) - TWO_PI) < 1e-6)


def _chain(loop: dict, emap: dict) -> list | None:
    """Ordered 3D points of one face loop (edge directions fixed by end-point matching);
    None if the loop consists only of full-circle edges (a height bound of a cylinder)."""
    segs = [emap[ce["edgeId"]] for ce in loop.get("coedges") or [] if ce.get("edgeId") in emap]
    if segs and all(_is_full_circle(e) for e in segs):
        return None
    samples = [_edge_samples(e) for e in segs]
    pts: list = []
    n = len(samples)
    for i, s in enumerate(samples):
        if not pts:
            nxt = samples[(i + 1) % n] if n > 1 else s
            first_fwd = any(_close3(s[-1], q) for q in (nxt[0], nxt[-1]))
            pts.extend(s if first_fwd else s[::-1])
            continue
        last = pts[-1]
        if _close3(s[0], last):
            pts.extend(s[1:])
        elif _close3(s[-1], last):
            pts.extend(s[::-1][1:])
        else:
            pts.extend(s)
    return pts


def _close3(a, b, tol=1e-7) -> bool:
    return all(abs(x - y) < tol for x, y in zip(a, b))


def _crossings(poly: list[tuple[float, float]], h: float) -> list[float]:
    """Parameter values where the closed polygon (param, height) crosses height h."""
    xs = []
    for i in range(len(poly)):
        (s0, z0), (s1, z1) = poly[i], poly[(i + 1) % len(poly)]
        if (z0 - h) * (z1 - h) < 0:
            xs.append(s0 + (h - z0) / (z1 - z0) * (s1 - s0))
    return sorted(xs)


def _intervals_from_crossings(xs: list[float]) -> list[tuple[float, float]]:
    return [(xs[i], xs[i + 1]) for i in range(0, len(xs) - 1, 2)]


def _inside_poly2(pt, poly) -> bool:
    x, y = pt
    inside = False
    for i in range(len(poly)):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % len(poly)]
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            inside = not inside
    return inside


# ---------------------------------------------------------------- face sections
def _cyl_section(face: dict, emap: dict, fr: Frame, h_m: float) -> list[tuple[float, float]] | None:
    """Angular intervals (radians, CCW in the u-v plane) of a cylinder face at height h."""
    s = face["surface"]
    c = fr.uv(_v(s["origin"]))
    bounds, polys = [], []
    for lp in face.get("loops") or []:
        pts = _chain(lp, emap)
        if pts is None:
            bounds += [fr.h(_v((emap[ce["edgeId"]].get("geometry") or {}).get("startPoint"))) for ce in lp["coedges"]]
            continue
        th, prev = [], None
        for p in pts:
            u, v = fr.uv(p)
            a = math.atan2(v - c[1], u - c[0])
            if prev is not None:
                while a - prev > math.pi:
                    a -= TWO_PI
                while a - prev < -math.pi:
                    a += TWO_PI
            th.append((a, fr.h(p)))
            prev = a
        if abs(th[-1][0] - th[0][0]) > math.pi:  # loop winds around the cylinder: treat as a height bound
            bounds += [z for _, z in th]
            continue
        polys.append(th)
    base = bool(bounds) and min(bounds) - 1e-12 <= h_m <= max(bounds) + 1e-12
    loop_iv = []
    for poly in polys:
        for a, b in _intervals_from_crossings(_crossings(poly, h_m)):
            loop_iv.append((a, b))
    if not base and not loop_iv:
        return None
    cuts = {0.0}
    for a, b in loop_iv:
        cuts.update((a % TWO_PI, b % TWO_PI))
    cuts = sorted(cuts)

    def member(t: float) -> bool:
        m = base
        for a, b in loop_iv:
            tt = a + ((t - a) % TWO_PI)
            if tt <= b:
                m = not m
        return m

    pieces = []
    for i, a in enumerate(cuts):
        b = cuts[i + 1] if i + 1 < len(cuts) else TWO_PI
        if b - a > 1e-9 and member((a + b) / 2):
            pieces.append([a, b])
    if not pieces:
        return None
    if len(pieces) > 1 and pieces[0][0] == 0.0 and abs(pieces[-1][1] - TWO_PI) < 1e-12:  # join across 0
        pieces[0][0] = pieces[-1][0] - TWO_PI
        pieces.pop()
    merged = []
    for p in sorted(pieces):
        if merged and abs(p[0] - merged[-1][1]) < 1e-9:
            merged[-1][1] = p[1]
        else:
            merged.append(p)
    return [(a, b) for a, b in merged]


def _plane_section(face: dict, emap: dict, fr: Frame, h_m: float) -> list[tuple[tuple, tuple]] | None:
    """Segments (u-v end points, metres) of a wall plane at height h."""
    s = face["surface"]
    n = _unit(_v(s["normal"]))
    t = _unit(_cross(fr.axis, n))
    o = _v(s["origin"])
    iv = []
    for lp in face.get("loops") or []:
        pts = _chain(lp, emap) or []
        poly = [(_dot(tuple(p[i] - o[i] for i in range(3)), t), fr.h(p)) for p in pts]
        iv += _intervals_from_crossings(_crossings(poly, h_m)) if poly else []
    if not iv:
        return None
    o_uv, t_uv = fr.uv(o), fr.uv(t)
    return [((o_uv[0] + a * t_uv[0], o_uv[1] + a * t_uv[1]), (o_uv[0] + b * t_uv[0], o_uv[1] + b * t_uv[1])) for a, b in iv]


# ---------------------------------------------------------------- main entry
def analyse_prismatic(data: dict) -> dict:
    bodies = [(i, b) for i, b in enumerate(data.get("bodies") or []) if str(b.get("type", "")).upper() in ("SOLID", "")]
    out: dict[str, Any] = {"file": FILE, "solid_body_count": len(bodies)}
    if len(bodies) != 1:
        out["error"] = "expected exactly one solid body"
        return out
    bi, body = bodies[0]
    faces = body.get("faces") or []
    edges = body.get("edges") or []
    emap = {e.get("id"): e for e in edges}
    out.update({"body_index": bi, "body_id": body.get("id"), "face_count": len(faces), "edge_count": len(edges),
                "vertex_count": len(body.get("vertices") or [])})
    fptr = lambda fi: f"{FILE}#/bodies/{bi}/faces/{fi}"  # noqa: E731

    # ---- 1. tool axis ------------------------------------------------------------
    groups: list[dict] = []
    for f in faces:
        s = f.get("surface") or {}
        st = str(s.get("type", "")).upper()
        d = _v(s.get("normal")) if st == "PLANE" else _v(s.get("axis")) if st in ("CYLINDER", "CONE", "TORUS") else None
        if not d:
            continue
        for g in groups:
            if _parallel(d, g["dir"]):
                g["area"] += float(f.get("area") or 0)
                break
        else:
            groups.append({"dir": _unit(d), "area": float(f.get("area") or 0)})
    if not groups:
        out["error"] = "no planar or rotational faces"
        return out
    groups.sort(key=lambda g: g["area"], reverse=True)
    d0 = groups[0]["dir"]
    k = max(range(3), key=lambda i: abs(d0[i]))
    try:
        fr = Frame(tuple(1.0 if i == k else 0.0 for i in range(3)) if abs(abs(d0[k]) - 1) < 1e-9 else d0)
    except ValueError as exc:
        out["error"] = str(exc)
        return out
    d = fr.axis
    non_analytic = [fi for fi, f in enumerate(faces) if str((f.get("surface") or {}).get("type", "")).upper() not in ANALYTIC]
    curved_np, inclined = [], []
    for fi, f in enumerate(faces):
        s = f.get("surface") or {}
        st = str(s.get("type", "")).upper()
        if st in ("CYLINDER", "CONE", "TORUS") and not _parallel(_v(s["axis"]), d):
            curved_np.append(fi)
        if st == "PLANE" and not (_parallel(_v(s["normal"]), d) or _perp(_v(s["normal"]), d)):
            inclined.append(fi)
    out["tool_axis"] = {
        "direction": list(d), "name": fr.axis_name, "plane_axes": list(fr.plane_names),
        "basis": f"largest total face area sharing one direction ({groups[0]['area'] * 1e6:.1f} of "
                 f"{sum(g['area'] for g in groups) * 1e6:.1f} mm2, {len(groups)} direction groups)",
        "is_2_5d": not curved_np and not inclined and not non_analytic,
        "curved_faces_not_parallel": [fptr(i) for i in curved_np],
        "inclined_planes": [fptr(i) for i in inclined],
        "non_analytic_faces": [fptr(i) for i in non_analytic],
    }

    # ---- 2. envelope ----------------------------------------------------------------
    pts = [_v(v.get("point")) for v in body.get("vertices") or [] if v.get("point")]
    for f in faces:
        box = f.get("box") or {}
        if str((f.get("surface") or {}).get("type", "")).upper() in ANALYTIC and box.get("minCorner"):
            pts += [_v(box["minCorner"]), _v(box["maxCorner"])]
    lo = [_mm(min(p[i] for p in pts)) for i in range(3)]
    hi = [_mm(max(p[i] for p in pts)) for i in range(3)]
    out["envelope"] = {"min_mm": lo, "max_mm": hi, "size_mm": [round(hi[i] - lo[i], 4) for i in range(3)],
                       "basis": f"{len(faces) - len(non_analytic)} analytic face boxes + {len(body.get('vertices') or [])} vertices"}

    # ---- 3. levels, walls, blends --------------------------------------------------------
    levels_raw, walls, blends = [], {}, []
    for fi, f in enumerate(faces):
        s = f.get("surface") or {}
        st = str(s.get("type", "")).upper()
        ori = f.get("orientation")
        base = {"face_index": fi, "face_id": f.get("id"), "surface": st,
                "area_mm2": round(float(f.get("area") or 0) * 1e6, 3), "pointer": fptr(fi)}
        if st == "PLANE":
            n = _unit(_v(s["normal"]))
            out_n = n if ori else tuple(-c for c in n)
            if _parallel(n, d):
                polys = [[fr.uv(p) for p in (_chain(lp, emap) or [])] for lp in f.get("loops") or []]
                levels_raw.append({**base, "height_mm": _mm(fr.h(_v(s["origin"]))),
                                   "facing": "+" if _dot(out_n, d) > 0 else "-", "_polys": [p for p in polys if p]})
            elif _perp(n, d):
                walls[fi] = {**base, "kind": "plane", "outward_normal": [round(x, 6) + 0.0 for x in out_n],
                             "plane_point_mm": [_mm(x) for x in _v(s["origin"])]}
        elif st == "CYLINDER" and _parallel(_v(s["axis"]), d):
            r = float(s["radius"])
            sweeps = [math.degrees(float((emap[ce["edgeId"]].get("geometry") or {}).get("arcSweep")))
                      for lp in f.get("loops") or [] for ce in lp.get("coedges") or []
                      if ce.get("edgeId") in emap and str((emap[ce["edgeId"]].get("curve") or {}).get("type")).upper() == "CIRCLE"
                      and abs(float(emap[ce["edgeId"]]["curve"].get("radius", 0)) - r) < 1e-7
                      and (emap[ce["edgeId"]].get("geometry") or {}).get("arcSweep") is not None]
            walls[fi] = {**base, "kind": "arc", "radius_mm": _mm(r), "diameter_mm": _mm(2 * r),
                         "centre_mm": [_mm(c) for c in fr.uv(_v(s["origin"]))], "convex": bool(ori),
                         "edge_arc_sweeps_deg": sorted({round(x, 3) for x in sweeps})}
        elif st == "TORUS" and _parallel(_v(s["axis"]), d):
            blends.append({**base, "kind": "torus_blend", "fillet_radius_mm": _mm(float(s["minorRadius"])),
                           "sweep_circle_radius_mm": _mm(float(s["majorRadius"])),
                           "centre_mm": [_mm(c) for c in fr.uv(_v(s["origin"]))],
                           "height_mm": _mm(fr.h(_v(s["origin"]))), "concave": not bool(ori)})

    lv: dict[tuple, dict] = {}
    for p in levels_raw:
        g = lv.setdefault((p["height_mm"], p["facing"]), {"height_mm": p["height_mm"], "facing": p["facing"],
                                                          "total_area_mm2": 0.0, "faces": [], "_polys": []})
        g["total_area_mm2"] = round(g["total_area_mm2"] + p["area_mm2"], 3)
        g["faces"].append({"face_id": p["face_id"], "area_mm2": p["area_mm2"], "pointer": p["pointer"]})
        g["_polys"].append(p["_polys"])
    levels = sorted(lv.values(), key=lambda g: (-g["height_mm"], g["facing"]))
    other = ("-" if fr.sign > 0 else "+") + fr.axis_name[1]
    for g in levels:
        g["reachable_from"] = f"{fr.axis_name} side (top setup)" if g["facing"] == "+" else f"{other} side (opposite setup)"

    # ---- 4. bands and section loops ---------------------------------------------------
    heights = sorted({g["height_mm"] for g in levels})
    bands = []
    for b0, b1 in zip(heights, heights[1:]):
        hm = (b0 + b1) / 2 / 1000.0
        curves = []
        for fi, w in walls.items():
            f = faces[fi]
            if w["kind"] == "arc":
                ivs = _cyl_section(f, emap, fr, hm) or []
                c = [x / 1000 for x in w["centre_mm"]]
                r = w["radius_mm"] / 1000
                for a, b in ivs:
                    full = abs((b - a) - TWO_PI) < 1e-9
                    curves.append({"fi": fi, "kind": "arc", "full": full, "a0": a, "a1": b,
                                   "start": (c[0] + r * math.cos(a), c[1] + r * math.sin(a)),
                                   "end": (c[0] + r * math.cos(b), c[1] + r * math.sin(b)), "c": c, "r": r})
            else:
                for p0, p1 in _plane_section(f, emap, fr, hm) or []:
                    curves.append({"fi": fi, "kind": "line", "full": False, "start": p0, "end": p1})
        loops = _assemble(curves)
        if not loops:
            continue
        polys = [_loop_poly(lp) for lp in loops]
        recs = []
        for i, lp in enumerate(loops):
            probe = _sample_point(lp[0])
            depth = sum(1 for j, pg in enumerate(polys) if j != i and _inside_poly2(probe, pg))
            recs.append({"curves": lp, "poly": polys[i], "depth": depth, "void": depth % 2 == 1})
        bands.append({"range_mm": [b0, b1], "slice_height_mm": round((b0 + b1) / 2, 4), "loops": recs})

    # ---- 5. type loops, merge across bands ------------------------------------------------
    regions: dict[tuple, list] = defaultdict(list)  # identical loops in ADJACENT bands merge; others stay separate
    for band in bands:
        for rec in band["loops"]:
            key = (rec["void"], tuple(sorted({c["fi"] for c in rec["curves"]})), _sig(rec["curves"]))
            prev = regions[key][-1] if regions[key] else None
            if prev and abs(prev["height_span_mm"][1] - band["range_mm"][0]) < 1e-6:
                prev["height_span_mm"][1] = band["range_mm"][1]
                prev["bands"].append(band["range_mm"])
                continue
            regions[key].append({"_rec": rec, "height_span_mm": list(band["range_mm"]), "bands": [band["range_mm"]]})
    hmin, hmax = heights[0], heights[-1]
    out_loops = []
    for reg in (r for lst in regions.values() for r in lst):
        rec = reg["_rec"]
        t = _type_region(rec, walls, fr)
        t["height_span_mm"] = reg["height_span_mm"]
        t["bands_mm"] = reg["bands"]
        t["spans_full_part_height"] = abs(reg["height_span_mm"][0] - hmin) < 1e-6 and abs(reg["height_span_mm"][1] - hmax) < 1e-6
        if rec["void"]:
            probe = _void_probe(rec)
            t["interior_probe_mm"] = [_mm(probe[0]), _mm(probe[1])]
            b0, b1 = reg["height_span_mm"]
            floor = _level_contains(levels, b0, "+", probe)
            ceiling = _level_contains(levels, b1, "-", probe)
            t["floor_at_mm"] = b0 if floor else None
            t["closed_top_at_mm"] = b1 if ceiling else None
            t["open_both_ends"] = not floor and not ceiling
            if t["type"] == "window_or_pocket":
                t["type"] = "through_window" if t["open_both_ends"] else "pocket"
        out_loops.append(t)
    order = {"outer_contour": 0, "boss": 1, "pin": 2, "bore_with_slot": 3, "hole": 4, "through_window": 5, "pocket": 6}
    out_loops.sort(key=lambda t: (order.get(t["type"], 9), t["height_span_mm"][0], t["ref_centre_mm"]))
    for i, t in enumerate(out_loops):
        t["region_index"] = i
    for g in levels:
        g.pop("_polys", None)
    out["levels"] = levels
    out["height_range_mm"] = [hmin, hmax]
    out["bands"] = [{"range_mm": b["range_mm"], "slice_height_mm": b["slice_height_mm"],
                     "loop_count": len(b["loops"]), "void_loops": sum(1 for r in b["loops"] if r["void"])} for b in bands]
    out["regions"] = out_loops
    out["blends"] = sorted(blends, key=lambda b: (b["centre_mm"], b["height_mm"], b["face_id"]))
    out["patterns"] = _patterns(out_loops)
    out["limitations"] = LIMITATIONS
    return out


# ---------------------------------------------------------------- loop assembly
def _assemble(curves: list[dict]) -> list[list[dict]]:
    loops = [[c] for c in curves if c["full"]]
    rest = [c for c in curves if not c["full"]]
    used = [False] * len(rest)
    for i, c in enumerate(rest):
        if used[i]:
            continue
        used[i] = True
        chain = [dict(c, rev=False)]
        start, cur = c["start"], c["end"]
        for _ in range(len(rest)):
            if _close2(cur, start):
                break
            for j, d in enumerate(rest):
                if used[j]:
                    continue
                if _close2(d["start"], cur):
                    used[j] = True
                    chain.append(dict(d, rev=False))
                    cur = d["end"]
                    break
                if _close2(d["end"], cur):
                    used[j] = True
                    chain.append(dict(d, rev=True))
                    cur = d["start"]
                    break
            else:
                break
        if _close2(cur, start):
            loops.append(chain)
    return loops


def _curve_pts(c: dict, step_deg: float = 5.0) -> list[tuple[float, float]]:
    if c["kind"] == "line":
        pts = [c["start"], c["end"]]
    else:
        n = max(2, int(math.degrees(c["a1"] - c["a0"]) / step_deg) + 1)
        pts = [(c["c"][0] + c["r"] * math.cos(c["a0"] + (c["a1"] - c["a0"]) * i / n),
                c["c"][1] + c["r"] * math.sin(c["a0"] + (c["a1"] - c["a0"]) * i / n)) for i in range(n + 1)]
    return pts[::-1] if c.get("rev") else pts


def _loop_poly(lp: list[dict]) -> list[tuple[float, float]]:
    pts = []
    for c in lp:
        p = _curve_pts(c)
        pts.extend(p[:-1] if not c["full"] else p[:-1])
    return pts


def _sample_point(c: dict) -> tuple[float, float]:
    if c["kind"] == "line":
        return ((c["start"][0] + c["end"][0]) / 2, (c["start"][1] + c["end"][1]) / 2)
    a = (c["a0"] + c["a1"]) / 2
    return (c["c"][0] + c["r"] * math.cos(a), c["c"][1] + c["r"] * math.sin(a))


def _void_probe(rec: dict) -> tuple[float, float]:
    """A point inside a void loop: step 0.1 mm off the middle of its first curve, on the
    side that lies inside the loop polygon."""
    c = rec["curves"][0]
    p = _sample_point(c)
    if c["kind"] == "line":
        dx, dy = c["end"][0] - c["start"][0], c["end"][1] - c["start"][1]
        n = _unit((-dy, dx))
    else:
        n = _unit((p[0] - c["c"][0], p[1] - c["c"][1]))
    for sgn in (1, -1):
        q = (p[0] + sgn * 1e-4 * n[0], p[1] + sgn * 1e-4 * n[1])
        if _inside_poly2(q, rec["poly"]):
            return q
    return p


def _level_contains(levels: list[dict], h_mm: float, facing: str, pt) -> bool:
    for g in levels:
        if abs(g["height_mm"] - h_mm) < 1e-6 and g["facing"] == facing:
            for face_polys in g["_polys"]:
                if sum(1 for pg in face_polys if _inside_poly2(pt, pg)) % 2 == 1:
                    return True
    return False


def _sig(curves: list[dict]) -> tuple:
    return tuple(sorted((c["fi"], round(c["start"][0], 6), round(c["start"][1], 6)) for c in curves))


# ---------------------------------------------------------------- region typing
def _element(c: dict, walls: dict, fr: Frame) -> dict:
    w = walls[c["fi"]]
    s, e = (c["end"], c["start"]) if c.get("rev") else (c["start"], c["end"])
    el = {"face_id": w["face_id"], "pointer": w["pointer"], "start_mm": [_mm(s[0]), _mm(s[1])], "end_mm": [_mm(e[0]), _mm(e[1])]}
    if c["kind"] == "arc":
        el.update({"kind": "full_circle" if c["full"] else "arc", "radius_mm": w["radius_mm"], "diameter_mm": w["diameter_mm"],
                   "centre_mm": w["centre_mm"], "convex": w["convex"],
                   "sweep_deg": round(math.degrees(c["a1"] - c["a0"]), 3),
                   "direction_in_loop": ("CW" if c.get("rev") else "CCW") + " (viewed from the +axis side)"})
    else:
        el.update({"kind": "line", "length_mm": _mm(math.dist(s, e)), "outward_normal": w["outward_normal"],
                   "outward_normal_uv": [round(x, 6) + 0.0 for x in fr.uv(w["outward_normal"])]})
    return el


def _type_region(rec: dict, walls: dict, fr: Frame) -> dict:
    curves = rec["curves"]
    els = [_element(c, walls, fr) for c in curves]
    arcs = [e for e in els if e["kind"] in ("arc", "full_circle")]
    lines = [e for e in els if e["kind"] == "line"]
    single_full = len(els) == 1 and els[0]["kind"] == "full_circle"
    t: dict[str, Any] = {"side": "void" if rec["void"] else "material", "containment_depth": rec["depth"],
                         "side_basis": "even-odd containment of section loops (0/2/.. = material boundary, 1/3/.. = void)",
                         "elements": els}
    xs = [p[0] for p in rec["poly"]]
    ys = [p[1] for p in rec["poly"]]
    t["extent_mm"] = {"min": [_mm(min(xs)), _mm(min(ys))], "max": [_mm(max(xs)), _mm(max(ys))],
                      "axes": list(fr.plane_names)}
    if single_full:
        t["ref_centre_mm"] = els[0]["centre_mm"]
        t["type"] = "hole" if rec["void"] else "boss"
        return t
    t["ref_centre_mm"] = [round((t["extent_mm"]["min"][i] + t["extent_mm"]["max"][i]) / 2, 4) for i in range(2)]
    if rec["void"]:
        concave_corners = sorted({a["radius_mm"] for a in arcs if not a["convex"]})
        t["min_concave_radius_mm"] = concave_corners[0] if concave_corners else None
        big = [a for a in arcs if a["sweep_deg"] >= 300]
        if big and lines:
            t["type"] = "bore_with_slot"
            t["ref_centre_mm"] = big[0]["centre_mm"]
            t["slot"] = _slot(big[0], lines)
        else:
            t["type"] = "window_or_pocket"
    else:
        t["type"] = "outer_contour"
        t["min_concave_radius_mm"] = min((a["radius_mm"] for a in arcs if not a["convex"]), default=None)
    return t


def _slot(bore: dict, lines: list[dict]) -> dict:
    """Slot/keyway at a bore: two parallel walls whose outward normals face each other plus
    an end wall perpendicular to them."""
    res: dict[str, Any] = {"bore_diameter_mm": bore["diameter_mm"], "bore_centre_mm": bore["centre_mm"],
                           "walls": [ln["pointer"] for ln in lines]}

    def mid(ln):
        return ((ln["start_mm"][0] + ln["end_mm"][0]) / 2, (ln["start_mm"][1] + ln["end_mm"][1]) / 2)

    def n2(ln):
        return tuple(ln["outward_normal_uv"])

    best = None
    for i, a in enumerate(lines):
        for b in lines[i + 1:]:
            na, nb = n2(a), n2(b)
            if abs(na[0] * nb[0] + na[1] * nb[1] + 1) < 1e-6:
                ma, mb = mid(a), mid(b)
                dist = (mb[0] - ma[0]) * na[0] + (mb[1] - ma[1]) * na[1]
                if dist > 0 and (best is None or dist > best[2]):
                    best = (a, b, dist)
    if best:
        a, b, dist = best
        res["width_mm"] = round(dist, 4)
        res["width_basis"] = f"distance between the facing walls {a['face_id']} and {b['face_id']}"
        na = n2(a)
        ends = [ln for ln in lines if ln not in (a, b) and abs(n2(ln)[0] * na[0] + n2(ln)[1] * na[1]) < 1e-6]
        if ends:
            e, ne = ends[0], n2(ends[0])
            me = mid(e)
            dist_c = abs((me[0] - bore["centre_mm"][0]) * ne[0] + (me[1] - bore["centre_mm"][1]) * ne[1])
            res["end_wall_distance_from_bore_axis_mm"] = round(dist_c, 4)
            res["depth_beyond_bore_surface_mm"] = round(dist_c - bore["radius_mm"], 4)
            res["direction_from_bore_axis"] = [round(-ne[0], 6) + 0.0, round(-ne[1], 6) + 0.0]
    return res


def _patterns(regions: list[dict]) -> list[dict]:
    """Equal-diameter full-circle holes or pins arranged on a circle around the centre of a
    bore, hole or boss."""
    singles = [t for t in regions if t["type"] in ("hole", "boss") and len(t["elements"]) == 1]
    centres = sorted({tuple(t["ref_centre_mm"]) for t in regions if t["type"] in ("bore_with_slot", "hole", "boss")})
    by_kind: dict[tuple, list] = defaultdict(list)
    for t in singles:
        by_kind[(t["type"], t["elements"][0]["diameter_mm"], tuple(t["height_span_mm"]))].append(t)
    out = []
    for (kind, dia, span), items in sorted(by_kind.items()):
        if len(items) < 3:
            continue
        for c in centres:
            rs = [math.dist(c, it["ref_centre_mm"]) for it in items]
            if rs[0] > 1e-3 and max(rs) - min(rs) < 1e-3:
                angs = sorted(round(math.degrees(math.atan2(it["ref_centre_mm"][1] - c[1], it["ref_centre_mm"][0] - c[0])) % 360, 3)
                              for it in items)
                gaps = [round((angs[(j + 1) % len(angs)] - angs[j]) % 360, 3) for j in range(len(angs))]
                for it in items:
                    it["type"] = "pin" if kind == "boss" else it["type"]
                out.append({"element": "pin" if kind == "boss" else kind, "diameter_mm": dia, "count": len(items),
                            "pattern_centre_mm": list(c), "pitch_circle_diameter_mm": round(2 * rs[0], 4),
                            "angular_positions_deg": angs, "angular_gaps_deg": gaps,
                            "equally_spaced": max(gaps) - min(gaps) < 0.01, "height_span_mm": list(span),
                            "region_indices": [it["region_index"] for it in items]})
                break
    return out
