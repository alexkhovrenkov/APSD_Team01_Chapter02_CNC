"""Static checks of candidate NC programs for LatheLab / MillLab.

THIS IS NOT A SIMULATION. It reads the program text and flags structural problems for the
human G3 (code) gate. A clean result says nothing about the machined shape; only the
simulator (G4) can show that.

Dialect facts come from experiment_config/simulator_dialect.json (static reading of the
simulator source, 2026-11-26). Lathe programs follow LatheLab: X = DIAMETER, U/W are
incremental, G90/G92/G94 are BOX CYCLES (not absolute mode), G91 is not supported.

Severity classes (documented in evaluation_methodology.md):
  critical - the simulator would alarm/stop, or geometry is certainly wrong (no F on a feed
             move, arc without radius, unsupported G-code, inch units)
  major    - likely wrong part, collision risk or rejected by the gate (feed with spindle
             off, no tool selected, rapid inside the stock, diameter/radius sign error,
             arc radius mismatch, comp active at tool change)
  minor    - robustness/style issues the simulator tolerates (missing M30, comp not
             cancelled at end, G96 without G50, missing modal safe line)
  info     - observations (extents, cycles used, checks skipped)

Known limitation: blocks inside a G70-G73 profile (between P and Q) are checked as ordinary
moves, and the tool position after a cycle is not modelled.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .paths import DIALECT_PATH

WORD = re.compile(r"([A-Z])\s*([-+]?(?:\d+\.?\d*|\.\d+))")
SEVERITIES = ("critical", "major", "minor", "info")
LATHE_CYCLES = {70, 71, 72, 73, 74, 75, 76}
LATHE_BOX = {90, 92, 94}
MILL_CANNED = {73, 74, 76, 81, 82, 83, 84, 85, 86, 89}


def load_dialect(path: Path = DIALECT_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass
class Finding:
    severity: str
    line: int | None
    code: str
    message: str

    def to_dict(self) -> dict:
        return {"severity": self.severity, "line": self.line, "code": self.code, "message": self.message}


@dataclass
class State:
    units: str | None = None
    absolute: bool | None = None  # mill only
    motion: int | None = None
    feed: float | None = None
    feed_per_rev: bool | None = None
    spindle_on: bool = False
    s_word: float | None = None
    tool: int | None = None
    offset: int | None = None
    comp: int = 40
    len_comp: bool = False
    canned: int | None = None
    css: bool = False
    g50_limit: bool = False
    plane: int | None = None
    ended: bool = False
    g43_warned: bool = False
    pos: dict = field(default_factory=lambda: {"X": None, "Y": None, "Z": None})


def strip_comments(line: str) -> str:
    line = re.sub(r"\([^)]*\)", " ", line)
    return line.split(";")[0].upper().strip()


def check_program(text: str, dialect_name: str, dialect: dict | None = None, stock: dict | None = None) -> dict:
    """dialect_name: 'lathelab' | 'milllab'. stock (optional): lathe {'diameter','length'};
    mill {'size_x','size_y','size_z','z_top'} in the program's work frame."""
    dialect = dialect or load_dialect()
    d = dialect[dialect_name]
    lathe = dialect_name == "lathelab"
    sup_g = {float(x) for x in d["supported_g"]}
    sup_m = {int(x) for x in d["supported_m"]}
    st = State()
    f: list[Finding] = []
    ext: dict[str, list[float]] = {"X": [], "Y": [], "Z": []}
    cycles_used: set[str] = set()
    first_motion_line = None
    saw_safe_line = False
    code_lines = 0
    last_motion: tuple[int, int | None, dict] | None = None

    def add(sev, ln, code, msg):
        f.append(Finding(sev, ln, code, msg))

    lines = text.splitlines()
    for n, raw in enumerate(lines, 1):
        s = strip_comments(raw)
        if not s or s.startswith("%") or re.fullmatch(r"O\d+", s):
            continue
        s = re.sub(r"^N\d+\s*", "", s)
        words = WORD.findall(s)
        if not words:
            continue
        letters = [w[0] for w in words]
        dup = {c for c in letters if c not in "GM" and letters.count(c) > 1}
        if dup:
            add("critical", n, "duplicate_address", f"address {','.join(sorted(dup))} appears twice in one block")
        code_lines += 1
        if st.ended:
            add("minor", n, "code_after_end", "code after M30/M02 is never executed")
            st.ended = False
        gs = [round(float(v), 1) for c, v in words if c == "G"]
        ms = [int(float(v)) for c, v in words if c == "M"]
        w = {c: float(v) for c, v in words if c not in "GMN"}
        for g in gs:
            if g not in sup_g:
                add("critical", n, "unsupported_g", f"G{g:g} is not supported by {dialect_name} (simulator: error)")
        for m in ms:
            if m not in sup_m:
                add("minor", n, "unsupported_m", f"M{m:02d} is not supported by {dialect_name} (simulator: ignored)")
        if len([m for m in ms if m != 98]) > 1:
            add("minor", n, "multiple_m", "more than one M-code in a block")
        cycle_block = False
        for g in gs:
            gi = int(g)
            if gi == 20:
                st.units = "inch"
                add("critical", n, "inch_units", "G20 (inch) - the experiment uses mm (G21)")
            elif gi == 21:
                st.units = "mm"
            elif gi in (0, 1, 2, 3, 32):
                st.motion = gi
            elif gi in (17, 18, 19):
                st.plane = gi
                if gi == 17 and not lathe or gi == 18 and lathe:
                    saw_safe_line = True
            elif gi in (40, 41, 42):
                if gi in (41, 42) and not lathe and "D" not in w:
                    add("minor", n, "comp_without_d", f"G{gi} without D - the tool centre runs on the contour (simulator warning)")
                st.comp = gi
            elif gi == 43:
                st.len_comp = True
                if "H" not in w:
                    add("minor", n, "g43_without_h", "G43 without H - the previous H register is used")
            elif gi == 49:
                st.len_comp = False
            elif gi == 50 and lathe:
                if "S" in w:
                    st.g50_limit = True
            elif gi == 96 and lathe:
                st.css = True
                if not st.g50_limit:
                    add("minor", n, "css_without_limit", "G96 without a preceding G50 S.. spindle limit")
            elif gi == 97:
                st.css = False
            elif lathe and gi in (98, 99):
                st.feed_per_rev = gi == 99
            elif not lathe and gi in (94, 95):
                st.feed_per_rev = gi == 95
            elif not lathe and gi in (90, 91):
                st.absolute = gi == 90
            elif lathe and gi in LATHE_BOX:
                st.motion = gi
                cycles_used.add(f"G{gi}")
                if not any(a in w for a in "XZUW"):
                    add("major", n, "g90_as_absolute", f"G{gi} without X/Z/U/W: in LatheLab G{gi} is a BOX CYCLE, not absolute mode")
            elif lathe and gi in LATHE_CYCLES:
                cycle_block = True
                cycles_used.add(f"G{gi}")
            elif not lathe and gi in MILL_CANNED:
                st.canned = gi
                cycles_used.add(f"G{gi}")
                if "Z" in w and "R" in w and w["Z"] >= w["R"]:
                    add("critical", n, "canned_z_not_below_r", f"G{gi}: Z{w['Z']:g} is not below the R-plane R{w['R']:g}")
            elif not lathe and gi == 80:
                st.canned = None
            elif gi == 28 and st.comp != 40:
                add("major", n, "g28_with_comp", "G28 with cutter/nose compensation active - cancel with G40 first")
        if gs and any(int(g) == 40 for g in gs) and any(int(g) in (21, 20) for g in gs):
            saw_safe_line = True
        if "T" in w:
            t = int(w["T"])
            if lathe:
                st.tool, st.offset = (t // 100, t % 100) if t >= 100 else (t, 0)
                if st.offset == 0:
                    add("minor", n, "tool_offset_00", f"T{t} selects offset 00 - use TttOO (e.g. T0101) so nose radius/tip are known")
            else:
                st.tool = t
        for m in ms:
            if m in (3, 4):
                st.spindle_on = True
                if "S" not in w and st.s_word is None:
                    add("major", n, "spindle_without_s", f"M0{m} without a spindle speed S")
            elif m == 5:
                st.spindle_on = False
            elif m == 6:
                if lathe:
                    pass
                else:
                    if st.comp != 40:
                        add("major", n, "m06_with_comp", "M06 with cutter compensation active - cancel with G40 first")
                    if st.canned is not None:
                        add("major", n, "m06_with_canned", "M06 with a canned cycle active - cancel with G80 first")
                    st.len_comp = False
            elif m in (30, 2):
                st.ended = True
        if "S" in w:
            st.s_word = w["S"]
            lim = d.get("conventions", {}).get("machine_limits", {}).get("maxRpm")
            if lim and not st.css and w["S"] > lim and not (lathe and 50 in [int(g) for g in gs]):
                add("minor", n, "s_above_max", f"S{w['S']:g} exceeds the simulator maximum {lim} rpm (clamped)")
        if "F" in w:
            st.feed = w["F"]
            if lathe and st.feed_per_rev and w["F"] > 1.0 and st.motion not in (32, 92) and not cycle_block:
                add("minor", n, "feed_per_rev_high", f"F{w['F']:g} mm/rev is very high for turning (G99 active)")
            if lathe and st.feed_per_rev is False and w["F"] < 5:
                add("minor", n, "feed_per_min_low", f"F{w['F']:g} mm/min (G98) is extremely slow - G99 intended?")
            if not lathe and st.feed_per_rev and w["F"] > 5:
                add("minor", n, "feed_per_rev_mill_high", f"F{w['F']:g} mm/rev (G95) is very large - G94 intended?")

        # ------------------------------------------------ motion
        moves = [a for a in ("X", "Y", "Z", "U", "W") if a in w]
        if cycle_block:
            if st.feed is None and "F" not in w and any(int(g) in (71, 72, 73, 74, 75, 76) for g in gs) and ("P" in w and "Q" in w):
                add("critical", n, "cycle_without_feed", "cycle block without a feed rate (F)")
            if not st.spindle_on:
                add("major", n, "cycle_spindle_off", "machining cycle while the spindle is stopped")
            continue
        if not moves:
            continue
        if first_motion_line is None:
            first_motion_line = n
            if st.units is None:
                add("minor", n, "units_not_declared", "motion before G21 is programmed (relies on the simulator default)")
            if not lathe and st.absolute is None:
                add("minor", n, "distance_mode_not_declared", "motion before G90/G91 is programmed")
        prev = dict(st.pos)
        if lathe:
            if "X" in w and "U" in w:
                add("critical", n, "x_and_u", "X and U in the same block")
            if "Z" in w and "W" in w:
                add("critical", n, "z_and_w", "Z and W in the same block")
            if "X" in w:
                st.pos["X"] = w["X"]
            if "U" in w:
                st.pos["X"] = (st.pos["X"] or 0.0) + w["U"]
            if "Z" in w:
                st.pos["Z"] = w["Z"]
            if "W" in w:
                st.pos["Z"] = (st.pos["Z"] or 0.0) + w["W"]
        else:
            for a in "XYZ":
                if a in w:
                    st.pos[a] = (st.pos[a] or 0.0) + w[a] if st.absolute is False else w[a]
        cutting = st.motion in (1, 2, 3, 32) or (lathe and st.motion in LATHE_BOX) or (not lathe and st.canned is not None)
        if cutting:
            if st.feed is None:
                add("critical", n, "feed_missing", "feed move without a feed rate (F) - the control would alarm")
            if not st.spindle_on:
                add("major", n, "spindle_off", "feed move while the spindle is stopped (M03/M04 missing)")
            if st.tool is None:
                add("major", n, "no_tool", "feed move before any T tool selection")
            if not lathe and not st.len_comp and st.canned is None and st.motion in (1, 2, 3):
                if not st.g43_warned:
                    add("minor", n, "no_length_comp", "no G43 Hnn active (acceptable only if MillLab AUTO TOOL COMP is enabled and documented)")
                    st.g43_warned = True
        if st.motion in (2, 3) and not (lathe and st.motion in LATHE_BOX):
            _check_arc(n, w, prev, st, lathe, add)
        if not lathe and st.motion == 0 and ("X" in w or "Y" in w) and st.pos["Z"] is not None:
            ztop = (stock or {}).get("z_top", 0.0)
            if st.pos["Z"] < ztop - 1e-9:
                add("major", n, "rapid_below_top", f"G00 move in XY with Z{st.pos['Z']:g} below the stock top Z{ztop:g} - possible rapid into material")
        if lathe and st.motion == 0 and stock and stock.get("diameter") and st.pos["X"] is not None and st.pos["Z"] is not None:
            if st.pos["Z"] < 0 and 0 < st.pos["X"] < stock["diameter"] and prev["X"] is not None and prev["X"] >= stock["diameter"]:
                add("major", n, "rapid_into_stock", f"G00 from outside the stock to X{st.pos['X']:g} Z{st.pos['Z']:g} (inside the stock diameter, behind Z0)")
        for a in ("X", "Y", "Z"):
            if st.pos[a] is not None:
                ext[a].append(st.pos[a])
        last_motion = (n, st.motion, dict(st.pos))

    # ------------------------------------------------ end of program
    if code_lines == 0:
        return {"dialect": dialect_name, "nc_lines": 0, "findings": [Finding("critical", None, "empty", "no NC blocks found").to_dict()],
                "counts": {"critical": 1, "major": 0, "minor": 0, "info": 0}, "kind": "static check - NOT a simulation"}
    if not st.ended:
        add("minor", None, "no_m30", "program has no M30/M02 end")
    if st.comp != 40:
        add("minor", None, "comp_active_at_end", "program ends with compensation active (G40 missing)")
    if st.spindle_on:
        add("info", None, "spindle_on_at_end", "spindle still running at the end - M05 before M30 is good practice")
    if not lathe and st.canned is not None:
        add("info", None, "canned_active_at_end", "canned cycle still active at the end - G80 is good practice")
    if not saw_safe_line:
        add("minor", None, "no_safe_line", "no safe start line (e.g. G21 G18 G40 G99 / G21 G17 G40 G49 G80 G90 G94)")
    if last_motion and last_motion[1] != 0 and not re.search(r"G28|G53", text.upper()):
        add("minor", last_motion[0], "no_final_retract", "last motion is a feed move - no rapid retract / home return before the end")
    # Facing slightly past the centre line (X = -2 x nose radius, e.g. X-1.6 for R0.8) is normal practice and is
    # used in the simulator's own examples; beyond -4 mm on diameter it points to a sign or radius/diameter error.
    if lathe and ext["X"] and min(ext["X"]) < -4.0:
        add("major", None, "negative_diameter", f"X reaches {min(ext['X']):g}: X is a DIAMETER in LatheLab - check diameter/radius convention")
    elif lathe and ext["X"] and min(ext["X"]) < 0:
        add("info", None, "past_centre", f"X reaches {min(ext['X']):g} (facing past the centre line - fine if it equals about 2 x nose radius)")
    if stock:
        if lathe and stock.get("diameter") and ext["X"] and max(ext["X"]) > stock["diameter"] + 60:
            add("info", None, "far_from_stock", f"max X{max(ext['X']):g} is far outside the stock diameter {stock['diameter']:g}")
        if lathe and stock.get("length") and ext["Z"] and min(ext["Z"]) < -stock["length"]:
            add("major", None, "beyond_stock_length", f"Z reaches {min(ext['Z']):g}, beyond the stock length {stock['length']:g} (chuck collision risk)")
        if not lathe and stock.get("z_bottom") is not None and ext["Z"] and min(ext["Z"]) < stock["z_bottom"]:
            add("major", None, "below_stock_bottom", f"Z reaches {min(ext['Z']):g}, below the stock bottom {stock['z_bottom']:g} (vise/table risk)")
    else:
        add("info", None, "bounds_check_skipped", "no approved stock in the experiment configuration - out-of-bounds checks skipped")
    if cycles_used:
        add("info", None, "cycles_used", f"cycles used: {', '.join(sorted(cycles_used))} (cycle internals are not checked statically)")
    counts = {s: sum(1 for x in f if x.severity == s) for s in SEVERITIES}
    rng = lambda v: [round(min(v), 4), round(max(v), 4)] if v else None  # noqa: E731
    return {"dialect": dialect_name, "kind": "static check - NOT a simulation", "nc_lines": code_lines,
            "extents": {a: rng(v) for a, v in ext.items() if (a != "Y" or not lathe)},
            "x_is_diameter": lathe, "counts": counts, "findings": [x.to_dict() for x in f]}


def _check_arc(n, w, prev, st, lathe, add):
    has_r = "R" in w
    ijk = [a for a in "IJK" if a in w]
    if not has_r and not ijk:
        add("critical", n, "arc_without_radius", f"G0{st.motion} without R or I/J/K")
        return
    if lathe:
        a0, b0 = (prev["X"] / 2 if prev["X"] is not None else None), prev["Z"]
        a1, b1 = (st.pos["X"] / 2 if st.pos["X"] is not None else None), st.pos["Z"]
        ia, ib = w.get("I", 0.0), w.get("K", 0.0)
    else:
        plane = st.plane or 17
        ax = {17: ("X", "Y", "I", "J"), 18: ("Z", "X", "K", "I"), 19: ("Y", "Z", "J", "K")}[plane]
        a0, b0, a1, b1 = prev[ax[0]], prev[ax[1]], st.pos[ax[0]], st.pos[ax[1]]
        ia, ib = w.get(ax[2], 0.0), w.get(ax[3], 0.0)
    if None in (a0, b0, a1, b1):
        return
    chord = math.hypot(a1 - a0, b1 - b0)
    if has_r:
        if abs(w["R"]) * 2 < chord - 1e-3:
            add("critical", n, "arc_radius_too_small", f"R{w['R']:g} is smaller than half the chord {chord / 2:.3f} - no such arc"
                + (" (lathe X is a diameter: did you use radius values?)" if lathe else ""))
    elif ijk:
        cx, cy = a0 + ia, b0 + ib
        r0, r1 = math.hypot(a0 - cx, b0 - cy), math.hypot(a1 - cx, b1 - cy)
        if abs(r0 - r1) > max(0.01, 0.005 * r0):
            add("major", n, "arc_radius_mismatch", f"arc start radius {r0:.3f} != end radius {r1:.3f} (check I/J/K"
                + ("; I is a RADIUS value on the lathe" if lathe else "") + ")")


def check_file(path: Path, dialect_name: str | None = None, stock: dict | None = None) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    name = dialect_name or guess_dialect(path, text)
    res = check_program(text, name, stock=stock)
    res["file"] = str(path)
    return res


def guess_dialect(path: Path, text: str = "") -> str:
    p = str(path).lower()
    if "lathe" in p or "turn" in p:
        return "lathelab"
    if "mill" in p:
        return "milllab"
    return "milllab" if re.search(r"\bG17\b|\bM0?6\b|\bG43\b", text.upper()) else "lathelab"


def summarize(results: list[dict]) -> dict[str, Any]:
    tot = {s: sum(r["counts"][s] for r in results) for s in SEVERITIES}
    return {"files": len(results), "counts": tot}
