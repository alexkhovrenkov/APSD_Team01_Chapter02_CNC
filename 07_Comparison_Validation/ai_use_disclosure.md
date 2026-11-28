# AI-use disclosure – Part E (brief §2.7, §2.10)

## A. AI used to build the Part E workflow (not an experiment attempt)

| Item | Record |
|---|---|
| Provider | Anthropic |
| Model designation | `claude-opus-5-5` (as reported by the tool's own system information) |
| Interface | Claude Code, VS Code extension, operated by a team member on the team member's computer |
| Date of use | 2026-11-26 |
| Input modalities | text; images (rendered drawing sheets and crops, read to draft the evaluation reference) |
| Settings | tool defaults; no fine-tuning, no parameter training |
| What it did | inspected the repository, the brief PDF, the Chapter 1 pipeline and the simulator's public source; ran **read-only** Onshape API extractions with the team's existing keys (loaded from the Chapter 1 `.env` by path, never printed or copied); wrote `apsd_cam` (06), `apsd_part_e` (07), the schemas, configuration, templates, tests and documents; drafted `evaluation_reference/*.json` (status PENDING_HUMAN_REVIEW) |
| What it did **not** do | generate any NC program for the parts; run the four experiment attempts; run LatheLab/MillLab; record any human approval; modify 00–04 or the Chapter 1 repository |
| External scripts and libraries | PyMuPDF (scratch environment, to read the brief PDF and render the drawings), requests, python-dotenv, jsonschema, pytest; curl (simulator HTML) |
| Human verification | pending: the team must review the code, the reference draft and every statement in these documents before submission |

Because this assistant has seen the drawings, the CAD data and the reference draft, **it must not be used as the
generating model for the experiment attempts**. Its context is not isolated.

## B. AI used in the experiment (the four attempts)

To be recorded automatically per run in `05|06/prompts_and_logs/runs/<run>/run_meta.json`: provider, model name exactly
as shown in the chat's model selector, interface, date, operator, input modalities (Mode I: text + image; Mode II:
text), settings ("chat defaults"), prompt and reply SHA-256, extracted files.

Status 2026-11-26: **no attempt run.**

## C. Terminology
Configuring the model through system-like instructions, rules and examples in the prompt is **contextual prompting**,
not fine-tuning. No model weights were changed.
