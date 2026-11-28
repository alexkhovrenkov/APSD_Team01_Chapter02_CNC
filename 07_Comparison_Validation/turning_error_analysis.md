# Turning failure-and-correction sequence (APSD-LATHE) – Q2.14

**Status: NOT_RUN. No AI attempt exists yet, so no failure has been observed.** Fill this from one real, archived
failure. Do not construct or stage a failure to complete the report (brief §2.10).

| Step | Content | Evidence (paths, run id, line numbers, screenshots) |
|---|---|---|
| 1. Original prompt and input data | mode, run id, model name and date; drawing image or manifest hash | `0?_AI_Mode_*/prompts_and_logs/runs/<run>/prompt.md`, `input_manifest.json` |
| 2. Original AI output | quote the relevant feature, operation and NC lines unchanged | `<part>/initial/<run>/...` |
| 3. Discovered issue | what was wrong; gate (G1–G4); who found it (human, static check, LatheLab) | review record issue id |
| 4. Root cause | e.g. misread drawing callout, missing CAD semantics, dialect misunderstanding (LatheLab G90/X-diameter, MillLab G43/G41), wrong datum transform, invented dimension | |
| 5. Engineering consequence | effect on the part, tool or machine (dimension error in mm, gouge, collision, scrap) | |
| 6. Human decision | accept / edit and re-test / reject; name and date | review record `decision`, `reviewer`, `review_date` |
| 7. Corrected program | `revisions/vNN_...` with diff to the parent | `program_revision_log.csv` row |
| 8. Subsequent simulation result | LatheLab settings, Program-check messages, remaining material, conformance | `simulation_evidence/<part>/<mode>/simulation_log.json` + screenshots |
| 9. Lessons learned | prompt, pipeline or checklist change it led to | |
