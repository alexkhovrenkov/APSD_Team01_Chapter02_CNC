"""Static NC checker tests. All programs here are SYNTHETIC snippets written to exercise
the checker; they are not programs for APSD-LATHE / APSD-MILLING."""

from __future__ import annotations

from apsd_part_e.nc_check import check_program

LATHE_OK = """%
O0001 (SYNTHETIC TEST - FACE AND TURN D40 STOCK)
G21 G18 G40 G99
G28 U0 W0
T0101
G50 S2500
G96 S180 M03
G00 X44. Z2.
G01 Z0 F0.2
X-1.6
G00 X38. Z2.
G01 Z-30. F0.25
G02 X40. Z-31. R1.
G00 X60. Z5.
G28 U0 W0
M05
M30
%"""

MILL_OK = """%
O1000 (SYNTHETIC TEST - SLOT)
G21 G17 G40 G49 G80 G90 G94
T02 M06
G54 G43 H02
S3000 M03
G00 X-10. Y20. Z5.
G01 Z-2. F200
X60.
G03 X70. Y30. R10.
G00 Z50.
M05
G91 G28 Z0
M30
%"""


def codes(res, sev=None):
    return [f["code"] for f in res["findings"] if sev is None or f["severity"] == sev]


def test_clean_lathe_program_has_no_critical_or_major():
    r = check_program(LATHE_OK, "lathelab")
    assert r["counts"]["critical"] == 0 and r["counts"]["major"] == 0, r["findings"]
    assert r["x_is_diameter"] and r["extents"]["X"] == [-1.6, 60.0]
    assert r["kind"].startswith("static check")


def test_clean_mill_program_has_no_critical_or_major():
    r = check_program(MILL_OK, "milllab")
    assert r["counts"]["critical"] == 0 and r["counts"]["major"] == 0, r["findings"]


def test_feed_missing_is_critical():
    r = check_program(LATHE_OK.replace("G01 Z0 F0.2", "G01 Z0"), "lathelab")
    assert "feed_missing" in codes(r, "critical")


def test_g91_not_supported_on_lathe():
    r = check_program(LATHE_OK.replace("G21 G18 G40 G99", "G21 G18 G40 G99 G91"), "lathelab")
    assert "unsupported_g" in codes(r, "critical")


def test_g90_as_absolute_mode_on_lathe_is_flagged():
    r = check_program(LATHE_OK.replace("G21 G18 G40 G99", "G21 G18 G40 G99\nG90"), "lathelab")
    assert "g90_as_absolute" in codes(r, "major")


def test_g90_is_fine_on_mill():
    assert "g90_as_absolute" not in codes(check_program(MILL_OK, "milllab"))


def test_lathe_specific_code_rejected_on_mill():
    r = check_program(MILL_OK.replace("X60.", "G71 U2. R0.5\nX60."), "milllab")
    assert "unsupported_g" in codes(r, "critical")


def test_arc_radius_too_small_and_missing_radius():
    r = check_program(LATHE_OK.replace("G02 X40. Z-31. R1.", "G02 X40. Z-41. R1."), "lathelab")
    assert "arc_radius_too_small" in codes(r, "critical")
    r = check_program(MILL_OK.replace("G03 X70. Y30. R10.", "G03 X70. Y30."), "milllab")
    assert "arc_without_radius" in codes(r, "critical")


def test_lathe_ijk_uses_radius_for_i():
    good = LATHE_OK.replace("G02 X40. Z-31. R1.", "G02 X40. Z-31. I0 K-1.")
    assert "arc_radius_mismatch" not in codes(check_program(good, "lathelab"))
    bad = LATHE_OK.replace("G02 X40. Z-31. R1.", "G02 X40. Z-31. I2. K-1.")
    assert "arc_radius_mismatch" in codes(check_program(bad, "lathelab"), "major")


def test_spindle_off_and_no_tool():
    r = check_program(LATHE_OK.replace("G96 S180 M03", "G96 S180"), "lathelab")
    assert "spindle_off" in codes(r, "major")
    r = check_program(MILL_OK.replace("T02 M06\n", ""), "milllab")
    assert "no_tool" in codes(r, "major")


def test_mill_rapid_below_top_and_m06_with_comp():
    r = check_program(MILL_OK.replace("G00 Z50.", "G00 X0 Y0"), "milllab")
    assert "rapid_below_top" in codes(r, "major")
    r = check_program(MILL_OK.replace("G01 Z-2. F200", "G41 D02\nG01 Z-2. F200").replace("G00 Z50.", "G00 Z50.\nT03 M06"), "milllab")
    assert "m06_with_comp" in codes(r, "major")


def test_program_end_and_units():
    r = check_program(LATHE_OK.replace("M30", ""), "lathelab")
    assert "no_m30" in codes(r, "minor")
    r = check_program(LATHE_OK.replace("G21", "G20"), "lathelab")
    assert "inch_units" in codes(r, "critical")


def test_negative_diameter_flagged():
    r = check_program(LATHE_OK.replace("X-1.6", "X-10."), "lathelab")
    assert "negative_diameter" in codes(r, "major")
    assert "past_centre" in codes(check_program(LATHE_OK, "lathelab"), "info")


def test_css_without_limit_and_tool_offset_00():
    r = check_program(LATHE_OK.replace("G50 S2500\n", "").replace("T0101", "T01"), "lathelab")
    assert "css_without_limit" in codes(r, "minor") and "tool_offset_00" in codes(r, "minor")


def test_stock_bounds_used_when_given():
    r = check_program(LATHE_OK, "lathelab", stock={"diameter": 40.0, "length": 20.0})
    assert "beyond_stock_length" in codes(r, "major")
    r = check_program(LATHE_OK, "lathelab")
    assert "bounds_check_skipped" in codes(r, "info")


def test_lathe_cycles_not_misread_as_motion():
    prog = LATHE_OK.replace("G00 X38. Z2.", "G00 X42. Z2.\nG71 U2. R0.5\nG71 P10 Q20 U0.4 W0.1 F0.25\nN10 G00 X30.\nN20 G01 Z-30.\nG70 P10 Q20").replace("G02 X40. Z-31. R1.\n", "")
    r = check_program(prog, "lathelab")
    assert r["counts"]["critical"] == 0 and "cycles_used" in codes(r, "info")


def test_empty_program():
    assert check_program("(only a comment)\n", "lathelab")["counts"]["critical"] == 1


def test_stock_bounds_come_from_the_confirmed_config():
    from apsd_part_e.nc_check import stock_from_config
    lathe, mill = stock_from_config("lathelab"), stock_from_config("milllab")
    assert lathe["diameter"] == 105 and lathe["length"] == 240 - 25 - 1
    assert mill["z_top"] == 0 and mill["z_bottom"] == -24


def test_g76_first_block_needs_no_feed():
    from apsd_part_e.nc_check import check_program
    ok = "G21 G18 G99\nT0404\nG97 S150 M03\nG00 X56 Z10\nG76 P020060 Q100 R0.05\nG76 X43.87 Z-122 P3067 Q700 F5.0\nG00 X110\nM05\nM30\n"
    assert not [f for f in check_program(ok, "lathelab")["findings"] if f["code"] == "cycle_without_feed"]
    bad = ok.replace(" F5.0", "")
    assert [f for f in check_program(bad, "lathelab")["findings"] if f["code"] == "cycle_without_feed"]
