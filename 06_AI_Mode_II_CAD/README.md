# 06 – Mode II: CAD-data-driven NC generation (brief §2.7.2)

In Mode II the AI receives **structured geometric facts extracted from the team's Onshape model** (the course's option iii,
Onshape API + Python) instead of a drawing. It also gets the same shared configuration and template as Mode I, and no
drawing, no human baseline and no Mode I output.

| Path | Contents | Status 2026-11-26 |
|---|---|---|
| [extractor_and_manifest/](extractor_and_manifest/README.md) | `scripts/apsd_cam` (new) + `scripts/vendor_ch1` (Chapter 1 pipeline, unchanged), schema, live evidence, manifests, tests | **working**; both manifests generated from live CAD data and schema-valid; 33 tests pass |
| `prompts_and_logs/` | `runs/<UTC>_modeII_<part>/`, same run protocol as [05](../05_AI_Mode_I_Drawing/prompts_and_logs/README.md) | no run yet |
| `lathe/`, `milling/` | `initial/<run>/`, `revisions/`, `recognized_features.json` (G1 worksheet), `operation_plan.md` | NOT_YET_GENERATED |

**What the AI receives in Mode II.** `manifests/<part>_manifest.json` with three things removed by the prompt builder (each
removal is recorded in the run's `input_manifest.json`):

1. `manufacturing_considerations`: process hints computed by our extractor. Mode I gets no such hints.
2. `extraction.feature_tree`: the designer's feature names (e.g. "Z-10-Pins"). These are words, not geometry.
3. Human annotations that the team has not approved for Mode II. Currently that is `H-L-01`, the verified thread reading
   from the drawing, which is **not sent** by default.
