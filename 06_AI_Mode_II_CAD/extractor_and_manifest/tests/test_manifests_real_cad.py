"""Integration tests on the REAL Onshape evidence of both workpieces (extraction 2026-11-26).

The expected numbers are what the CAD model contains; several also appear on the
instructor drawings (sheet 2 / sheet 3), which is noted where it is the case. These tests
check that the pipeline reports the CAD faithfully - they are not a drawing check.
"""

from __future__ import annotations

import json

import jsonschema
import pytest

from apsd_cam import MANIFEST_DIR
from apsd_cam.cnc_manifest import validate


def feat(m, fid):
    return next(f for f in m["features"] if f["id"] == fid)


def dim(m, fid, key):
    return feat(m, fid)["dimensions"][key]["value"]


def loc(m, fid, key):
    return feat(m, fid)["location"][key]["value"]


# ------------------------------------------------------------------ schema, units, frame
@pytest.mark.parametrize("which", ["lathe_manifest", "milling_manifest"])
def test_schema_valid(which, request):
    validate(request.getfixturevalue(which))


@pytest.mark.parametrize("part", ["lathe", "milling"])
def test_committed_manifest_matches_rebuild(part, request):
    """The committed manifest must be reproducible from the committed evidence."""
    rebuilt = request.getfixturevalue(f"{part}_manifest")
    committed = json.loads((MANIFEST_DIR / f"{part}_manifest.json").read_text(encoding="utf-8"))
    for key in ("features", "relationships", "bounding_box", "missing_data", "human_annotations"):
        assert committed[key] == rebuilt[key], key


def test_units_are_mm_not_metres(lathe_manifest, milling_manifest):
    assert lathe_manifest["units"]["length"] == "mm"
    assert lathe_manifest["bounding_box"]["size_mm"][0] == 210.0  # not 0.21
    assert milling_manifest["bounding_box"]["size_mm"] == [156.0, 72.7823, 24.0]


def test_same_cad_revision_for_both_parts(lathe_manifest, milling_manifest):
    """Same document snapshot -> both workpieces come from one model state."""
    a, b = lathe_manifest["cad_source"], milling_manifest["cad_source"]
    assert a["document_id"] == b["document_id"]
    assert a["snapshot_microversion"] == b["snapshot_microversion"]
    assert a["revision_changed_during_extraction"] is False and b["revision_changed_during_extraction"] is False


# ------------------------------------------------------------------ lathe
def test_lathe_profile(lathe_manifest):
    m = lathe_manifest
    assert dim(m, "L-AXIS", "overall_axial_length") == 210.0  # drawing: 210
    ods = [(dim(m, f"L-OD-0{i}", "diameter"), loc(m, f"L-OD-0{i}", "axial_from"), loc(m, f"L-OD-0{i}", "axial_to")) for i in range(1, 5)]
    assert ods == [(29.9, 0.0, 20.0), (60.0, 20.0, 55.0), (100.0, 60.0, 80.0), (50.0, 85.0, 210.0)]
    assert [dim(m, f"L-BLEND-0{i}", "radius") for i in (1, 2)] == [5.0, 5.0]  # drawing: R5
    assert [dim(m, f"L-BORE-0{i}", "diameter") for i in (1, 2, 3)] == [12.0, 13.0, 30.0]


def test_lathe_holes_key_threads(lathe_manifest):
    m = lathe_manifest
    assert dim(m, "L-HOLES-01", "diameter") == 3.52 and dim(m, "L-HOLES-01", "count") == 6
    assert dim(m, "L-HOLES-01", "pitch_circle_diameter") == 46.0
    assert dim(m, "L-HOLES-01", "depth") == 4.1  # drawing: 4,1
    assert dim(m, "L-KEY-01", "width") == 7.98 and dim(m, "L-KEY-01", "top_distance_from_axis") == 17.9  # drawing: 7,98 / 17,9
    assert dim(m, "L-THREAD-EXT-01", "pitch") == 5.0
    assert dim(m, "L-THREAD-INT-01", "pitch") == 2.0
    # thread designation is NOT in CAD -> must stay UNKNOWN, never invented
    assert feat(m, "L-THREAD-EXT-01")["dimensions"]["designation_standard_class"]["label"] == "UNKNOWN"


def test_lathe_inconsistency_flagged_not_hidden(lathe_manifest):
    b = feat(lathe_manifest, "L-BORE-01")
    assert b["needs_human_verification"] and "14" in b["uncertainty"]


# ------------------------------------------------------------------ milling
def test_milling_axis_levels(milling_manifest):
    m = milling_manifest
    assert m["coordinate_system"]["axes"]["tool_axis"]["value"] == "+Z"
    assert m["coordinate_system"]["axes"]["is_2_5d"]["value"] is True
    levels = sorted((loc(m, f["id"], "height"), loc(m, f["id"], "facing")) for f in m["features"] if f["type"] == "planar_level")
    assert levels == [(-10.0, "-Z"), (-5.0, "-Z"), (5.0, "+Z"), (10.0, "+Z"), (14.0, "+Z")]


