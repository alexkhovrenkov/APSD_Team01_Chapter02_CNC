"""Prompt isolation, write-once archiving, revision preservation and metric definitions.
Replies and worksheets used here are SYNTHETIC test data, not AI results for the parts."""

from __future__ import annotations

import csv
import json

import pytest

from apsd_part_e import metrics, prompts, runs


# ------------------------------------------------------------------ prompts / isolation
@pytest.mark.parametrize("mode", ["I", "II"])
@pytest.mark.parametrize("part", ["lathe", "milling"])
def test_real_prompts_pass_isolation(mode, part):
    text, ctx = prompts.build_prompt(mode, part)
    assert ctx["isolation"]["passed"], ctx["isolation"]
    assert "R-L-" not in text and "R-M-" not in text
    if mode == "I":
        assert "apsd-cnc-feature-manifest" not in text and ctx["attachments"]
    else:
        assert '"manufacturing_considerations"' not in text and ".png" not in text and not ctx["attachments"]
        assert '"feature_tree"' not in text


def test_both_modes_share_identical_task_text():
    a, _ = prompts.build_prompt("I", "milling")
    b, _ = prompts.build_prompt("II", "milling")
    head_a = a.split("# Geometry source")[0].split("Mode: ")[0]
    head_b = b.split("# Geometry source")[0].split("Mode: ")[0]
    assert head_a == head_b
    cfg_a = a.split("# Machine, simulator")[1].split("# Geometry source")[0]
    cfg_b = b.split("# Machine, simulator")[1].split("# Geometry source")[0]
    assert cfg_a == cfg_b


def test_leak_detector_catches_reference_dimension():
    assert prompts.leaked_numbers("boss centre distance 105 mm", "milling") == ["105"]
    assert prompts.leaked_numbers("use G21 and T0101, op_10, id 20caaefd", "milling") == []


def test_unapproved_human_annotation_is_not_sent():
    m, removed = prompts.mode_ii_manifest("lathe")
    assert m["human_annotations"] == [] and any("annotation" in r for r in removed)


def test_preflight_blocks_without_baseline_and_part_b():
    probs = prompts.preflight("lathe")
    assert any("baseline" in p for p in probs) and any(".stock" in p for p in probs)


# ------------------------------------------------------------------ archiving
REPLY = """Here is my proposal.
## 1. Recognized features
```json features
{"features": [{"id": "F01", "type": "outer_diameter", "dimensions": {"diameter_mm": 40}}], "unclear_or_missing": [{"item": "x", "why": "y"}]}
```
## 2. Operation plan
```json operations
{"setups": [{"id": "S1", "operations": [{"id": "OP10", "name": "face", "tool": "T01", "features": ["F01"], "simulator_supported": true, "nc_file": "op_10_face.nc"}]}], "assumptions": ["a"]}
```
## 4. NC programs
```gcode file=op_10_face.nc setup=S1 op=OP10
G21 G18 G40 G99
T0101
G50 S2000
G96 S150 M03
G00 X44. Z2.
G01 Z0 F0.2
X-1.6
G00 X60. Z5.
M05
M30
```
"""


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    mode_i = tmp_path / "05_AI_Mode_I_Drawing"
    mode_ii = tmp_path / "06_AI_Mode_II_CAD"
    review = tmp_path / "07" / "human_review_records"
    log = tmp_path / "07" / "program_revision_log.csv"
    review.mkdir(parents=True)
    monkeypatch.setattr(runs, "MODE_DIR", {"I": mode_i, "II": mode_ii})
    monkeypatch.setattr(runs, "REVIEW_DIR", review)
    monkeypatch.setattr(runs, "REVISION_LOG", log)
    run = mode_i / "prompts_and_logs" / "runs" / "20990101T000000Z_modeI_lathe"
    run.mkdir(parents=True)
    (run / "prompt.md").write_text("PROMPT", encoding="utf-8")
    (run / "input_manifest.json").write_text(json.dumps({"mode": "I", "part": "APSD-LATHE", "prompt_sha256": prompts.sha("PROMPT")}), encoding="utf-8")
    reply = tmp_path / "reply.txt"
    reply.write_text(REPLY, encoding="utf-8")
    return {"run": run, "reply": reply, "review": review, "log": log, "mode_i": mode_i}


