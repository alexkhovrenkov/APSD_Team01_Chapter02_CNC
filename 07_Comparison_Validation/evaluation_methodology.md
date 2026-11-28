# Evaluation methodology – six-case comparison (brief Table 2.4, Q2.13)

The same measures are applied to the six cases (2 workpieces × manual baseline / Mode I / Mode II).
`python -m apsd_part_e matrix` computes [six_case_matrix.csv](six_case_matrix.csv) **only from recorded files**.
A value that has not been recorded is written as `NOT_MEASURED`, `NOT_RUN`, `PENDING_SIMULATION`,
`PENDING_HUMAN_REVIEW` or `MISSING_DEPENDENCY`. Nothing is estimated.

## Controlled variables
Same CAD snapshot for both parts (`4d05edae182b19aa4ea1f30d`; a named version is recommended), the same `ai_visible`
configuration, the same template and dialect summary (SHA-256 per run), the same output format, a new conversation per
attempt, and the first imported attempt counts as the *initial* proposal. Only the geometry block differs between the modes.

## Measures

| Measure | Definition | Source |
|---|---|---|
| Input coverage | What the AI received: Mode I = drawing sheet; Mode II = N manifest features / relationships / UNKNOWN items | run `input_manifest.json`, manifest |
| Recognized-feature coverage | correct ÷ applicable reference features. Correct = G1 outcome `CORRECT`, or `FLAGGED_AS_UNCLEAR` when the reference marks the item as not dimensioned in that mode's input (`drawing_dimensioned=false`, Mode I). `PARTIAL`, `INCORRECT`, `MISSED` and `INVENTED_VALUE` are not correct and are listed separately. | `<mode>/<part>/recognized_features.json` + `evaluation_reference/` (must be verified first) |
| Dimensional discrepancy | \|AI value − reference value\| in mm for every compared dimension; report n, mean, max and the count > 0.05 mm | same worksheet |
| Program issues and severity | static findings of the **initial** programs (critical / major / minor) + issues recorded at G1–G4 | `initial/<run>/automatic_checks.json`, review records |
| Simulator-validated operations | operations with `PASS` in `simulation_evidence/<part>/<case>/simulation_log.json` **and** an existing screenshot | simulation log |
| Failed / unsupported operations | entries `FAIL`, `PARTIAL`, `UNSUPPORTED` + operations marked `simulator_supported: false` | simulation log, operation plan |
| Human corrections | revisions in `program_revision_log.csv` with `author_type = human` (AI-authored revisions counted separately) | revision log |
| Human intervention count | gate decisions with a reviewer (`APPROVED`, `REJECTED`, `REQUIRES_CORRECTION`) + human revisions | review records, revision log |
| Development effort | minutes from `effort_log.csv`, split into `data_preparation`, `ai_generation`, `correction`, `human_review`, `simulation`. Start/end are written down **at the time** (local clock); no reconstructed times | effort log |
| Final validation status | all G4 `APPROVED` → approved; any `REJECTED` → rejected; otherwise pending | review records |

## Severity classification
- **critical**: the simulator would alarm or stop, or the geometry is certainly wrong (feed move without F, arc without or
  with an impossible radius, unsupported G-code, inch units, X and U in one block).
- **major**: likely wrong part, collision risk, or rejection at a gate (feed with the spindle off, no tool, G00 inside the
  stock, diameter/radius error, arc radius mismatch, compensation active at a tool change or G28, G90 misused as absolute
  mode on the lathe, wrong feature type, invented dimension used in code).
- **minor**: tolerated by the simulator but poor practice (no M30, compensation not cancelled at the end, G96 without G50,
  no safe start line, no final retract, tool offset 00).
- **info**: observations only, not counted as issues.

## Static checks vs simulation vs real machining
`nc_check` reads the text (dialect rules taken from the simulator source). It **cannot** show remaining material or
collisions with fixtures. Only LatheLab/MillLab runs (G4) produce simulator evidence. Neither replaces physical
validation; no program is run on a machine in this project.

## Baseline rows
The manual baseline is measured with the same static checks and the same simulation log. Its feature coverage is
`NOT_MEASURED` unless the Part C/D owners fill a baseline coverage worksheet; they are human-authored, so "human
corrections" is not applicable.
