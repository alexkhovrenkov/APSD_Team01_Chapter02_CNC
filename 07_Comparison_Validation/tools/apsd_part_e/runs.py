"""Archive AI replies (write-once), register revisions, keep the revision log and the
human-review records.

Preservation rules (tested in tests/test_runs.py):
  * every archived file is created with exclusive mode ('x'): an initial attempt can never
    be overwritten, re-importing the same run fails;
  * revisions go to <part>/revisions/vNN_<name> with the parent file's SHA-256;
  * the program_revision_log.csv is append-only;
  * review records are created with every gate PENDING_HUMAN_REVIEW and reviewer=null:
    the tool never fills in a human decision.
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import re
from pathlib import Path

from .nc_check import check_file
from .paths import DIALECT_OF, MODE_DIR, PARTS, REPO, REVIEW_DIR, REVISION_LOG
from .prompts import rel, sha

LOG_FIELDS = ["timestamp_utc", "workpiece", "mode", "run_id", "program", "version", "path", "sha256", "parent_path",
              "parent_sha256", "author_type", "author", "model", "reason", "review_record", "static_check_counts"]
GATES = ("G1_geometry", "G2_process", "G3_code", "G4_simulation")
STATUSES = ("PENDING_HUMAN_REVIEW", "APPROVED", "REJECTED", "REQUIRES_CORRECTION", "PENDING_SIMULATION")
FENCE = re.compile(r"```([^\n`]*)\n(.*?)```", re.S)


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def write_once(path: Path, data: str | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "xb" if isinstance(data, bytes) else "x"
    with open(path, mode, **({} if isinstance(data, bytes) else {"encoding": "utf-8"})) as fh:
        fh.write(data)


def append_log(row: dict) -> None:
    new = not REVISION_LOG.exists() or REVISION_LOG.stat().st_size == 0
    with open(REVISION_LOG, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=LOG_FIELDS)
        if new:
            w.writeheader()
        w.writerow({k: row.get(k, "") for k in LOG_FIELDS})


def parse_reply(text: str) -> dict:
    """Split a reply into JSON blocks (features / operations) and NC blocks (file=...)."""
    out: dict = {"features": None, "operations": None, "nc": [], "other_blocks": 0, "problems": []}
    for info, body in FENCE.findall(text):
        info = info.strip()
        low = info.lower()
        if low.startswith("json"):
            tag = low.split()[1] if len(low.split()) > 1 else ""
            try:
                obj = json.loads(body)
            except json.JSONDecodeError as exc:
                out["problems"].append(f"JSON block '{info}' does not parse: {exc}")
                continue
            if tag == "features" or (not tag and "features" in obj and out["features"] is None):
                out["features"] = obj
            elif tag == "operations" or (not tag and "setups" in obj and out["operations"] is None):
                out["operations"] = obj
            else:
                out["other_blocks"] += 1
        elif low.startswith(("gcode", "nc", "g-code")):
            attrs = dict(re.findall(r"(\w+)=([^\s]+)", info))
            name = attrs.get("file")
            if not name:
                out["problems"].append("NC block without file=... in its info string; saved as unnamed")
                name = f"unnamed_{len(out['nc']) + 1:02d}.nc"
            name = re.sub(r"[^A-Za-z0-9_.-]", "_", name)
            out["nc"].append({"file": name, "setup": attrs.get("setup"), "op": attrs.get("op"), "text": body})
        else:
            out["other_blocks"] += 1
    if out["features"] is None:
        out["problems"].append("no 'json features' block found")
    if out["operations"] is None:
        out["problems"].append("no 'json operations' block found")
    if not out["nc"]:
        out["problems"].append("no NC block found")
    names = [b["file"] for b in out["nc"]]
    if len(names) != len(set(names)):
        out["problems"].append("duplicate NC file names in the reply")
    return out


def review_record(part: str, mode: str, run_id: str, program: str, version: str, path: str, file_sha: str, checks: dict) -> dict:
    return {
        "record_type": "human_review_record", "workpiece": PARTS[part], "input_mode": f"Mode {mode}",
        "program": program, "program_version": version, "program_path": path, "program_sha256": file_sha, "run_id": run_id,
        "created_utc": _now(), "created_by": "apsd_part_e import tool (no human decision recorded by the tool)",
        "automatic_static_check": {"counts": checks["counts"], "kind": checks["kind"], "file": "automatic_checks.json"},
        "gates": {g: {"status": "PENDING_HUMAN_REVIEW" if g != "G4_simulation" else "PENDING_SIMULATION",
                      "issues": [], "evidence": [], "recommended_correction": None, "ai_review_suggestion": None,
                      "decision": None, "reviewer": None, "review_date": None} for g in GATES},
        "allowed_status_values": list(STATUSES),
        "issue_format": {"id": "I01", "gate": "G3_code", "severity": "critical|major|minor", "description": "...", "evidence": "file:line or screenshot",
                         "recommended_correction": "...", "found_by": "human|static_check|simulator|ai_review"},
    }


def import_response(run_dir: Path, reply_file: Path, model: str, operator: str, date: str | None = None,
                    interface: str = "claude.ai web chat (manual paste, new conversation)", conversation_ref: str | None = None) -> dict:
    run_dir = run_dir.resolve()
    ctx = json.loads((run_dir / "input_manifest.json").read_text(encoding="utf-8"))
    mode = ctx["mode"]
    part = next(k for k, v in PARTS.items() if v == ctx["part"])
    prompt = (run_dir / "prompt.md").read_text(encoding="utf-8")
    if sha(prompt) != ctx["prompt_sha256"]:
        raise SystemExit("prompt.md changed after it was prepared - the archived prompt would not match what was sent")
    raw = reply_file.read_bytes()
    write_once(run_dir / "response_raw.txt", raw)  # fails if the run was already imported
    text = raw.decode("utf-8", errors="replace")
    parsed = parse_reply(text)
    run_id = run_dir.name
    initial = MODE_DIR[mode] / ("lathe" if part == "lathe" else "milling") / "initial" / run_id
    files = []
    if parsed["features"] is not None:
        write_once(initial / "recognized_features_raw.json", json.dumps(parsed["features"], indent=1, ensure_ascii=False) + "\n")
    if parsed["operations"] is not None:
        write_once(initial / "operation_plan_raw.json", json.dumps(parsed["operations"], indent=1, ensure_ascii=False) + "\n")
    checks_all = {}
    for b in parsed["nc"]:
        p = initial / b["file"]
        write_once(p, b["text"])
        res = check_file(p, DIALECT_OF[part])
        checks_all[b["file"]] = res
        fsha = sha(p.read_bytes())
        rec = review_record(part, mode, run_id, b["file"], "v00_initial", rel(p), fsha, res)
        rec_path = REVIEW_DIR / f"{run_id}__{Path(b['file']).stem}.json"
        write_once(rec_path, json.dumps(rec, indent=1) + "\n")
        append_log({"timestamp_utc": _now(), "workpiece": PARTS[part], "mode": f"Mode {mode}", "run_id": run_id, "program": b["file"],
                    "version": "v00_initial", "path": rel(p), "sha256": fsha, "author_type": "AI", "author": operator,
                    "model": model, "reason": "initial AI proposal (unverified)", "review_record": rel(rec_path),
                    "static_check_counts": json.dumps(res["counts"])})
        files.append({"file": rel(p), "sha256": fsha, "setup": b["setup"], "op": b["op"], "static_check_counts": res["counts"]})
    write_once(initial / "automatic_checks.json", json.dumps(checks_all, indent=1) + "\n")
    meta = {"run_id": run_id, "mode": mode, "workpiece": PARTS[part], "provider": "Anthropic", "model_designation": model,
            "model_designation_source": "as entered by the operator from the chat's model selector", "interface": interface,
            "date_of_use": date or dt.date.today().isoformat(), "operator": operator, "conversation_ref": conversation_ref,
            "input_modalities": ["text", "image"] if mode == "I" else ["text"], "settings": "chat defaults (no temperature control in the web chat)",
            "prompt_sha256": ctx["prompt_sha256"], "reply_sha256": sha(raw), "imported_utc": _now(),
            "parse_problems": parsed["problems"], "extracted_files": files, "initial_dir": rel(initial),
            "status": "INITIAL AI PROPOSAL - UNVERIFIED (simulation-only candidate)"}
    write_once(run_dir / "run_meta.json", json.dumps(meta, indent=1) + "\n")
    write_once(initial / "README.md", f"# Initial AI attempt {run_id}\n\nMode {mode}, {PARTS[part]}, model '{model}', {meta['date_of_use']}.\n"
               f"UNVERIFIED simulation-only candidate. Do not edit these files - put corrections in ../../revisions/.\n"
               f"Prompt and raw reply: {rel(run_dir)}\n")
    _init_part_worksheets(mode, part, run_id, parsed)
    return meta


def _init_part_worksheets(mode: str, part: str, run_id: str, parsed: dict) -> None:
    """Create the part-level G1 worksheet and operation plan once (first imported attempt)."""
    pdir = MODE_DIR[mode] / ("lathe" if part == "lathe" else "milling")
    ws = pdir / "recognized_features.json"
    if not ws.exists() or json.loads(ws.read_text(encoding="utf-8")).get("status") == "NOT_YET_GENERATED":
        feats = (parsed["features"] or {}).get("features", [])
        doc = {"title": f"G1 geometry worksheet - Mode {mode} - {PARTS[part]}", "status": "PENDING_HUMAN_REVIEW",
               "source_run": run_id, "ai_features_raw": f"initial/{run_id}/recognized_features_raw.json",
               "ai_unclear_or_missing": (parsed["features"] or {}).get("unclear_or_missing", []),
               "instructions": "For every reference feature (07_Comparison_Validation/evaluation_reference) fill outcome = "
                               "CORRECT | PARTIAL | INCORRECT | MISSED | FLAGGED_AS_UNCLEAR | INVENTED_VALUE, the AI feature ids, "
                               "and ai_value for each compared dimension. Reviewer and date are mandatory. Do not edit ai_* fields.",
               "reference_mapping": [], "ai_feature_ids": [f.get("id") for f in feats], "reviewer": None, "review_date": None}
        ws.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    op = pdir / "operation_plan.md"
    if not op.exists() or "NOT_YET_GENERATED" in op.read_text(encoding="utf-8"):
        ops = parsed["operations"] or {}
        lines = [f"# Operation plan - Mode {mode} - {PARTS[part]}", "", f"Source: initial AI attempt `{run_id}` (UNVERIFIED). "
                 "G2 process-gate decisions go in 07_Comparison_Validation/human_review_records/.", "",
                 "| Setup | Op | Name | Tool | Strategy | Features | Simulator supported | NC file |", "|---|---|---|---|---|---|---|---|"]
        for s in ops.get("setups", []):
            for o in s.get("operations", []):
                lines.append(f"| {s.get('id')} | {o.get('id')} | {o.get('name')} | {o.get('tool')} | {o.get('strategy')} | "
                             f"{', '.join(o.get('features', []))} | {o.get('simulator_supported')} | {o.get('nc_file')} |")
        lines += ["", "## AI assumptions (unverified)", ""] + [f"- {a}" for a in ops.get("assumptions", [])]
        op.write_text("\n".join(lines) + "\n", encoding="utf-8")


def register_revision(parent: Path, new_file: Path, author_type: str, author: str, reason: str,
                      model: str | None = None, review_record_path: str | None = None) -> Path:
    """Copy a corrected program into <part>/revisions/vNN_<name>; never touches the parent."""
    parent = parent.resolve()
    if author_type not in ("human", "AI"):
        raise ValueError("author_type must be 'human' or 'AI'")
    parts = parent.parts
    part_dir = next(Path(*parts[: i + 1]) for i, p in enumerate(parts) if p in ("lathe", "milling") and parts[i - 1].startswith("0"))
    mode = "I" if part_dir.parent.name.startswith("05") else "II"
    part = part_dir.name
    rev_dir = part_dir / "revisions"
    rev_dir.mkdir(parents=True, exist_ok=True)
    stem = parent.stem
    existing = sorted(rev_dir.glob(f"v*_{stem}{parent.suffix}"))
    n = len(existing) + 1
    dest = rev_dir / f"v{n:02d}_{stem}{parent.suffix}"
    write_once(dest, new_file.read_bytes())
    res = check_file(dest, DIALECT_OF["lathe" if part == "lathe" else "milling"])
    append_log({"timestamp_utc": _now(), "workpiece": PARTS["lathe" if part == "lathe" else "milling"], "mode": f"Mode {mode}",
                "run_id": parent.parent.name if parent.parent.parent.name == "initial" else "", "program": parent.name,
                "version": f"v{n:02d}", "path": rel(dest), "sha256": sha(dest.read_bytes()), "parent_path": rel(parent),
                "parent_sha256": sha(parent.read_bytes()), "author_type": author_type, "author": author, "model": model or "",
                "reason": reason, "review_record": review_record_path or "", "static_check_counts": json.dumps(res["counts"])})
    return dest


__all__ = ["import_response", "register_revision", "parse_reply", "write_once", "REPO"]
