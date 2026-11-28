# Chapter 2 – Part E: Dual-mode generative-AI CNC programming (Team01)

**Research question (brief §2.7).** How does the quality and reliability of AI-assisted CNC programming change when the
AI receives (I) a dimensioned engineering drawing or (II) machine-readable geometry extracted from CAD? Both modes use
the same part revision, stock, tools, reference frames and test criteria. The human programs from Parts C and D are the
baseline. Claude only *proposes and reviews*. The team owns geometry interpretation, cutting strategy, code approval and
simulation.

> **Status on 2026-11-26.** The Mode II CAD pipeline is working and the experiment tooling and documents are complete.
> **No AI programming attempt has been run yet.** They are blocked by inputs that belong to other parts of the
> assignment (see [Outstanding human tasks](#outstanding-human-tasks)). Everything not yet measured is marked
> `NOT_RUN`, `NOT_MEASURED`, `PENDING_SIMULATION`, `PENDING_HUMAN_REVIEW` or `MISSING_DEPENDENCY`.

## Where things are

| Folder | Brief section | Contents |
|---|---|---|
| [05_AI_Mode_I_Drawing/](05_AI_Mode_I_Drawing/README.md) | 2.7.1 | Drawing inputs (300 dpi + SHA-256), run protocol, prompts/replies per run, `lathe/` and `milling/` (`initial/`, `revisions/`, G1 worksheet, operation plan) |
| [06_AI_Mode_II_CAD/](06_AI_Mode_II_CAD/README.md) | 2.7.2 | **CAD extractor** (`extractor_and_manifest/`: scripts, schema, live evidence, manifests, tests), prompts/replies per run, `lathe/` and `milling/` |
| [07_Comparison_Validation/](07_Comparison_Validation/README.md) | 2.7.3, Q2.11–Q2.14 | Shared experiment config, simulator dialect, evaluator-only reference, tools (prompt builder, importer, NC checker, metrics, export), six-case matrix, revision log, review records, simulation evidence, methodology, error analyses, answers |

## Architecture (as implemented)

```mermaid
flowchart LR
  subgraph CAD["06 Mode II - CAD data"]
    OS[(Onshape document<br/>APSD-LATHE-Final, APSD-MILLING)] -->|read-only GET, HMAC-signed<br/>vendored Chapter 1 client| EV[evidence/&lt;run&gt;_part/<br/>sanitised JSON + SHA-256]
    EV --> LP[Chapter 1 rotational parser<br/>+ OPITZ fact builder<br/>vendored unchanged]
    EV --> PP[prismatic.py<br/>2.5D section-loop analysis]
    LP --> CM[cnc_manifest.py<br/>labels + evidence pointers]
    PP --> CM
    CM --> MF[manifests/lathe_manifest.json<br/>manifests/milling_manifest.json<br/>schema-validated]
  end
  subgraph DRW["05 Mode I - drawing"]
    PDF[Instructor sheets 2 and 3<br/>brief PDF p.25/26] --> IMG[drawing_inputs/*.png 300 dpi<br/>+ SHA-256]
  end
  CFG[07 shared_experiment_config.json<br/>+ simulator_dialect.json<br/>+ prompt_template.md] --> PB
  MF -->|filtered: no process hints,<br/>no feature names, approved annotations only| PB
  IMG -->|attachment| PB
  PB[apsd_part_e build-prompt<br/>preflight + isolation checks] --> P[prompts_and_logs/runs/&lt;run&gt;/prompt.md]
  P -->|new claude.ai chat, operator| AI((Claude))
  AI -->|reply.txt| IM[apsd_part_e import-response<br/>write-once archive]
  IM --> INI[lathe|milling/initial/&lt;run&gt;/*.nc]
  IM --> SC[nc_check: static checks]
  IM --> RR[human_review_records/<br/>G1-G4 PENDING]
  INI -->|human or AI correction| REV[revisions/vNN_*.nc<br/>+ program_revision_log.csv]
  RR --> SIM[LatheLab / MillLab<br/>manual run by the team]
  SIM --> SE[simulation_evidence/.../simulation_log.json]
  REF[evaluation_reference/<br/>EVALUATOR ONLY] --> MET
  RR --> MET[apsd_part_e matrix]
  SE --> MET
  MET --> MX[six_case_matrix.csv]
```

## Environment setup (macOS / Linux, Python ≥ 3.11; tested with 3.13)

```bash
cd 06_AI_Mode_II_CAD/extractor_and_manifest
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt            # requests, python-dotenv, jsonschema, pytest (pinned)
cp .env.example .env                        # add Onshape API keys - never commit .env
```
Only the extractor needs network access and keys. The 07 tools use the same virtual environment (standard library + jsonschema).
**No paid API is used.** Claude is used through the claude.ai web chat, as in Chapter 1.

## Commands

| Step | Command (from the folder shown) |
|---|---|
| Check keys/targets (values never shown) | `scripts$ python -m apsd_cam check-env [--env-file PATH]` |
| Extract CAD (read-only) | `scripts$ python -m apsd_cam extract --part all [--env-file PATH]` |
| Build + validate manifests | `scripts$ python -m apsd_cam manifest --part all` |
| Inspect a manifest | `scripts$ python -m apsd_cam summary --part milling` |
| Extractor tests (offline) | `extractor_and_manifest$ python -m pytest -q tests` |
| Experiment status | `07_Comparison_Validation/tools$ python -m apsd_part_e status` |
| Build one prompt | `tools$ python -m apsd_part_e build-prompt --mode I --part lathe` |
| Archive a reply | `tools$ python -m apsd_part_e import-response <run_dir> <reply.txt> --model "<selector name>" --operator "<name>"` |
| Store a correction | `tools$ python -m apsd_part_e revise <initial .nc> <corrected .nc> --author-type human --author "<name>" --reason "..."` |
| Static NC checks | `tools$ python -m apsd_part_e nc-check <files> [--dialect lathelab\|milllab]` |
| Recompute the six-case matrix | `tools$ python -m apsd_part_e matrix` |
| Tools tests (offline) | `tools$ python -m pytest -q tests` |
| Export submission copy | `tools$ python -m apsd_part_e export ~/Desktop/submission` (copy only; renames 03/04 to `*_Human` in the copy) |

## Reproducing the four AI programming attempts

1. **Prerequisites (human):** Part B route/tool sheets approved → copy stock, tools, cutting data, setups, work zeros and
   clearances into `07_Comparison_Validation/experiment_config/shared_experiment_config.json` (status `CONFIRMED`,
   class `HUMAN_APPROVED`). Commit the human baselines in `03_Lathe/` and `04_Mill/` **before** any AI run (brief §2.5).
   Decide which drawing Mode I uses (instructor sheet vs team drawing of named version Ch2-Final). The manifests are
   already extracted from Ch2-Final, which is the default target.
2. `python -m apsd_part_e build-prompt --mode I --part lathe` (repeat for `--mode I --part milling`, `--mode II --part lathe`,
   `--mode II --part milling`). The builder refuses while inputs are missing. It also runs the isolation checks and records
   the hash of every input in `input_manifest.json`.
3. For each run, open a **new** claude.ai conversation (no Project, memory off, nothing else attached). Note the model name
   from the selector. For Mode I attach the listed drawing PNG. Paste `prompt.md` as one message and save the full reply
   as `reply.txt` in the run folder.
4. `python -m apsd_part_e import-response ...`. This writes the initial files once, runs the static checks, logs the
   revision and creates the G1–G4 review records.
5. The team completes G1 (fill the `reference_mapping` in `<mode>/<part>/recognized_features.json`), G2, G3, and G4
   (simulate, then fill `simulation_evidence/.../simulation_log.json`), and stores corrections with `revise`.
6. `python -m apsd_part_e matrix`, then update the analyses in `07_Comparison_Validation/` with observed values only.

## Simulator configuration (LatheLab / MillLab)

The dialect was read from the simulator's public source on 2026-11-26 (`07_Comparison_Validation/experiment_config/simulator_dialect.json`,
with SHA-256 of the pages). Key conventions:

- **LatheLab:** X is a **diameter** (X0 = spindle centre line); Z0 is normally the finished front face and −Z points to the
  chuck. U/W are incremental. **`G90` is the OD turning box cycle, not "absolute mode", and `G91` is not supported.**
  `T0101` = tool 01 / offset 01. Use `G50 S..` before `G96`. Threading: G76/G92/G32 with G97. Rear tool post.
  Stock dialog: diameter, length, bore, face allowance, grip length, material.
- **MillLab:** G54 is set at the chosen top corner (default front-left) with Z0 on the finished top (default). Use
  `G43 Hnn` (or enable AUTO TOOL COMP and document it). `G41/G42 Dnn` is simulated only in G17. Canned cycles
  G73/G74/G76/G81–G86/G89 with G80. M06 tool change. Stock is a rectangular block only. Use one run per setup.
- Enter the Part B stock and tools in **Stock / Workpiece** and **Tools & offsets** before every run, and keep the program
  version (hash) with each screenshot.

## Approval gates G1–G4

The checklist is in [07_Comparison_Validation/human_review_checklist.md](07_Comparison_Validation/human_review_checklist.md).
There is one record per AI program in `07_Comparison_Validation/human_review_records/`. The tools create every record as
`PENDING_HUMAN_REVIEW` / `PENDING_SIMULATION` with `reviewer: null`. Only a team member may set `APPROVED`, `REJECTED` or
`REQUIRES_CORRECTION`, with their name and date. Claude may write suggestions only in `ai_review_suggestion`.

## Tests (run on 2026-11-26)

- `06_AI_Mode_II_CAD/extractor_and_manifest/tests`: **33 passed**. These are integration tests on the real Onshape
  evidence (values, reproducibility, every evidence pointer resolves, hashes) plus synthetic B-rep unit tests and
  vendor/secret checks.
- `07_Comparison_Validation/tools/tests`: **32 passed** (2026-11-28). These cover the NC checker on synthetic snippets, isolation for
  the four real prompts, write-once archiving, revision preservation and the metric definitions.

Synthetic fixtures are labelled as such. They test the software, not the parts.

## Outstanding human tasks

| # | Task | Owner (part) | Blocks |
|---|---|---|---|
| 1 | ~~Copy Part B values into the shared config~~ done 2026-11-28 from `02_Process_Plans/` (stock, material, work zeros, tools, speeds/feeds). Still open: **safety clearances** (both), setup 2 grip/datum/simulation stock (both), part position in the milling block, lathe T05/T09 reach, lathe internal thread (M14×1 vs CAD M14×2) | Part B | all 4 AI attempts |
| 2 | Write and commit the human lathe and milling baselines (03_Lathe, 04_Mill) | Parts C/D | AI attempts (brief §2.5), baseline rows of the matrix |
| 3 | ~~Named version, `onshape_link.txt`, drawing PDFs~~ done 2026-11-28 (**Ch2-Final**). Still open: fix the lathe drawing title block (says inches, Letter size) | Part A | Mode I team drawing |
| 4 | Choose the Mode I drawing (instructor sheet or team drawing) | Part E | Mode I attempts |
| 5 | Verify the evaluation reference (`evaluation_reference/*.json`) against the drawing, especially the open readings (lathe "2", and "20"/"21" on the instructor sheet) | Part E | metrics |
| 6 | Decide whether human annotation `H-L-01` may be sent in Mode II (default: not sent) | Part E | Mode II lathe |
| 7 | Run the four attempts, G1–G4 reviews and simulations; log effort in `effort_log.csv` | Part E | Q2.11, Q2.13, Q2.14 |
| 8 | Extend the root `.gitignore` (it only lists `.DS_Store`; `.DS_Store` is still tracked) with `.env`, `.venv/`, `__pycache__/`. No credential was found in this repository; the extractor folder has its own `.gitignore` | all | hygiene |

## AI-use disclosure

See [07_Comparison_Validation/ai_use_disclosure.md](07_Comparison_Validation/ai_use_disclosure.md). In short:
the tooling, documents and draft reference in 05/06/07 were prepared with **Claude Code (Anthropic), model id
`claude-opus-5-5`, VS Code extension, 2026-11-26**, under the supervision of a team member. No AI-generated NC program
exists in the repository yet. Contextual prompting is used; no model was fine-tuned.
