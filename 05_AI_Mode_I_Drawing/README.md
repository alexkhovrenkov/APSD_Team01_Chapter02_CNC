# 05 – Mode I: drawing-driven NC generation (brief §2.7.1)

In Mode I the AI receives **only the dimensioned drawing** of the workpiece, plus the shared configuration (machine, dialect,
units, stock, tools, datum, output format). It receives no CAD manifest, no human baseline and no Mode II output.

| Path | Contents | Status 2026-11-26 |
|---|---|---|
| [drawing_inputs/](drawing_inputs/README.md) | 300 dpi renders of instructor sheets 2 (milling) and 3 (lathe) with SHA-256 and the reason the orthographic/section views are included | ready; choice of sheet PENDING_HUMAN_REVIEW |
| [prompts_and_logs/](prompts_and_logs/README.md) | Run protocol; `runs/<UTC>_modeI_<part>/` = exact prompt, input manifest, isolation check, raw reply, run metadata | no run yet |
| `lathe/`, `milling/` | `initial/<run>/` (AI files, write-once), `revisions/` (vNN corrections), `recognized_features.json` (G1 worksheet), `operation_plan.md` | NOT_YET_GENERATED |

The prompt is built from the same template as Mode II
([07 …/prompt_template.md](../07_Comparison_Validation/experiment_config/prompt_template.md)). It tells the model to read
dimensions only from callouts, never from image scale, and to list unclear or missing dimensions instead of inventing them.

**Known drawing gaps (draft, to verify at G1).** The following are not dimensioned on the sheets: the milling boss centre
distance, the R115/R60 arc centres, the pin and hole pitch-circle diameters (the milling sheet gives only "23" in B-B), the
internal thread pitch, and the meaning of the lathe "2" and "20/21/25" callouts. A correct Mode I answer must flag them.
These checks are planned for Q2.11.

How to run: see [README_Part_E.md](../README_Part_E.md#reproducing-the-four-ai-programming-attempts).