def test_milling_bosses_bores_keyway(milling_manifest):
    m = milling_manifest
    assert (dim(m, "M-BOSS-01", "diameter"), loc(m, "M-BOSS-01", "centre")) == (60.0, [0.0, 0.0])  # drawing: Ø60
    assert (dim(m, "M-BOSS-02", "diameter"), loc(m, "M-BOSS-02", "centre")) == (42.0, [105.0, 0.0])  # drawing: Ø42
    assert dim(m, "M-BORE-01", "diameter") == 30.0 and feat(m, "M-BORE-01")["location"]["through"]["value"] is True
    assert dim(m, "M-HOLE-01", "diameter") == 20.0 and feat(m, "M-HOLE-01")["location"]["through"]["value"] is True
    assert dim(m, "M-KEYWAY-01", "width") == 8.0  # drawing: 8
    assert dim(m, "M-KEYWAY-01", "end_wall_distance_from_bore_axis") == 18.0
    assert dim(m, "M-KEYWAY-01", "depth_beyond_bore_surface") == 3.0


def test_milling_window_pins_fillets(milling_manifest):
    m = milling_manifest
    w = feat(m, "M-WINDOW-01")
    assert w["type"] == "through_window" and dim(m, "M-WINDOW-01", "min_concave_radius") == 8.0  # drawing: R8
    radii = sorted(e["radius_mm"] for e in w["geometry_elements"])
    assert radii == [8.0, 8.0, 8.0, 8.0, 21.0, 30.0, 68.0, 107.0]
    assert dim(m, "M-PINS-01", "count") == 6 and dim(m, "M-PINS-01", "diameter") == 3.5
    assert dim(m, "M-PINS-01", "pitch_circle_diameter") == 46.0 and dim(m, "M-PINS-01", "height") == 4.0
    assert dim(m, "M-FILLET-01", "radius") == 2.0  # drawing: R2
    contour = sorted(e["radius_mm"] for e in feat(m, "M-CONTOUR-01")["geometry_elements"])
    assert contour == [21.0, 30.0, 60.0, 115.0]  # drawing: R60, R115


def test_milling_relationships(milling_manifest):
    rel = {r["description"]: r["value"] for r in milling_manifest["relationships"]}
    assert rel["Centre distance between the two bosses / bores"] == 105.0  # NOT dimensioned on the drawing
    assert any(v == 8.0 and "R115 and R107" in d for d, v in rel.items())  # drawing: 8
    assert any(v == 8.0 and "R68 and R60" in d for d, v in rel.items())  # drawing: 8


def test_interface_lathe_milling(lathe_manifest, milling_manifest):
    """Assembly interface: lathe key/holes vs milling keyway/pins (same PCD, compatible sizes)."""
    assert dim(lathe_manifest, "L-HOLES-01", "pitch_circle_diameter") == dim(milling_manifest, "M-PINS-01", "pitch_circle_diameter")
    assert dim(lathe_manifest, "L-HOLES-01", "diameter") > dim(milling_manifest, "M-PINS-01", "diameter")
    assert dim(lathe_manifest, "L-KEY-01", "width") < dim(milling_manifest, "M-KEYWAY-01", "width")
    assert dim(lathe_manifest, "L-OD-01", "diameter") < dim(milling_manifest, "M-BORE-01", "diameter")


# ------------------------------------------------------------------ traceability
def _resolve(evidence_dir, ref):
    fname, _, ptr = ref.partition("#")
    data = json.loads((evidence_dir / fname).read_text(encoding="utf-8"))
    for tok in [t for t in ptr.split("/") if t]:
        data = data[int(tok)] if isinstance(data, list) else data[tok]
    return data


@pytest.mark.parametrize("part", ["lathe", "milling"])
def test_every_evidence_pointer_resolves(part, request):
    m = request.getfixturevalue(f"{part}_manifest")
    ev = request.getfixturevalue(f"{part}_evidence")
    checked = 0
    for f in m["features"]:
        refs = list(f["evidence"]) + [r for v in list(f["dimensions"].values()) + list(f["location"].values()) for r in v.get("evidence", [])]
        for ref in refs:
            if "#/" in ref and " " not in ref.split("#")[0]:
                _resolve(ev, ref.split(" ")[0])
                checked += 1
    assert checked > 20


@pytest.mark.parametrize("part", ["lathe", "milling"])
def test_evidence_hashes_match(part, request):
    import hashlib

    m = request.getfixturevalue(f"{part}_manifest")
    ev = request.getfixturevalue(f"{part}_evidence")
    for name, sha in m["extraction"]["evidence_files"].items():
        assert hashlib.sha256((ev / name).read_bytes()).hexdigest() == sha


def test_manufacturing_hints_flagged_for_exclusion(lathe_manifest, milling_manifest):
    for m in (lathe_manifest, milling_manifest):
        assert m["manufacturing_considerations"]["excluded_from_mode_II_prompt"] is True


def test_human_annotations_not_auto_approved(lathe_manifest):
    assert lathe_manifest["human_annotations"], "Chapter 1 verified drawing fact expected"
    assert all(h["approved_for_mode_II_prompt"] is False for h in lathe_manifest["human_annotations"])


def test_schema_rejects_bad_manifest(milling_manifest):
    import copy

    bad = copy.deepcopy(milling_manifest)
    bad["features"][0]["dimensions"]["total_area"] = {"value": 5, "unit": "mm2", "label": "UNKNOWN", "note": "x"}
    with pytest.raises(jsonschema.ValidationError):
        validate(bad)
    bad = copy.deepcopy(milling_manifest)
    bad["features"][0]["evidence"] = []
    with pytest.raises(jsonschema.ValidationError):
        validate(bad)
    bad = copy.deepcopy(milling_manifest)
    bad["features"][0]["label"] = "GUESSED"
    with pytest.raises(jsonschema.ValidationError):
        validate(bad)
