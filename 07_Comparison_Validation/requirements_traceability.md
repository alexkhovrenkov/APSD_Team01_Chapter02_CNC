# Part E – repository audit and requirements traceability (2026-11-26)

## 1. Repository audit (before Part E work)

| Area | Found | Use for Part E |
|---|---|---|
| Git | `main`, 4 commits; only change: tracked `.DS_Store` modified | preserved; nothing committed by the tool |
| `EVALUATION.md` | TA-style evaluation prompt incl. Appendix B dimensions and an NC lint sketch | read; its rubric checklist E.1–E.4 is mapped below; its lint script was **not** reused because it treats G90 as absolute mode, which is wrong for LatheLab |
| 00–04 | **only `.gitkeep`** (no report, drawings, onshape_link, process plans, human NC) | dependencies MISSING (see §3) |
| 05–07 | only `.gitkeep` | Part E implemented here |
| Brief PDF | outside the repo: `~/Downloads/APSD.Part 00. Fall 2026 MAIN Project-P2.pdf` (sha256 `965a9eff…`) | requirements source; drawing sheets pp. 25–26 |
| Chapter 1 repo | `~/APSD_Project_2026` (branch `juli-changes`, commit `17f6d60`): Onshape API pipeline (read-only HMAC client, extraction, rotational parser, OPITZ manifest, 56 tests), Claude-chat handoff | **reused**: 9 modules vendored byte-identical into `06/.../scripts/vendor_ch1` |
| Onshape document (live, read-only, 2026-11-26) | tabs APSD-LATHE-Final (geometry identical to Chapter 1), **APSD-MILLING** + drawing, Assembly-Lathe-Milling + drawing | Mode II source for both parts |
| Simulator | public single-page apps (LatheLab, MillLab) | dialect extracted → `experiment_config/simulator_dialect.json` |
| Credentials | none in this repository; Chapter 1 `.env` (git-ignored) holds keys | used by path only, never printed |
| Extra-credit criteria (+10 %) | only the heading "+possible Extra (+10%)"; **no criteria found** in the brief or EVALUATION.md | none invented; see §4 |

## 2. Traceability: brief requirement → file → status

Statuses: COMPLETE · PARTIALLY_COMPLETE · BLOCKED · PENDING_HUMAN_REVIEW · PENDING_SIMULATION.

| Requirement (brief) | Where | Status |
|---|---|---|
| 2.7 AI system disclosure (provider, model, date, modalities, settings, scripts) | `ai_use_disclosure.md`; per-run `run_meta.json` (automatic) | PARTIALLY_COMPLETE (tool use recorded; attempt records pending) |
| 2.7 same revision, stock, tools, frames, criteria | `experiment_config/shared_experiment_config.json`; identical-template test | BLOCKED (Part B values missing) |
| 2.7.1 drawing(s) + justified ortho/section views, logged | `05/drawing_inputs/` (+ `input_manifest.json`, justification) | PENDING_HUMAN_REVIEW (choice of sheet) |
| 2.7.1 machine, stock, coordinates, tools, units, datum, outputs in the prompt | `experiment_config/prompt_template.md`, `apsd_part_e build-prompt` | BLOCKED (stock/tools/datum pending) |
| 2.7.1 request (i)–(iv); flag unclear dimensions | prompt template "What to deliver", "Required response format" | COMPLETE |
| 2.7.1 verify each inferred feature before code | G1 worksheet `05/<part>/recognized_features.json`, checklist G1 | PENDING_HUMAN_REVIEW (no attempt yet) |
| 2.7.2 reproducible route, structured facts | `06/extractor_and_manifest/` (Onshape API + Python) | COMPLETE |
| 2.7.2 bounding boxes, centres, radii, axes, surfaces, placements | `manifests/*.json` (schema-valid, 33 tests) | COMPLETE |
| 2.7.3 attempt per mode × workpiece, even if it fails | `apsd_part_e build-prompt / import-response`; `05|06/<part>/initial/` | BLOCKED (0/4 run) |
| 2.7.3 record tools, setups, code changes, validation conditions | run folders, `program_revision_log.csv`, review records, `simulation_log` template | PARTIALLY_COMPLETE (mechanism ready, no data) |
| Table 2.4 six-case matrix, initial vs corrected separated | `six_case_matrix.csv` (generated), `evaluation_methodology.md` | PARTIALLY_COMPLETE (MISSING_DEPENDENCY / NOT_RUN) |
| G1–G4 gates for every AI program | `human_review_checklist.md`, `human_review_records/` | PENDING_HUMAN_REVIEW |
| Q2.11 | `Q2_11_to_Q2_14.md` §Q2.11 (pre-registered check points) | BLOCKED |
| Q2.12 | `Q2_11_to_Q2_14.md` §Q2.12, `06/extractor_and_manifest/README.md` | COMPLETE (team review pending) |
| Q2.13 | `Q2_11_to_Q2_14.md` §Q2.13, methodology | BLOCKED |
| Q2.14 | `turning_error_analysis.md`, `milling_error_analysis.md` | BLOCKED |
| Deliverables E: prompts + source images | `05/drawing_inputs/`, prompt template, runs/ | PARTIALLY_COMPLETE |
| Deliverables E: extractor + exported manifest | `06/extractor_and_manifest/` | COMPLETE |
| Deliverables E: initial AI NC files, both parts, both modes | `05|06/<part>/initial/` | BLOCKED |
| Deliverables E: revisions + approval records | `revisions/`, `program_revision_log.csv`, `human_review_records/` | BLOCKED |
| Deliverables E: completed evaluation table, two error analyses | `six_case_matrix.csv`, `*_error_analysis.md` | BLOCKED |
| 2.9 simulator evidence | `simulation_evidence/<part>/<case>/` + template | PENDING_SIMULATION |
| 2.11 submission layout | existing 00–07; `apsd_part_e export` creates the brief's names in a copy | COMPLETE (mechanism) |

## 3. Rubric (Part E, 20 marks) – what exists and what is still needed

| Criterion | Marks | State | Still needed (owner) |
|---|---|---|---|
| Drawing-based AI approach | 4 | inputs, template, protocol, G1 worksheet mechanism ready | Part B values; run Mode I ×2; G1 review (Part E) |
| Functioning structured CAD-data workflow | 6 | working end to end on live data from named version Ch2-Final; schema, tests, docs, Q2.12 | team review |
| Four AI attempts and transparent logs | 4 | write-once archive, hashes, revision log, metadata | baselines first (C/D), then 4 runs (E) |
| Comparative analysis and human verification | 6 | methodology, matrix generator, checklist, records, templates | attempts, reviews, simulations, effort log (E) |

## 4. Extra credit (+10 %)
No criteria are documented. Possibly relevant work that exists (not claimed as extra credit): a second, prismatic CAD
analyser beyond Chapter 1; a dialect-aware static checker derived from the simulator source; automatic isolation checks;
reproducibility tests on live evidence. Suggest asking the instructor what counts.

## 5. Dependencies on other parts

| Needed from | Item | Why |
|---|---|---|
| Part A | named Onshape version, `onshape_link.txt`, drawing PDFs, CAD exports | same-revision guarantee; Mode I team drawing option |
| Part B | stock, material, tools + offsets, cutting data, setups, datums, clearances | identical AI inputs to the baseline (EVALUATION.md E.3) |
| Parts C/D | committed human NC baselines + simulator setup logs | brief 2.5 order; baseline rows; comparison |
| Part F | report sections (6) and (8) referencing these files | final report |
