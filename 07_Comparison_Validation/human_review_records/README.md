# Human review records

One JSON file per AI program version, named `<run_id>__<program>.json`. `apsd_part_e import-response` creates them with:

```json
"gates": {"G1_geometry":   {"status": "PENDING_HUMAN_REVIEW", "issues": [], "evidence": [], "recommended_correction": null,
                            "ai_review_suggestion": null, "decision": null, "reviewer": null, "review_date": null},
          "G2_process": {...}, "G3_code": {...}, "G4_simulation": {"status": "PENDING_SIMULATION", ...}}
```

How to complete a gate (team member):
1. Add issues as `{"id": "I01", "gate": "G3_code", "severity": "major", "description": "...", "evidence": "file:line or screenshot path", "recommended_correction": "...", "found_by": "human|static_check|simulator|ai_review"}`.
2. Set `status` to `APPROVED`, `REJECTED` or `REQUIRES_CORRECTION`, write a short `decision`, and fill in your
   **own** name and the date.
3. If corrected, store the new file with `python -m apsd_part_e revise ... --review-record <this file>` and give the
   revision its own record. You can copy this file, change `program_version` and reset the gates.

`ai_review_suggestion` may hold Claude's review comments. It never counts as a human decision. Records for the human
baselines (optional, e.g. G4 of the manual programs) use `"input_mode": "Manual baseline"`.

Status 2026-11-26: no records yet (no AI program exists).