def test_import_archives_everything_write_once(sandbox):
    meta = runs.import_response(sandbox["run"], sandbox["reply"], "Test-Model (synthetic)", "tester", "2099-01-01")
    init = sandbox["mode_i"] / "lathe" / "initial" / sandbox["run"].name
    assert (init / "op_10_face.nc").exists() and (init / "recognized_features_raw.json").exists()
    assert (sandbox["run"] / "response_raw.txt").read_text(encoding="utf-8") == REPLY
    assert meta["parse_problems"] == [] and meta["status"].startswith("INITIAL AI PROPOSAL")
    with pytest.raises(FileExistsError):
        runs.import_response(sandbox["run"], sandbox["reply"], "Test-Model", "tester")
    rec = json.loads(next(sandbox["review"].glob("*.json")).read_text(encoding="utf-8"))
    assert all(g["reviewer"] is None and g["decision"] is None for g in rec["gates"].values())
    assert rec["gates"]["G1_geometry"]["status"] == "PENDING_HUMAN_REVIEW"
    rows = list(csv.DictReader(open(sandbox["log"], encoding="utf-8")))
    assert rows[0]["version"] == "v00_initial" and rows[0]["author_type"] == "AI"


def test_revision_never_touches_initial(sandbox, tmp_path):
    runs.import_response(sandbox["run"], sandbox["reply"], "Test-Model", "tester", "2099-01-01")
    parent = sandbox["mode_i"] / "lathe" / "initial" / sandbox["run"].name / "op_10_face.nc"
    before = parent.read_bytes()
    fixed = tmp_path / "fixed.nc"
    fixed.write_text(before.decode().replace("G00 X60. Z5.", "G00 X60. Z5.\nG28 U0 W0"), encoding="utf-8")
    d1 = runs.register_revision(parent, fixed, "human", "tester", "add home return")
    d2 = runs.register_revision(parent, fixed, "human", "tester", "second edit")
    assert parent.read_bytes() == before
    assert d1.name == "v01_op_10_face.nc" and d2.name == "v02_op_10_face.nc"
    rows = list(csv.DictReader(open(sandbox["log"], encoding="utf-8")))
    assert rows[-1]["parent_sha256"] == prompts.sha(before) and rows[-1]["author_type"] == "human"


def test_parse_reply_reports_missing_blocks():
    p = runs.parse_reply("no code here")
    assert "no NC block found" in p["problems"] and "no 'json features' block found" in p["problems"]


# ------------------------------------------------------------------ metrics
REF = {"features": [{"ref_id": "R-X-01", "drawing_dimensioned": True}, {"ref_id": "R-X-02", "drawing_dimensioned": True},
                    {"ref_id": "R-X-03", "drawing_dimensioned": False}, {"ref_id": "R-X-04", "drawing_dimensioned": True}]}


def test_coverage_not_measured_without_reviewer():
    assert metrics.coverage({"reference_mapping": [{"ref_id": "R-X-01", "outcome": "CORRECT"}]}, REF, "I")["status"] == "NOT_MEASURED"


def test_coverage_definition():
    ws = {"reviewer": "synthetic", "reference_mapping": [
        {"ref_id": "R-X-01", "outcome": "CORRECT", "dims": {"d": {"ai_value": 30.0, "reference_value": 30.0}}},
        {"ref_id": "R-X-02", "outcome": "INCORRECT", "dims": {"d": {"ai_value": 21.0, "reference_value": 20.0}}},
        {"ref_id": "R-X-03", "outcome": "FLAGGED_AS_UNCLEAR"}]}
    c = metrics.coverage(ws, REF, "I")
    assert c["coverage"] == "2/4 = 0.50"  # R-X-03 counts: not dimensioned on the drawing and correctly flagged
    assert c["missed"] == ["R-X-04"] and c["incorrect"] == ["R-X-02"]
    assert c["dimensional"]["max_abs_error_mm"] == 1.0 and c["dimensional"]["over_0.05mm"] == 1
    assert metrics.coverage(ws, REF, "II")["coverage"] == "1/4 = 0.25"  # in Mode II the value IS in the input


def test_current_matrix_reports_dependencies_not_numbers(tmp_path):
    rows = metrics.build_matrix(tmp_path / "m.csv")
    assert len(rows) == 6
    manual = [r for r in rows if r["source_mode"] == "Manual baseline"]
    assert all(r["initial_nc_result"].startswith("MISSING_DEPENDENCY") for r in manual)
    ai = [r for r in rows if r["source_mode"] != "Manual baseline"]
    assert all(r["recognized_feature_coverage"] in ("NOT_RUN", "NOT_MEASURED") for r in ai)
