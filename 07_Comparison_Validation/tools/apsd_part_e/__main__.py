"""Part E experiment tools. Run from 07_Comparison_Validation/tools:

  python -m apsd_part_e status
        dependency and attempt status for the six cases
  python -m apsd_part_e build-prompt --mode I|II --part lathe|milling [--allow-pending]
        preflight + isolation checks -> 05|06/prompts_and_logs/runs/<run>/prompt.md (+ input_manifest.json)
  python -m apsd_part_e import-response RUN_DIR REPLY_FILE --model "<as shown in the model selector>" --operator "<name>"
        archive the reply WRITE-ONCE, split NC files into <part>/initial/<run>/, static checks,
        revision log row and G1-G4 review records (all PENDING_HUMAN_REVIEW)
  python -m apsd_part_e revise PARENT_NC NEW_FILE --author-type human|AI --author "<name>" --reason "..." [--model ..] [--review-record ..]
        store a corrected program as <part>/revisions/vNN_<name> (parent untouched)
  python -m apsd_part_e nc-check FILE... [--dialect lathelab|milllab]
        static checks (NOT a simulation)
  python -m apsd_part_e matrix
        recompute 07_Comparison_Validation/six_case_matrix.csv from the records
  python -m apsd_part_e export OUT_DIR
        copy the repo into the brief's ZIP layout outside the repository
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .paths import BASELINE_OF, MODE_DIR, NC_SUFFIXES, PARTS, REFERENCE_DIR
from .prompts import preflight, rel


def cmd_status(_a):
    for part in PARTS:
        files = [p for p in BASELINE_OF[part].rglob("*") if p.is_file() and p.suffix.lower() in NC_SUFFIXES]
        print(f"{PARTS[part]}: human baseline files in {rel(BASELINE_OF[part])}: {len(files)}")
        ref = json.loads((REFERENCE_DIR / f"reference_features_{part}.json").read_text(encoding="utf-8"))
        print(f"  evaluation reference: {ref['status']}")
        for mode in ("I", "II"):
            runs = sorted((MODE_DIR[mode] / "prompts_and_logs" / "runs").glob(f"*_mode{mode}_{part}"))
            imported = [r for r in runs if (r / "run_meta.json").exists()]
            print(f"  Mode {mode}: {len(runs)} prompt(s) prepared, {len(imported)} imported")
        for p in preflight(part):
            print(f"  PREFLIGHT: {p}")


def cmd_build_prompt(a):
    from .prompts import write_run

    d, problems = write_run(a.mode, a.part, a.allow_pending, a.include_feature_tree)
    ctx = json.loads((d / "input_manifest.json").read_text(encoding="utf-8"))
    print(f"Prompt ready: {rel(d / 'prompt.md')} ({ctx['prompt_characters']:,} characters), isolation checks passed")
    if problems:
        print("Accepted deviations (disclosed in input_manifest.json):\n  - " + "\n  - ".join(problems))
    att = ctx["attachments"]
    print(f"""
1. Open a NEW claude.ai conversation (no Project, memory off, no other files).
2. Note the model name exactly as shown in the model selector.
3. {'Attach ' + att[0]['path'] + ' (check sha256 ' + att[0]['sha256'][:12] + '...) and paste' if att else 'Paste'} the whole prompt.md as ONE message.
4. Save the complete reply as {rel(d / 'reply.txt')}
5. python -m apsd_part_e import-response {rel(d)} {rel(d / 'reply.txt')} --model "<model>" --operator "<name>"
""")


def cmd_import(a):
    from .runs import import_response

    meta = import_response(Path(a.run_dir), Path(a.reply_file), a.model, a.operator, a.date, a.interface, a.conversation_ref)
    print(json.dumps({k: meta[k] for k in ("run_id", "model_designation", "date_of_use", "parse_problems", "initial_dir")}, indent=1))
    for f in meta["extracted_files"]:
        print(f"  {f['file']}  static: {f['static_check_counts']}")


def cmd_revise(a):
    from .runs import register_revision

    d = register_revision(Path(a.parent), Path(a.new_file), a.author_type, a.author, a.reason, a.model, a.review_record)
    print(f"revision stored: {rel(d)} (parent unchanged, logged in program_revision_log.csv)")


def cmd_nc_check(a):
    from .nc_check import check_file

    worst = 0
    for f in a.files:
        r = check_file(Path(f), a.dialect)
        print(f"{f}  [{r['dialect']}, {r['kind']}]  {r['counts']}  extents {r.get('extents')}")
        for x in r["findings"]:
            print(f"   {x['severity']:8s} L{x['line'] or '-':<5} {x['code']}: {x['message']}")
        worst = max(worst, 2 if r["counts"]["critical"] else 1 if r["counts"]["major"] else 0)
    sys.exit(worst if a.strict else 0)


def cmd_matrix(_a):
    from .metrics import build_matrix

    for r in build_matrix():
        print(f"{r['case']:38s} coverage={r['recognized_feature_coverage']!s:14s} NC={r['initial_nc_result']}")
    print("written: 07_Comparison_Validation/six_case_matrix.csv")


def cmd_export(a):
    from .export import export

    export(Path(a.out_dir), a.team, not a.no_zip)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m apsd_part_e", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status").set_defaults(fn=cmd_status)
    p = sub.add_parser("build-prompt")
    p.add_argument("--mode", choices=["I", "II"], required=True)
    p.add_argument("--part", choices=list(PARTS), required=True)
    p.add_argument("--allow-pending", action="store_true")
    p.add_argument("--include-feature-tree", action="store_true", help="Mode II: also send the designer's feature names")
    p.set_defaults(fn=cmd_build_prompt)
    p = sub.add_parser("import-response")
    p.add_argument("run_dir")
    p.add_argument("reply_file")
    p.add_argument("--model", required=True)
    p.add_argument("--operator", required=True)
    p.add_argument("--date")
    p.add_argument("--interface", default="claude.ai web chat (manual paste, new conversation)")
    p.add_argument("--conversation-ref")
    p.set_defaults(fn=cmd_import)
    p = sub.add_parser("revise")
    p.add_argument("parent")
    p.add_argument("new_file")
    p.add_argument("--author-type", choices=["human", "AI"], required=True)
    p.add_argument("--author", required=True)
    p.add_argument("--reason", required=True)
    p.add_argument("--model")
    p.add_argument("--review-record")
    p.set_defaults(fn=cmd_revise)
    p = sub.add_parser("nc-check")
    p.add_argument("files", nargs="+")
    p.add_argument("--dialect", choices=["lathelab", "milllab"])
    p.add_argument("--strict", action="store_true", help="exit 2 on critical, 1 on major findings")
    p.set_defaults(fn=cmd_nc_check)
    sub.add_parser("matrix").set_defaults(fn=cmd_matrix)
    p = sub.add_parser("export")
    p.add_argument("out_dir")
    p.add_argument("--team", default="Team01")
    p.add_argument("--no-zip", action="store_true")
    p.set_defaults(fn=cmd_export)
    a = ap.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
