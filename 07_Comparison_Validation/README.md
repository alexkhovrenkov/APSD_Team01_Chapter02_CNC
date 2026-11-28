# 07 – Comparison and validation (brief §2.7.3, Q2.11–Q2.14)

| Path | Purpose | Status 2026-11-26 |
|---|---|---|
| [experiment_config/](experiment_config/) | `shared_experiment_config.json` (identical AI-visible inputs for both modes), `simulator_dialect.json` (from the simulator source), `prompt_template.md` | config BLOCKED on Part B values |
| [evaluation_reference/](evaluation_reference/) | **evaluator only**: reference features (drawing reading + CAD value) defining coverage and dimension errors. The prompt builder rejects any of its content | draft, PENDING_HUMAN_REVIEW |
| [tools/](tools/) | `apsd_part_e`: build-prompt (preflight + isolation), import-response (write-once), revise, nc-check (static), matrix, export; 31 tests | working |
| [six_case_matrix.csv](six_case_matrix.csv) | Table 2.4, generated from records | MISSING_DEPENDENCY / NOT_RUN |
| [program_revision_log.csv](program_revision_log.csv) | append-only log of every AI/human program version | header only |
| [effort_log.csv](effort_log.csv) | observed minutes per case and activity | header only |
| [human_review_checklist.md](human_review_checklist.md), [human_review_records/](human_review_records/README.md) | gates G1–G4 | no AI program yet |
| [simulation_evidence/](simulation_evidence/) | `<lathe|milling>/<manual|mode_I|mode_II>/simulation_log.json` + screenshots; template at the top level | PENDING_SIMULATION |
| [evaluation_methodology.md](evaluation_methodology.md) | definitions of every measure and the severity classes | complete |
| [Q2_11_to_Q2_14.md](Q2_11_to_Q2_14.md), [turning_error_analysis.md](turning_error_analysis.md), [milling_error_analysis.md](milling_error_analysis.md) | answers / templates | Q2.12 answered; others NOT_RUN |
| [requirements_traceability.md](requirements_traceability.md) | audit, requirement → file map, rubric status | complete |
| [ai_use_disclosure.md](ai_use_disclosure.md) | AI use for this work and for the attempts | complete for the tooling |

Run commands: see [README_Part_E.md](../README_Part_E.md#commands). The PDF versions required by the brief
(`human_review_checklist.pdf`) should be exported from these Markdown sources when the content is final.
