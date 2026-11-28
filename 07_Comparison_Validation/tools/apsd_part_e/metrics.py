"""Six-case evaluation (brief Table 2.4) computed ONLY from recorded evidence.

Definitions (also in evaluation_methodology.md):
  recognized-feature coverage = correct reference features / applicable reference features.
      A feature is correct if its G1 outcome is CORRECT, or FLAGGED_AS_UNCLEAR when the
      reference marks it as not dimensioned in that mode's input (drawing_dimensioned=false
      for Mode I). PARTIAL / INCORRECT / MISSED / INVENTED_VALUE are not correct.
  dimensional discrepancy     = |AI value - reference value| in mm per compared dimension.
  program issues              = static-check findings of the INITIAL programs (by severity)
                                + issues recorded by humans in the review records.
  simulator-validated ops     = operations with result PASS in simulation_evidence/<part>/<case>/simulation_log.json
                                whose evidence file exists in the repository.
  human interventions         = recorded gate decisions with a reviewer (APPROVED, REJECTED,
                                REQUIRES_CORRECTION) + revisions authored by a human.
  development effort          = minutes in effort_log.csv per case and activity.
Anything not recorded is NOT_MEASURED / PENDING_*; nothing is estimated.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from .nc_check import check_file
from .paths import (BASELINE_OF, DIALECT_OF, EFFORT_LOG, MATRIX_CSV, MODE_DIR, NC_SUFFIXES, PARTS, REFERENCE_DIR, REPO,
                    REVIEW_DIR, REVISION_LOG, SIM_EVIDENCE_DIR)
from .prompts import rel

CASES = [("lathe", "manual"), ("lathe", "I"), ("lathe", "II"), ("milling", "manual"), ("milling", "I"), ("milling", "II")]
CASE_DIR = {"manual": "manual", "I": "mode_I", "II": "mode_II"}
COLUMNS = ["case", "workpiece", "source_mode", "input_coverage", "recognized_features", "missing_features", "incorrect_features",
           "recognized_feature_coverage", "dimensional_discrepancies_mm", "initial_nc_result", "program_issues_by_severity",
           "human_corrections", "simulator_validated_operations", "failed_or_unsupported_operations", "human_intervention_count",
           "development_effort_min", "final_validation_status", "evidence"]
GOOD = {"CORRECT"}


def coverage(worksheet: dict, reference: dict, mode: str) -> dict:
    refs = {f["ref_id"]: f for f in reference["features"]}
    mapping = {m["ref_id"]: m for m in worksheet.get("reference_mapping", []) if m.get("outcome")}
    if not worksheet.get("reviewer") or not mapping:
        return {"status": "NOT_MEASURED", "reason": "G1 worksheet not reviewed (no reviewer or no outcomes)"}
    correct, missed, incorrect, partial, errors = [], [], [], [], []
    for rid, f in refs.items():
        m = mapping.get(rid)
        out = (m or {}).get("outcome", "MISSED")
        undimensioned = mode == "I" and f.get("drawing_dimensioned") is False
        if out in GOOD or (undimensioned and out == "FLAGGED_AS_UNCLEAR"):
            correct.append(rid)
        elif out == "PARTIAL":
            partial.append(rid)
        elif out in ("INCORRECT", "INVENTED_VALUE"):
            incorrect.append(rid)
        else:
            missed.append(rid)
        for name, dv in ((m or {}).get("dims") or {}).items():
            ai = dv.get("ai_value")
            refv = dv.get("reference_value")
            if isinstance(ai, (int, float)) and isinstance(refv, (int, float)):
                errors.append({"ref_id": rid, "dimension": name, "ai": ai, "reference": refv, "abs_error_mm": round(abs(ai - refv), 4)})
    n = len(refs)
    errs = [e["abs_error_mm"] for e in errors]
    return {"status": "MEASURED", "applicable": n, "correct": len(correct), "partial": partial, "missed": missed, "incorrect": incorrect,
            "coverage": f"{len(correct)}/{n} = {len(correct) / n:.2f}" if n else "n/a",
            "dimensional": {"compared": len(errs), "mean_abs_error_mm": round(sum(errs) / len(errs), 4) if errs else None,
                            "max_abs_error_mm": max(errs) if errs else None, "over_0.05mm": sum(1 for e in errs if e > 0.05),
                            "items": errors}}


def _ai_runs(part: str, mode: str) -> list[Path]:
    base = MODE_DIR[mode] / "prompts_and_logs" / "runs"
    return sorted(p for p in base.glob(f"*_mode{mode}_{part}") if (p / "run_meta.json").exists())


def _records(run_id: str | None = None, workpiece: str | None = None, mode_label: str | None = None) -> list[dict]:
    out = []
    for p in sorted(REVIEW_DIR.glob("*.json")):
        try:
            r = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if r.get("record_type") != "human_review_record":
            continue
        if run_id and r.get("run_id") != run_id:
            continue
        if workpiece and r.get("workpiece") != workpiece:
            continue
        if mode_label and r.get("input_mode") != mode_label:
            continue
        r["_path"] = rel(p)
        out.append(r)
    return out


def _revisions(workpiece: str, mode_label: str) -> list[dict]:
    if not REVISION_LOG.exists():
        return []
    with open(REVISION_LOG, newline="", encoding="utf-8") as fh:
        return [r for r in csv.DictReader(fh) if r["workpiece"] == workpiece and r["mode"] == mode_label]


def _sim(part: str, case: str) -> dict:
    log = SIM_EVIDENCE_DIR / part / CASE_DIR[case] / "simulation_log.json"
    if not log.exists():
        return {"status": "PENDING_SIMULATION", "validated": 0, "failed_or_unsupported": []}
    data = json.loads(log.read_text(encoding="utf-8"))
    ok, bad = [], []
    for e in data.get("runs", []):
        ev = [REPO / x for x in e.get("evidence", [])]
        if e.get("result") == "PASS" and ev and all(p.exists() for p in ev):
            ok.append(e.get("operation"))
        elif e.get("result") in ("FAIL", "UNSUPPORTED", "PARTIAL"):
            bad.append(f"{e.get('operation')}: {e.get('result')}")
    return {"status": "RECORDED" if data.get("runs") else "PENDING_SIMULATION", "validated": len(ok), "operations": ok,
            "failed_or_unsupported": bad}


def _effort(case_label: str) -> dict:
    if not EFFORT_LOG.exists():
        return {"status": "NOT_MEASURED"}
    tot: dict[str, float] = {}
    with open(EFFORT_LOG, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r.get("case") == case_label and r.get("minutes"):
                tot[r["activity"]] = tot.get(r["activity"], 0.0) + float(r["minutes"])
    return {"status": "MEASURED", "minutes_by_activity": tot, "total": sum(tot.values())} if tot else {"status": "NOT_MEASURED"}


def _interventions(records: list[dict], revisions: list[dict]) -> dict:
    decisions = [(r["program"], g, x["status"]) for r in records for g, x in r["gates"].items()
                 if x.get("reviewer") and x.get("status") in ("APPROVED", "REJECTED", "REQUIRES_CORRECTION")]
    human_revs = [r for r in revisions if r["author_type"] == "human"]
    return {"gate_decisions": len(decisions), "human_revisions": len(human_revs), "total": len(decisions) + len(human_revs)}


def evaluate_case(part: str, case: str) -> dict:
    wp = PARTS[part]
    label = f"{wp} / {'Manual baseline' if case == 'manual' else 'Mode ' + case}"
    row: dict = {"case": label, "workpiece": wp, "source_mode": "Manual baseline" if case == "manual" else ("I: Drawing" if case == "I" else "II: CAD data")}
    reference = json.loads((REFERENCE_DIR / f"reference_features_{part}.json").read_text(encoding="utf-8"))
    sim = _sim(part, case)
    if case == "manual":
        files = sorted(p for p in BASELINE_OF[part].rglob("*") if p.is_file() and p.suffix.lower() in NC_SUFFIXES)
        if not files:
            row.update({k: "MISSING_DEPENDENCY" for k in COLUMNS if k not in row})
            row["input_coverage"] = "Full drawing / CAPP (Parts C/D)"
            row["initial_nc_result"] = f"MISSING_DEPENDENCY: no human NC program in {rel(BASELINE_OF[part])}"
            row["evidence"] = rel(BASELINE_OF[part])
            return row
        # A 'setup_*complete*' program is the full program of a setup; op_* files are excerpts of it.
        # Measure the complete programs only (otherwise every issue is counted twice); fall back to all files.
        complete = [p for p in files if p.name.lower().startswith("setup") and "complete" in p.name.lower()]
        measured = complete or files
        checks = [check_file(p, DIALECT_OF[part]) for p in measured]
        counts = {s: sum(c["counts"][s] for c in checks) for s in ("critical", "major", "minor")}
        recs = _records(workpiece=wp, mode_label="Manual baseline")
        row.update({"input_coverage": "Full drawing / CAPP (Parts C/D)", "recognized_features": "NOT_MEASURED (baseline G1 coverage worksheet not recorded)",
                    "missing_features": "NOT_MEASURED", "incorrect_features": "NOT_MEASURED", "recognized_feature_coverage": "NOT_MEASURED",
                    "dimensional_discrepancies_mm": "NOT_MEASURED", "initial_nc_result": f"{len(files)} human NC file(s); measured: {', '.join(p.name for p in measured)}",
                    "program_issues_by_severity": f"static: {counts}", "human_corrections": "n/a (human-authored)",
                    "simulator_validated_operations": sim["validated"] if sim["status"] == "RECORDED" else "PENDING_SIMULATION",
                    "failed_or_unsupported_operations": "; ".join(sim["failed_or_unsupported"]) or ("PENDING_SIMULATION" if sim["status"] != "RECORDED" else "none recorded"),
                    "human_intervention_count": "n/a", "development_effort_min": _fmt_effort(_effort(label)),
                    "final_validation_status": _final(recs, sim), "evidence": "; ".join(rel(p) for p in files)})
        return row
    runs = _ai_runs(part, case)
    if not runs:
        prepared = sorted((MODE_DIR[case] / "prompts_and_logs" / "runs").glob(f"*_mode{case}_{part}"))
        row.update({k: "NOT_RUN" for k in COLUMNS if k not in row})
        row["input_coverage"] = "drawing sheet image" if case == "I" else "CAD feature manifest"
        row["initial_nc_result"] = "NOT_RUN" + (f" (prompt prepared: {prepared[-1].name})" if prepared else " (no prompt prepared)")
        row["evidence"] = rel(MODE_DIR[case] / "prompts_and_logs")
        return row
    run = runs[0]  # the FIRST imported attempt is the initial proposal
    meta = json.loads((run / "run_meta.json").read_text(encoding="utf-8"))
    ws_path = MODE_DIR[case] / part / "recognized_features.json"
    ws = json.loads(ws_path.read_text(encoding="utf-8")) if ws_path.exists() else {}
    cov = coverage(ws, reference, case)
    recs = _records(run_id=meta["run_id"])
    revs = _revisions(PARTS[part], f"Mode {case}")
    # Same rule as the baseline rows: current checker, complete setup programs only (op files are excerpts).
    # The counts stored at import time stay in initial/<run>/automatic_checks.json as the historical record.
    init_files = sorted(p for p in (REPO / meta["initial_dir"]).glob("*") if p.is_file() and p.suffix.lower() in NC_SUFFIXES)
    measured = [p for p in init_files if p.name.lower().startswith("setup") and "complete" in p.name.lower()] or init_files
    static = {s: sum(check_file(p, DIALECT_OF[part])["counts"][s] for p in measured) for s in ("critical", "major", "minor")}
    human_issues: dict[str, int] = {}
    for r in recs:
        for g in r["gates"].values():
            for i in g.get("issues", []):
                human_issues[i.get("severity", "unclassified")] = human_issues.get(i.get("severity", "unclassified"), 0) + 1
    if case == "I":
        input_cov = "drawing sheet image (1 sheet)"
    else:
        man = json.loads((REPO / "06_AI_Mode_II_CAD/extractor_and_manifest/manifests" / f"{part}_manifest.json").read_text(encoding="utf-8"))
        input_cov = f"CAD manifest: {len(man['features'])} features, {len(man['relationships'])} relationships, {len(man['missing_data'])} UNKNOWN items"
    m = cov if cov["status"] == "MEASURED" else None
    row.update({
        "input_coverage": input_cov,
        "recognized_features": f"{m['correct']}/{m['applicable']}" if m else "NOT_MEASURED",
        "missing_features": ", ".join(m["missed"]) or "none" if m else "NOT_MEASURED",
        "incorrect_features": ", ".join(m["incorrect"]) or "none" if m else "NOT_MEASURED",
        "recognized_feature_coverage": m["coverage"] if m else "NOT_MEASURED",
        "dimensional_discrepancies_mm": (f"n={m['dimensional']['compared']}, mean={m['dimensional']['mean_abs_error_mm']}, max={m['dimensional']['max_abs_error_mm']}, >0.05mm: {m['dimensional']['over_0.05mm']}") if m else "NOT_MEASURED",
        "initial_nc_result": f"{len(meta['extracted_files'])} NC file(s) from run {meta['run_id']} (model '{meta['model_designation']}', {meta['date_of_use']}); parse problems: {len(meta['parse_problems'])}",
        "program_issues_by_severity": f"static ({', '.join(p.name for p in measured)}): {static}; human-recorded: {human_issues or 'none recorded'}",
        "human_corrections": f"{sum(1 for r in revs if r['author_type'] == 'human')} human / {sum(1 for r in revs if r['author_type'] == 'AI' and r['version'] != 'v00_initial')} AI revisions",
        "simulator_validated_operations": sim["validated"] if sim["status"] == "RECORDED" else "PENDING_SIMULATION",
        "failed_or_unsupported_operations": "; ".join(sim["failed_or_unsupported"]) or ("PENDING_SIMULATION" if sim["status"] != "RECORDED" else "none recorded"),
        "human_intervention_count": _interventions(recs, revs)["total"],
        "development_effort_min": _fmt_effort(_effort(label)),
        "final_validation_status": _final(recs, sim),
        "evidence": f"{rel(run)}; {meta['initial_dir']}; {rel(ws_path)}",
    })
    return row


def _fmt_effort(e: dict) -> str:
    return "NOT_MEASURED" if e["status"] != "MEASURED" else f"{e['total']:g} min {e['minutes_by_activity']}"


def _final(recs: list[dict], sim: dict) -> str:
    if not recs:
        return "PENDING_HUMAN_REVIEW"
    g4 = [r["gates"]["G4_simulation"]["status"] for r in recs]
    if all(s == "APPROVED" for s in g4):
        return "APPROVED (all programs passed G4)"
    if any(s == "REJECTED" for s in g4):
        return "REJECTED (at least one program)"
    if sim["status"] != "RECORDED":
        return "PENDING_SIMULATION"
    return "PENDING_HUMAN_REVIEW"


def build_matrix(path: Path = MATRIX_CSV) -> list[dict]:
    rows = [evaluate_case(p, c) for p, c in CASES]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in COLUMNS})
    return rows
