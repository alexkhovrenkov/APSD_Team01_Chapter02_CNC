"""Shared fixtures.

Two kinds of data are used:
  * REAL evidence: ../evidence/<run>_lathe and <run>_milling, saved by a live read-only Onshape
    extraction on 2026-11-26. Tests on it are integration tests of the actual workpieces.
  * SYNTHETIC fixtures built below: invented minimal B-rep JSON used only to test the
    software (missing features, malformed input). They are NOT evidence about the
    assigned parts and must never be reported as engineering validation.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
EXTRACTOR = HERE.parent
sys.path.insert(0, str(EXTRACTOR / "scripts"))

import apsd_cam  # noqa: E402,F401  (sets up the vendored path)

SYNTHETIC = "SYNTHETIC TEST FIXTURE - not evidence about APSD-LATHE or APSD-MILLING"


def _latest(part: str) -> Path:
    runs = sorted((EXTRACTOR / "evidence").glob(f"*_{part}"))
    assert runs, f"no committed evidence for {part}"
    return runs[-1]


@pytest.fixture(scope="session")
def lathe_evidence() -> Path:
    return _latest("lathe")


@pytest.fixture(scope="session")
def milling_evidence() -> Path:
    return _latest("milling")


@pytest.fixture(scope="session")
def lathe_manifest(lathe_evidence):
    from apsd_cam.cnc_manifest import build_lathe

    return build_lathe(lathe_evidence)


@pytest.fixture(scope="session")
def milling_manifest(milling_evidence):
    from apsd_cam.cnc_manifest import build_milling

    return build_milling(milling_evidence)


# ------------------------------------------------------------------ synthetic B-rep builder
def P(x, y, z):
    return {"x": x, "y": y, "z": z}


class Brep:
    """Tiny builder for Onshape-like body details (metres). SYNTHETIC."""

    def __init__(self):
        self.faces, self.edges, self.n = [], [], 0

    def _id(self, p):
        self.n += 1
        return f"{p}{self.n}"

    def line(self, a, b):
        eid = self._id("E")
        mid = tuple((a[i] + b[i]) / 2 for i in range(3))
        self.edges.append({"id": eid, "curve": {"type": "LINE"},
                           "geometry": {"startPoint": P(*a), "endPoint": P(*b), "midPoint": P(*mid),
                                        "length": math.dist(a, b)}})
        return eid

    def circle(self, c, r, z):
        eid = self._id("E")
        p0 = (c[0] + r, c[1], z)
        self.edges.append({"id": eid, "curve": {"type": "CIRCLE", "radius": r, "origin": P(c[0], c[1], z), "normal": P(0, 0, 1)},
                           "geometry": {"startPoint": P(*p0), "endPoint": P(*p0), "midPoint": P(c[0] - r, c[1], z),
                                        "quarterPoint": P(c[0], c[1] + r, z), "arcSweep": 2 * math.pi, "length": 2 * math.pi * r}})
        return eid

    def face(self, surface, ori, loops, area=1e-4, box=None):
        f = {"id": self._id("F"), "surface": surface, "orientation": ori, "area": area,
             "loops": [{"coedges": [{"edgeId": e} for e in lp]} for lp in loops]}
        if box:
            f["box"] = {"minCorner": P(*box[0]), "maxCorner": P(*box[1])}
        self.faces.append(f)

    def body(self, n_bodies=1):
        b = {"id": "B1", "type": "SOLID", "faces": self.faces, "edges": self.edges, "vertices": []}
        return {"_note": SYNTHETIC, "bodies": [b] * n_bodies}


def block(with_hole: bool = True, lx=0.04, ly=0.03, h=0.01, hole_c=(0.02, 0.015), hole_r=0.005) -> dict:
    """Block lx x ly x h (z 0..h) with an optional vertical through hole. SYNTHETIC."""
    b = Brep()
    c = [(0, 0), (lx, 0), (lx, ly), (0, ly)]
    top = [b.line((*c[i], h), (*c[(i + 1) % 4], h)) for i in range(4)]
    bot = [b.line((*c[i], 0), (*c[(i + 1) % 4], 0)) for i in range(4)]
    vert = [b.line((*c[i], 0), (*c[i], h)) for i in range(4)]
    loops_top, loops_bot = [top], [bot]
    if with_hole:
        ct, cb = b.circle(hole_c, hole_r, h), b.circle(hole_c, hole_r, 0)
        loops_top.append([ct])
        loops_bot.append([cb])
        b.face({"type": "CYLINDER", "radius": hole_r, "origin": P(*hole_c, 0), "axis": P(0, 0, 1)}, False, [[ct], [cb]],
               area=2 * math.pi * hole_r * h, box=((hole_c[0] - hole_r, hole_c[1] - hole_r, 0), (hole_c[0] + hole_r, hole_c[1] + hole_r, h)))
    b.face({"type": "PLANE", "origin": P(0, 0, h), "normal": P(0, 0, 1)}, True, loops_top, area=lx * ly, box=((0, 0, h), (lx, ly, h)))
    b.face({"type": "PLANE", "origin": P(0, 0, 0), "normal": P(0, 0, 1)}, False, loops_bot, area=lx * ly, box=((0, 0, 0), (lx, ly, 0)))
    normals = [(0, -1, 0), (1, 0, 0), (0, 1, 0), (-1, 0, 0)]
    for i in range(4):
        a, d = c[i], c[(i + 1) % 4]
        b.face({"type": "PLANE", "origin": P(*a, 0), "normal": P(*normals[i])}, True,
               [[bot[i], vert[(i + 1) % 4], top[i], vert[i]]], area=math.dist(a, d) * h,
               box=((min(a[0], d[0]), min(a[1], d[1]), 0), (max(a[0], d[0]), max(a[1], d[1]), h)))
    return b.body()


@pytest.fixture
def synthetic_block_with_hole():
    return block(True)


@pytest.fixture
def synthetic_block_without_hole():
    return block(False)
