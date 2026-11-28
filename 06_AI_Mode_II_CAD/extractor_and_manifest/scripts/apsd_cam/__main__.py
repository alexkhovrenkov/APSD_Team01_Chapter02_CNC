"""Command line: run from 06_AI_Mode_II_CAD/extractor_and_manifest/scripts

  python -m apsd_cam check-env [--env-file PATH]
        which settings are present (never their values) and which Onshape tabs are targeted
  python -m apsd_cam extract --part lathe|milling|all [--auth hmac|basic|anonymous] [--env-file PATH]
        read-only Onshape API -> ../evidence/<run_id>_<part>/   (sanitized, hashed)
  python -m apsd_cam manifest --part lathe|milling|all [--evidence DIR]
        evidence (default: newest run of that part) -> ../manifests/<part>_manifest.json (schema-validated)
  python -m apsd_cam validate [FILES...]
        validate manifests against ../schemas/cnc_feature_manifest.schema.json
  python -m apsd_cam summary --part lathe|milling
        print the features of a manifest

Secrets: ONSHAPE_ACCESS_KEY / ONSHAPE_SECRET_KEY are read from the environment or from the
file given with --env-file (or $APSD_ENV_FILE, or ../.env). They are never printed or saved.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from pathlib import Path

from . import EVIDENCE_ROOT, EXTRACTOR_DIR, MANIFEST_DIR
from .targets import PARTS


def _load_env(path: str | None) -> str:
    from dotenv import load_dotenv

    cand = path or os.environ.get("APSD_ENV_FILE") or (str(EXTRACTOR_DIR / ".env") if (EXTRACTOR_DIR / ".env").exists() else None)
    if cand:
        if not Path(cand).exists():
            sys.exit(f"env file not found: {cand}")
        load_dotenv(cand, override=False)
        return f"loaded {Path(cand).name} (values not shown)"
    return "no env file; using process environment"


def _parts(arg: str) -> list[str]:
    return list(PARTS) if arg == "all" else [arg]


def cmd_check_env(args) -> None:
    print(_load_env(args.env_file))
    for name in ("ONSHAPE_ACCESS_KEY", "ONSHAPE_SECRET_KEY", "ONSHAPE_AUTH_MODE", "APSD_LATHE_URL", "APSD_MILLING_URL"):
        print(f"  {name:20s} {'set' if os.environ.get(name, '').strip() else 'not set'}")
    for k, tab in PARTS.items():
        t = tab.target()
        print(f"  {k:8s} -> {t.host} document={t.document_id} {t.wvm}={t.wvm_id} element={t.element_id} ({tab.expected_element_name})")


def cmd_extract(args) -> None:
    from apsd_pipeline.config import get_onshape_credentials  # vendored
    from apsd_pipeline.extract import run_extraction  # vendored

    print(_load_env(args.env_file))
    creds = get_onshape_credentials(args.auth)
    for k in _parts(args.part):
        tab = PARTS[k]
        tmp = EVIDENCE_ROOT / f".tmp_{k}"
        shutil.rmtree(tmp, ignore_errors=True)
        ev = run_extraction(tab.target(), creds, tmp, drawing_element_id=tab.drawing_element_id)
        final = EVIDENCE_ROOT / f"{ev.name}_{k}"
        if final.exists():
            sys.exit(f"{final} already exists; evidence is never overwritten")
        ev.rename(final)
        shutil.rmtree(tmp, ignore_errors=True)
        rec = json.loads((final / "extraction_record.json").read_text(encoding="utf-8"))
        if rec.get("element_name") != tab.expected_element_name:
            print(f"  WARNING: element name is '{rec.get('element_name')}', expected '{tab.expected_element_name}'")
        print(f"  {k}: evidence -> {final.relative_to(EXTRACTOR_DIR)}")
        time.sleep(1)  # distinct run ids


def latest_evidence(part: str) -> Path:
    eid = PARTS[part].target().element_id
    runs = []
    for r in sorted(EVIDENCE_ROOT.glob(f"*_{part}/extraction_record.json")):
        if json.loads(r.read_text(encoding="utf-8"))["target"]["element_id"] == eid:
            runs.append(r.parent)
    if not runs:
        sys.exit(f"No evidence for {part}. Run: python -m apsd_cam extract --part {part}")
    return runs[-1]


def cmd_manifest(args) -> None:
    from .cnc_manifest import BUILDERS, write

    for k in _parts(args.part):
        ev = Path(args.evidence).resolve() if args.evidence else latest_evidence(k)
        m = BUILDERS[k](ev)
        out = MANIFEST_DIR / f"{k}_manifest.json"
        write(m, out)
        labels: dict[str, int] = {}
        for f in m["features"]:
            labels[f["label"]] = labels.get(f["label"], 0) + 1
        print(f"{k}: {len(m['features'])} features {labels}, {len(m['relationships'])} relationships, "
              f"{len(m['missing_data'])} UNKNOWN items -> {out.relative_to(EXTRACTOR_DIR)} (schema-valid)")


def cmd_validate(args) -> None:
    from .cnc_manifest import validate

    files = [Path(f) for f in args.files] or sorted(MANIFEST_DIR.glob("*_manifest.json"))
    for f in files:
        validate(json.loads(f.read_text(encoding="utf-8")))
        print(f"valid: {f}")


def cmd_summary(args) -> None:
    m = json.loads((MANIFEST_DIR / f"{args.part}_manifest.json").read_text(encoding="utf-8"))
    print(f"{m['part']['id']}  revision {m['cad_source']['snapshot_microversion']}  run {m['extraction']['run_id']}")
    print(f"bbox {m['bounding_box']['min_mm']} .. {m['bounding_box']['max_mm']} mm")
    for f in m["features"]:
        print(f"  {f['id']:16s} [{f['label']:22s} {f['confidence']:6s}] {f['description']}")
    for r in m["relationships"]:
        print(f"  {r['id']:16s} {r['description']}: {r['value']} {r['unit'] or ''}")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="python -m apsd_cam", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("check-env")
    p.add_argument("--env-file")
    p.set_defaults(fn=cmd_check_env)
    p = sub.add_parser("extract")
    p.add_argument("--part", choices=["lathe", "milling", "all"], required=True)
    p.add_argument("--auth", choices=["hmac", "basic", "anonymous"])
    p.add_argument("--env-file")
    p.set_defaults(fn=cmd_extract)
    p = sub.add_parser("manifest")
    p.add_argument("--part", choices=["lathe", "milling", "all"], required=True)
    p.add_argument("--evidence")
    p.set_defaults(fn=cmd_manifest)
    p = sub.add_parser("validate")
    p.add_argument("files", nargs="*")
    p.set_defaults(fn=cmd_validate)
    p = sub.add_parser("summary")
    p.add_argument("--part", choices=["lathe", "milling"], required=True)
    p.set_defaults(fn=cmd_summary)
    args = ap.parse_args(argv)
    from apsd_pipeline.config import ConfigError

    try:
        args.fn(args)
    except ConfigError as exc:
        sys.exit(f"Configuration problem: {exc}")


if __name__ == "__main__":
    main()
