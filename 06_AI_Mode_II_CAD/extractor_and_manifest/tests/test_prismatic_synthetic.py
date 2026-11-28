"""Software tests of the 2.5D analyser on SYNTHETIC fixtures (see conftest.SYNTHETIC).
They test the code paths, not the assigned workpieces."""

from __future__ import annotations

import copy

from apsd_cam.prismatic import analyse_prismatic


def test_block_with_hole_recognised(synthetic_block_with_hole):
    a = analyse_prismatic(synthetic_block_with_hole)
    assert a.get("error") is None
    assert a["tool_axis"]["name"] == "+Z" and a["tool_axis"]["is_2_5d"]
    assert a["envelope"]["size_mm"] == [40.0, 30.0, 10.0]
    types = sorted(r["type"] for r in a["regions"])
    assert types == ["hole", "outer_contour"]
    hole = next(r for r in a["regions"] if r["type"] == "hole")
    assert hole["elements"][0]["diameter_mm"] == 10.0 and hole["ref_centre_mm"] == [20.0, 15.0]
    assert hole["open_both_ends"] is True


def test_missing_feature_is_not_invented(synthetic_block_without_hole):
    a = analyse_prismatic(synthetic_block_without_hole)
    assert [r["type"] for r in a["regions"]] == ["outer_contour"]
    assert a["patterns"] == []


def test_outer_contour_of_block(synthetic_block_without_hole):
    a = analyse_prismatic(synthetic_block_without_hole)
    c = a["regions"][0]
    assert c["side"] == "material" and len(c["elements"]) == 4
    assert sorted(e["length_mm"] for e in c["elements"]) == [30.0, 30.0, 40.0, 40.0]


def test_levels_facing(synthetic_block_with_hole):
    a = analyse_prismatic(synthetic_block_with_hole)
    assert [(lv["height_mm"], lv["facing"]) for lv in a["levels"]] == [(10.0, "+"), (0.0, "-")]


def test_malformed_two_bodies_rejected(synthetic_block_with_hole):
    data = copy.deepcopy(synthetic_block_with_hole)
    data["bodies"].append(copy.deepcopy(data["bodies"][0]))
    assert "error" in analyse_prismatic(data)


def test_empty_input_rejected():
    assert "error" in analyse_prismatic({})
    assert "error" in analyse_prismatic({"bodies": [{"type": "SOLID", "faces": [], "edges": []}]})


def test_inclined_axis_reported_not_guessed(synthetic_block_with_hole):
    data = copy.deepcopy(synthetic_block_with_hole)
    s = 2 ** -0.5
    for f in data["bodies"][0]["faces"]:
        surf = f["surface"]
        if surf["type"] == "PLANE" and surf["normal"]["z"]:
            surf["normal"] = {"x": 0.0, "y": s, "z": s}
        if surf["type"] == "CYLINDER":
            surf["axis"] = {"x": 0.0, "y": s, "z": s}
    a = analyse_prismatic(data)
    assert "error" in a or a["tool_axis"]["is_2_5d"] is False
