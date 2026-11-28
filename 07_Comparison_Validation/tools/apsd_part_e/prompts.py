"""Build the exact Mode I / Mode II prompts and check experimental isolation.

Both modes share the same template, the same 'ai_visible' configuration and the same
dialect summary. Only the geometry block differs:
  Mode I : drawing image(s) to ATTACH (listed with SHA-256); no manifest text.
  Mode II: the CAD manifest, with manufacturing_considerations removed, human annotations
           filtered to the approved ones, and the feature tree (feature NAMES) removed.

Isolation checks (recorded in isolation_check.json, a failing check stops the build):
  * no evaluation-reference content (reference ids, file names) in the prompt;
  * no line of a human baseline program (03_Lathe / 04_Mill) in the prompt;
  * Mode I: no manifest content; Mode II: no drawing attachment or drawing file name;
  * the shared configuration and template contain no reference dimension of the part
    (numbers >= 3 not attached to a letter, compared with the evaluation reference); numbers that are
    process values (tool sizes, feeds) are accepted only if listed with a reason in the config's
    'isolation_allowlist'.
Preflight (stop unless --allow-pending, then recorded as accepted deviations):
  * required configuration values still MISSING / PENDING_HUMAN_REVIEW;
  * no human baseline program yet (brief 2.5: baseline before AI);
  * evaluation reference not yet verified (needed later for metrics only: warning).
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from pathlib import Path

from .paths import (BASELINE_OF, CONFIG_PATH, DIALECT_PATH, DRAWING_INPUTS, DRAWING_OF, MANIFEST_DIR, MODE_DIR, NC_SUFFIXES,
                    PARTS, REFERENCE_DIR, REPO, TEMPLATE_PATH)

REQUIRED_KEYS = ("stock", "material", "work_origin", "setups", "workholding", "tools", "cutting_data", "safety_clearances")
# a "number" is a free-standing decimal: not part of an identifier (G21, T0101, op_10, hex ids)
NUM = re.compile(r"(?<![A-Za-z0-9._#-])\d+(?:\.\d+)?(?![0-9A-Za-z_])")


def sha(b: bytes | str) -> str:
    return hashlib.sha256(b.encode("utf-8") if isinstance(b, str) else b).hexdigest()


def rel(p: Path) -> str:
    try:
        return str(p.resolve().relative_to(REPO.resolve()))
    except ValueError:
        return str(p)


def template_text() -> str:
    t = TEMPLATE_PATH.read_text(encoding="utf-8")
    return t.split("=== PROMPT START ===", 1)[1].split("=== PROMPT END ===", 1)[0].strip() + "\n"


def ai_visible_config(part: str) -> dict:
    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return {"common": cfg["ai_visible"]["common"], PARTS[part]: cfg["ai_visible"][PARTS[part]]}


def dialect_summary(part: str) -> str:
    d = json.loads(DIALECT_PATH.read_text(encoding="utf-8"))
    key = "lathelab" if part == "lathe" else "milllab"
    x = d[key]
    g = ", ".join(f"G{int(v):02d}" if float(v).is_integer() else f"G{v}" for v in sorted(x["supported_g"]))
    m = ", ".join(f"M{int(v):02d}" for v in sorted(x["supported_m"]))
    conv = "\n".join(f"- {k}: {v}" for k, v in x["conventions"].items() if isinstance(v, str))
    return (f"Simulator: {'LatheLab' if key == 'lathelab' else 'MillLab'} (static reading of the public source, "
            f"{d['source']['retrieved_on']}).\nSupported G-codes: {g}\nSupported M-codes: {m}\n"
            f"Unsupported G-code -> simulator error; unsupported M-code -> ignored.\n{conv}\n")


def mode_ii_manifest(part: str, include_feature_tree: bool = False) -> tuple[dict, list[str]]:
    m = json.loads((MANIFEST_DIR / f"{part}_manifest.json").read_text(encoding="utf-8"))
    removed = ["manufacturing_considerations (process hints; Mode I gets none)"]
    m.pop("manufacturing_considerations", None)
    if not include_feature_tree and "feature_tree" in m.get("extraction", {}):
        m["extraction"].pop("feature_tree")
        removed.append("extraction.feature_tree (designer's feature NAMES are not geometry)")
    ann = m.get("human_annotations", [])
    kept = [a for a in ann if a.get("approved_for_mode_II_prompt")]
    if len(kept) != len(ann):
        removed.append(f"{len(ann) - len(kept)} human annotation(s) not approved for Mode II")
    m["human_annotations"] = kept
    return m, removed


def reference_numbers(part: str) -> set[float]:
    p = REFERENCE_DIR / f"reference_features_{part}.json"
    nums: set[float] = set()
    for f in json.loads(p.read_text(encoding="utf-8"))["features"]:
        for d in f["dims"].values():
            for k in ("drawing_value", "cad_value"):
                v = d.get(k)
                if isinstance(v, (int, float)) and not isinstance(v, bool) and v >= 3:
                    nums.add(round(float(v), 4))
    return nums


def leaked_numbers(text: str, part: str) -> list[str]:
    """Reference dimensions (>= 3 mm) of this part appearing as free numbers in shared text.
    Markdown headings and list markers ('## 5.', '(iv)') are ignored."""
    refs = reference_numbers(part)
    body = "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))
    return sorted({tok for tok in NUM.findall(body) if round(float(tok), 4) in refs})


def isolation_allowlist(part: str) -> dict[str, str]:
    """Numbers that equal a reference dimension but are PROCESS values in the shared config (tool sizes, feeds,
    step-downs). Each entry needs a written reason in shared_experiment_config.json -> isolation_allowlist.
    Both modes receive these values identically, so they cannot favour one mode."""
    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return {k: v for k, v in cfg.get("isolation_allowlist", {}).get(PARTS[part], {}).items() if str(v).strip()}


def baseline_lines(part: str) -> list[str]:
    out = []
    for p in BASELINE_OF[part].rglob("*"):
        if p.is_file() and p.suffix.lower() in NC_SUFFIXES:
            for ln in p.read_text(encoding="utf-8", errors="replace").splitlines():
                s = re.sub(r"\([^)]*\)", "", ln).strip()
                if len(s) >= 12:
                    out.append(s)
    return out


def preflight(part: str) -> list[str]:
    problems = []
    cfg = ai_visible_config(part)[PARTS[part]]
    for k in REQUIRED_KEYS:
        v = cfg.get(k, {})
        if v.get("status") != "CONFIRMED" or v.get("class") in ("MISSING", "UNVERIFIED_ASSUMPTION"):
            problems.append(f"config {PARTS[part]}.{k} is {v.get('class')}/{v.get('status')} (Part B input needed)")
    if not any(p.suffix.lower() in NC_SUFFIXES for p in BASELINE_OF[part].rglob("*") if p.is_file()):
        problems.append(f"no human baseline NC file in {rel(BASELINE_OF[part])} - brief 2.5 requires the baseline BEFORE AI code")
    ref = json.loads((REFERENCE_DIR / f"reference_features_{part}.json").read_text(encoding="utf-8"))
    if ref.get("status") != "VERIFIED":
        problems.append("evaluation reference not yet verified at G1 (needed for metrics, not for generation)")
    return problems


def build_prompt(mode: str, part: str, include_feature_tree: bool = False) -> tuple[str, dict]:
    if mode not in ("I", "II") or part not in PARTS:
        raise ValueError("mode must be I|II and part lathe|milling")
    cfg = ai_visible_config(part)
    cfg_json = json.dumps(cfg, indent=1, ensure_ascii=False)
    inputs = [{"role": "template", "path": rel(TEMPLATE_PATH), "sha256": sha(TEMPLATE_PATH.read_bytes())},
              {"role": "shared_config", "path": rel(CONFIG_PATH), "sha256": sha(CONFIG_PATH.read_bytes()), "section": f"ai_visible.common + ai_visible.{PARTS[part]}"},
              {"role": "dialect", "path": rel(DIALECT_PATH), "sha256": sha(DIALECT_PATH.read_bytes())}]
    removed: list[str] = []
    attachments: list[dict] = []
    if mode == "I":
        img = DRAWING_INPUTS / DRAWING_OF[part]
        attachments.append({"role": "drawing_image_ATTACH_TO_CHAT", "path": rel(img), "sha256": sha(img.read_bytes())})
        desc = ("Mode: DRAWING. The geometry source is the attached dimensioned engineering drawing image (one A4 sheet: "
                "isometric view plus the orthographic/section views that carry the dimensions; first-angle projection). "
                "Read dimensions only from the dimension callouts.")
        geo = ("The drawing is attached to this message as an image. No other geometry data is provided.")
    else:
        man, removed = mode_ii_manifest(part, include_feature_tree)
        man_json = json.dumps(man, indent=1, ensure_ascii=False)
        mp = MANIFEST_DIR / f"{part}_manifest.json"
        inputs.append({"role": "cad_manifest (filtered, embedded below)", "path": rel(mp), "sha256": sha(mp.read_bytes()),
                       "embedded_sha256": sha(man_json), "removed_before_sending": removed})
        desc = ("Mode: CAD DATA. The geometry source is a machine-readable feature manifest extracted by a Python script "
                "from the Onshape CAD model (JSON below). Every value carries a label: CAD_EXTRACTED, "
                "GEOMETRICALLY_INFERRED, HUMAN_ANNOTATED or UNKNOWN. Coordinates are in the CAD frame (mm); "
                "you must transform them into the machine work frame given in the configuration.")
        geo = "```json\n" + man_json + "\n```"
    tpl = template_text()
    text = (tpl.replace("{{PART_ID}}", PARTS[part]).replace("{{PROCESS}}", "turning (2-axis lathe)" if part == "lathe" else "milling (3-axis vertical machining centre)")
            .replace("{{GEOMETRY_SOURCE_DESCRIPTION}}", desc).replace("{{SHARED_CONFIG_JSON}}", cfg_json)
            .replace("{{DIALECT_SUMMARY}}", dialect_summary(part)).replace("{{GEOMETRY_BLOCK}}", geo))
    iso = isolation_check(mode, part, text, cfg_json, tpl)
    ctx = {"mode": mode, "part": PARTS[part], "inputs": inputs, "attachments": attachments,
           "prompt_sha256": sha(text), "prompt_characters": len(text), "isolation": iso}
    return text, ctx


def isolation_check(mode: str, part: str, text: str, cfg_json: str, tpl: str) -> dict:
    checks = []

    def chk(name, ok, detail=""):
        checks.append({"check": name, "passed": bool(ok), "detail": detail})

    chk("no evaluation-reference ids or files", not re.search(r"\bR-[LM]-\d\d\b|evaluation_reference|reference_features", text))
    bl = [ln for ln in baseline_lines(part) if ln in text]
    chk("no human-baseline NC line in the prompt", not bl, f"{len(bl)} baseline line(s) found" if bl else f"{len(baseline_lines(part))} baseline lines compared")
    other = "II" if mode == "I" else "I"
    chk(f"no Mode {other} output referenced", f"mode_{other}".lower() not in text.lower() and f"Mode {other} output" not in text)
    if mode == "I":
        chk("Mode I: no manifest content", "apsd-cnc-feature-manifest" not in text and not re.search(r"\b[LM]-(OD|BORE|BOSS|PINS|WINDOW|KEYWAY|AXIS)\b", text))
    else:
        chk("Mode II: no drawing image or drawing file", ".png" not in text and "drawing_inputs" not in text and "instructor_sheet" not in text)
        chk("Mode II: manufacturing hints removed", '"manufacturing_considerations"' not in text)
    allow = isolation_allowlist(part)
    lk_all = leaked_numbers(cfg_json, part)
    lk_cfg = [n for n in lk_all if n not in allow]
    allowed_found = [n for n in lk_all if n in allow]
    lk_tpl = leaked_numbers(tpl, part)
    chk("shared config contains no reference dimension of this part", not lk_cfg,
        (f"numbers found: {lk_cfg}" if lk_cfg else "")
        + (f"; allowed process values (see isolation_allowlist): {allowed_found}" if allowed_found else ""))
    chk("template contains no reference dimension of this part", not lk_tpl, f"numbers found: {lk_tpl}" if lk_tpl else "")
    return {"passed": all(c["passed"] for c in checks), "checks": checks,
            "limits": "These checks prove what the PROMPT contains. They cannot prove what the chat model saw elsewhere; "
                      "that is controlled by the run protocol (new conversation, no Project, no memory, only the listed attachment)."}


def new_run_dir(mode: str, part: str) -> Path:
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    d = MODE_DIR[mode] / "prompts_and_logs" / "runs" / f"{stamp}_mode{mode}_{part}"
    d.mkdir(parents=True, exist_ok=False)
    return d


def write_run(mode: str, part: str, allow_pending: bool, include_feature_tree: bool = False) -> tuple[Path, list[str]]:
    problems = preflight(part)
    blocking = [p for p in problems if "evaluation reference" not in p]
    if blocking and not allow_pending:
        raise SystemExit("Preflight stopped the build:\n  - " + "\n  - ".join(problems)
                         + "\nResolve them, or re-run with --allow-pending to record them as accepted (disclosed) deviations.")
    text, ctx = build_prompt(mode, part, include_feature_tree)
    if not ctx["isolation"]["passed"]:
        raise SystemExit("Isolation check failed:\n" + json.dumps(ctx["isolation"], indent=1))
    d = new_run_dir(mode, part)
    (d / "prompt.md").write_text(text, encoding="utf-8")
    ctx.update({"run_id": d.name, "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                "preflight_problems": problems, "accepted_deviations": problems if allow_pending else [],
                "status": "PROMPT_READY - not yet sent"})
    (d / "input_manifest.json").write_text(json.dumps(ctx, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    (d / "isolation_check.json").write_text(json.dumps(ctx["isolation"], indent=1) + "\n", encoding="utf-8")
    return d, problems

