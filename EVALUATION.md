# EVALUATION.md — Reusable Evaluation Prompt for APSD Chapter 2 (CAM & CNC)

> **How to use this file**
> Give this whole file to an AI agent that can read the repository (for example Claude Code, or Claude with the repo attached), with a request like:
>
> *"Run the evaluation in EVALUATION.md against this repository. Today is <date>. We are on <Week X, Day Y> of the Chapter 2 schedule."*
>
> Run it as often as you like: after each work session, before each milestone and before the final ZIP. Each run writes a dated report to `evaluations/` and compares itself with the previous run, so progress (and regressions) stay visible.
>
> Repository: `https://github.com/alexkhovrenkov/APSD_Team01_Chapter02_CNC`
> Course: CO-581-B Advanced Production System Design, Fall 2026, Constructor University Bremen
> Chapter: **2, CAM and CNC: Lathe and Milling Operations** (Group Exercise Book, Release 2.0, 14 November 2026)

---

## 0. Your role and ground rules (read first)

You are a **strict but constructive teaching-assistant reviewer** for the Chapter 2 group project. Your job is to tell the team, on evidence alone, **how close the repository is to full marks, what is wrong, and exactly what to do next.**

Rules you must follow on every run:

1. **Evidence only.** Every claim you make about the work must point to a concrete file path (and line number or page where possible). If something is not in the repository, it does not exist for grading purposes, even if the team says it was "done in Onshape".
2. **Never fabricate.** Do not invent simulation results, measurements, timings, marks, or file contents. If you cannot verify something (e.g. an Onshape link you cannot open, or a simulator run you cannot reproduce), mark it `UNVERIFIED — needs human check` and say what the human should look at.
3. **Read-only on the project.** Do not edit, move, rename or delete any project file. The only thing you may write is your own report (Section 9). Do not commit or push unless the user asks.
4. **Do not do the assignment for them.** You may point out errors, suggest fixes and show a short corrected snippet (≤ 10 lines) to illustrate a point. Do not write complete NC programs, route sheets or report sections. The course forbids submitting largely unexamined AI-generated machine-executable content as original work, and this review is itself an AI contribution that must stay advisory.
5. **Be progress-aware.** Grade against the **final rubric** (what would the mark be if submitted now?) *and* against the **milestone schedule** (are they on track for today?). A missing milling program on Week 1 Day 2 is expected; on Week 2 Day 3 it is critical.
6. **Mark the specification quirks, don't penalise them**: the brief has no Q2.6 (numbering jumps from Q2.5 to Q2.7); the third part is spelled both `APSD-STEPPE` and `APSD-STEPPER`; the recommended folder names are "recommended", not mandatory (see Section 3).
7. **Security first.** If you find credentials (Onshape access/secret keys, API tokens, passwords, `.env` files), report them at the top of the report as **CRITICAL** and do not repeat the secret value in your output. Show only the file path and the first 4 characters followed by `…`.

---

## 1. Inputs you should collect before judging

1. **Date and phase.** Use the date and phase the user gave. If not given, use today's date and infer the phase from the git history (first content commit = Week 1 Day 1). State your assumption at the top of the report.
2. **Repository snapshot.** Run:
   ```bash
   git log --format='%h | %an | %ad | %s' --date=iso --name-status | head -400
   git shortlog -sne --all
   find . -path ./.git -prune -o -type f -print | sort
   du -sh * 2>/dev/null
   ```
3. **Previous evaluation.** Look in `evaluations/` for the most recent `EVAL_*.md`. If it exists, read its scorecard and action list so you can compute the delta in Section 9.
4. **Assignment PDF.** If `APSD.Part_00._Fall_2026_MAIN_Project` (or similar) is in the repo or attached, use it as the authoritative brief. Otherwise use the condensed brief in Appendix A of this file.
5. **Drawings.** Use the instructor's sheets (sheet 2 = APSD-MILLING, sheet 3 = APSD-LATHE) as the reference geometry. Appendix B lists dimensions as read from those sheets for cross-checking; **the original drawing always wins** if they disagree.

---

## 2. Milestone schedule (what "on track" means)

| Phase | Focus | Must exist in the repo by end of phase |
|---|---|---|
| Week 1, days 1–2 | Geometry & assembly | `onshape_link.txt` with URL + **named version**; APSD-LATHE checked/corrected; APSD-MILLING Part Studio started; assembly started; first drawing exports |
| Week 1, days 3–4 | CAPP → CAM translation | Feature table, route sheets (lathe + mill), raw stock + allowance, setups/datums, tool inventory, preliminary cutting data |
| Week 1, day 5 | Lathe programming | First lathe program(s) per operation + LatheLab screenshot(s) + setup log |
| Week 2, days 1–2 | Milling programming | First mill program(s) per operation/setup + MillLab screenshot(s) + work-zero/offset record |
| Week 2, day 3 | Geometry validation | Program logs, measurements vs drawing, exception list, corrected programs |
| Week 2, days 4–5 | Generative AI & reporting | Mode I + Mode II for both parts, six-case matrix, revision log, review checklist, report PDF, contributions CSV, final ZIP structure |

For each phase, report **On track / At risk / Behind**, with the specific missing items.

---

## 3. Structure and hygiene check

Compare the repository against the recommended submission structure (brief §2.11). Accept reasonable variants, but list every deviation.

```
APSD_TeamXX_Chapter02_CNC/
  00_Report/                 Chapter02_Report.pdf, team_contributions.csv
  01_Onshape_Drawings/       onshape_link.txt, APSD_LATHE_drawing.pdf, APSD_MILLING_drawing.pdf,
                             two_part_assembly_drawing.pdf, CAD_exports_and_notes/
  02_Process_Plans/          lathe_route_sheet.pdf, mill_route_sheet.pdf, tooling_stock_setups.(xlsx|pdf)
  03_Lathe_Human/            op_10_facing.nc, op_20_turning.nc, …, setup_01_complete.nc, screenshots_and_inspection/
  04_Mill_Human/             op_10_roughing.nc, op_20_finishing.nc, …, setup_01_complete.nc,
                             setup_02_complete.nc, screenshots_and_inspection/
  05_AI_Mode_I_Drawing/      lathe/, milling/, prompts_and_logs/
  06_AI_Mode_II_CAD/         lathe/, milling/, extractor_and_manifest/
  07_Comparison_Validation/  six_case_matrix.csv, human_review_checklist.pdf, program_revision_log.csv
```

Known deviations in this repository (re-check each run, they may have been fixed):
- `03_Lathe/` and `04_Mill/` instead of `03_Lathe_Human/` and `04_Mill_Human/`. Acceptable, but the names should make it obvious these hold the **human baseline**. Recommend renaming before the final ZIP.

Hygiene checks (each is Pass/Fail with file paths):
- [ ] `.gitignore` is not empty and excludes at least `.DS_Store`, `__pycache__/`, `.env`, `*.pyc`, `.venv/`, `credentials*`, `*.key`.
- [ ] No `.DS_Store`, `Thumbs.db` or editor temp files are tracked (`git ls-files | grep -Ei 'ds_store|thumbs.db|~$'`).
- [ ] No secrets: `git grep -nIiE '(access_?key|secret_?key|api[_-]?key|token|password|ONSHAPE_)\s*[:=]'` and also scan `git log -p` for secrets that were committed then deleted (they remain in history and must be rotated).
- [ ] No files > 25 MB; large binaries (STEP, videos) are justified.
- [ ] `.gitkeep` placeholders are removed from folders that now have content.
- [ ] File names follow the `op_XX_<operation>.nc` / `setup_XX_complete.nc` pattern; no spaces or umlauts.
- [ ] A top-level `README.md` explains the layout, how to reproduce the Mode II pipeline, and who did what.
- [ ] The evaluation reports folder (`evaluations/`) and `EVALUATION.md` are **excluded from the final ZIP** (they are internal tooling), or their inclusion is disclosed as AI-use in the report.

---

## 4. Part-by-part assessment (rubric-aligned)

For every sub-criterion give: **Status** (`Missing` / `Started` / `Partial` / `Complete` / `Verified`), **Estimated marks** (out of the sub-weight), **Evidence** (paths), **Gaps**, and **Fix** (concrete action). Use the checklists below; every unchecked box needs a reason.

### Part A: Onshape modelling, drawing and assembly (20 marks)

**A.1 Reproducible two-part Onshape design (8)**
- [ ] `onshape_link.txt` contains a document URL **and** a named version (e.g. `/v/` or `/w/` plus version name). Workspace-only links are weaker: recommend a named version.
- [ ] Evidence that both Part Studios exist in **one** document: `APSD-LATHE` (with Chapter 1 feature history kept) and `APSD-MILLING`.
- [ ] Feature-tree screenshots for both parts; features are named meaningfully.
- [ ] A record of **corrections to the Chapter 1 lathe model** (what was wrong, what was changed), or an explicit statement that it was re-checked and nothing changed.
- [ ] A feature and design-assumption register separating *explicitly dimensioned*, *geometrically deduced* and *assumed* values.
- [ ] CAD exports (STEP preferred) in `CAD_exports_and_notes/`, matching the same named version.

**A.2 Two dimensioned component drawings (6)**
- [ ] `APSD_LATHE_drawing.pdf` and `APSD_MILLING_drawing.pdf`, A4 or A3.
- [ ] Each has: labelled isometric view; necessary front/top/side orthographic views; sections/details for internal features (lathe bores and internal thread; milling pocket/window, keyway, holes).
- [ ] Dimensions, units, diameters, radii, hole details, thread information present.
- [ ] Spot-check at least **8 dimensions per part** against Appendix B / the instructor sheet. Report any mismatch as a table: `feature | instructor value | team drawing value | file/page`.

**A.3 Assembly drawing, mates, interface verification (6)**
- [ ] `two_part_assembly_drawing.pdf` with item balloons, short BOM and isometric view.
- [ ] Assembly evidence (screenshot or export) showing mates, remaining degrees of freedom and contact.
- [ ] The milling part's Ø30 bore + 8 mm keyway engages the lathe part's corresponding diameter/key features consistently (check the interface dimensions agree between the two drawings).
- [ ] Answers to **Q2.1**, **Q2.2**, **Q2.3** exist (report or separate file) and are specific to *these* parts.

### Part B: Manufacturing plan, tooling and setups (15 marks)

**B.1 Traceable turning and milling routes (5)**
- [ ] Two route sheets (lathe, mill) with: raw material and geometry, finished allowance, workholding, process order, reference surfaces, machine orientation, stock removal, tool designation, inspection criteria.
- [ ] Mandatory vs optional (finishing) operations distinguished.
- [ ] An **operation-to-feature matrix** links every drawing feature to an operation, or explains why it is excluded (e.g. simulator limitation, other machine).

**B.2 Stock, workholding and multi-setup feasibility (5)**
- [ ] Stock dimensions for both parts, with machining allowance and **feasible clamping length** justified (lathe: overall length 210 mm + facing allowance + chuck grip; mill: envelope of the arm + allowance, clamping strategy for the curved profile).
- [ ] Setup/datum diagrams: at least one for turning and one for milling, showing work zero, machine axes and accessible features (**Q2.4**).
- [ ] Clear statement of which operations need re-clamping/second setup (**Q2.5**). Expected candidates: lathe second setup to machine the opposite end (left spigot, threaded blind bore, end-face holes), plus a note that off-axis holes and the keyway are not two-axis turning operations; milling second setup for the underside features shown in sections B-B / C-C if the team models them as two-sided.

**B.3 Tool selection and quantified machining parameters (5)**
- [ ] Tool sheet: for every tool, diameter or nose radius, type, and justified spindle speed, feed and depth of cut.
- [ ] Every value labelled as **drawing requirement**, **simulator setting** or **engineering estimate**.
- [ ] One turning and one milling calculation, unit-consistent. **Recompute them yourself** with the formulas below and report any arithmetic error with the corrected value:
  - Vc = πDN/1000 (m/min); N = 1000Vc/(πD) (rev/min)
  - Turning: vf = f·N (mm/min); MRR ≈ 1000·Vc·f·ap (mm³/min)
  - Milling: vf = fz·z·N (mm/min); MRR ≈ ae·ap·vf (mm³/min)
- [ ] Cutter sizes are compatible with the geometry: e.g. milling window inside corners are R8, so the finishing end mill must be ≤ Ø16 (and preferably smaller to avoid full-radius engagement); the 8 mm keyway needs ≤ Ø8; Ø3.5 holes need a matching drill. Flag any tool that physically cannot make its feature.

### Part C: Human-developed lathe G-code and LatheLab simulation (20 marks)

**C.1 Lathe G-code coverage and explanatory clarity (8)**
- [ ] Separate, labelled files or delimited modules per major operation (facing, OD roughing, OD finishing/profile, drilling/boring, grooving, threading as warranted) **plus** a consolidated run per setup.
- [ ] Each file header states: setup, tool, spindle/feed assumptions, toolpath intent, safe start and end state.
- [ ] **Line-level annotation** linking blocks to feature/tool/motion/safety (**Q2.7**). Check at least 15 random lines.
- [ ] Coverage table: which lathe features are programmed, which are simulator-limited but kept in the real plan (**C5**), which are missing.
- [ ] Programmed dimensions match the drawing: compare the program's X (diameter!) and Z values against Appendix B: Ø100 flange, flange width 20, overall length 210, step diameters, R5 fillets, thread region etc.

**C.2 Valid stock/tools/offsets and setup definition (4)**
- [ ] LatheLab setup log: stock OD, length, any pre-bore, tool IDs and geometry from **Stock** and **Tools & offsets**.
- [ ] Work zero and X/Z axes defined on a setup drawing; the X-as-diameter convention is confirmed in writing (**C1**).
- [ ] Controller-dialect checks documented (G21, G90/G91, G96/G97, G98/G99, T, S, F, M03/M05, G00/G01/G02/G03, any canned cycle) as *tested in the simulator*, not assumed.

**C.3 Operation-level simulation and geometric checks (8)**
- [ ] Screenshots **after each operation** (cross-section and 3D/Split where useful), plus Program check, Operations and Inspection outputs (**C4**, **Q2.8**).
- [ ] Discrepancies between simulated stock and the CAD profile are listed and either remedied or classified as simulator limitations.
- [ ] *Check part* results are kept separate from independently measured conformance.
- [ ] Screenshots are project-specific (correct stock dimensions visible, program text visible) and not the instructor's reference images.

### Part D: Human-developed milling G-code and MillLab simulation (20 marks)

**D.1 Milling G-code coverage and explanatory clarity (8)**
- [ ] Separate annotated programs per operation/setup: face milling, outer contour (R115/R60 arcs, Ø60 and Ø42 bosses), window/pocket with R8 corners, Ø30 and Ø20 bores, 8 mm keyway, Ø3.5 holes, any pins/steps visible in sections B-B and C-C.
- [ ] Roughing and finishing where required, sensible step-downs, radial engagement, non-cutting retracts.
- [ ] Line-level annotation, as for C.1.
- [ ] Programmed geometry matches the **team's own Onshape model**, not a lecture or simulator example (**D intro**).

**D.2 Tool selection and multi-orientation/setup strategy (4)**
- [ ] X/Y/Z directions, datum (MillLab default is front-left G54) and finished-part Z0 defined (**D1**).
- [ ] Cutter size justified against inside radii, narrow features, depth, access and residual stock (**D2**).
- [ ] For every additional setup: how the part is rotated/re-clamped, new datum, how new coordinates were derived (**D4**). Separate simulation runs per setup, correlated to the physical sequence.

**D.3 Operation-level simulation and geometric checks (8)**
- [ ] MillLab workpiece/tool/offset settings recorded (**D5**).
- [ ] Before/after captures of representative cuts; warnings and rapid moves reviewed.
- [ ] Cutter-centre trajectories on a labelled isometric **and** plan view, explaining cutter radius, entry/exit and work-origin influence (**Q2.9**).
- [ ] Differences between program, simulated removal and the Onshape drawing reported; manual corrections documented (**Q2.10**).

### Part E: Dual-mode generative AI CNC programming (20 marks, + possible 10 extra)

**E.1 Drawing-based AI approach, Mode I (4)**
- [ ] AI disclosure: provider, model/version, date, input modalities, settings, external scripts.
- [ ] Prompts and the exact source images sent are archived in `05_AI_Mode_I_Drawing/prompts_and_logs/`.
- [ ] Prompt supplies machine type, stock, coordinates, tool list, units, datum and expected outputs; requests (i) features + dimensions, (ii) operation sequence, (iii) toolpath assumptions, (iv) operation-labelled NC; instructs the model to flag unclear dimensions rather than invent them.
- [ ] Each AI-inferred feature was checked against the drawing **before** code was accepted (evidence of the check).

**E.2 Functioning structured CAD-data workflow, Mode II (6)**
- [ ] One of: STEP + parser, STL + Python mesh analysis (with explicit triangulation limitations), or Onshape API + Python.
- [ ] **Runnable**: extractor script, `requirements.txt` (pinned versions), README with run command, and an output manifest (JSON/CSV) committed. If a Python script exists, try to run it (offline) or at least `python -m py_compile` it; report the result.
- [ ] Manifest contains units, source file + model version, axes, bounding boxes, centres, radii, surfaces/placements, unknowns and confidence.
- [ ] Manifest values agree with the drawing (spot-check ≥ 5 values per part).
- [ ] API evidence is redacted (no keys in code, logs or screenshots).
- [ ] Architecture diagram or pseudocode (**Q2.12**), and a list of features that needed human annotation.

**E.3 Four AI programming attempts and transparent logs (4)**
- [ ] Separately identifiable **initial** AI NC files for: lathe Mode I, lathe Mode II, milling Mode I, milling Mode II, even if an attempt failed.
- [ ] All revisions kept (not overwritten): e.g. `*_v0_initial.nc`, `*_v1_rev.nc`, and a `program_revision_log.csv`.
- [ ] Both modes used the **same** part revision, stock, tools, reference frames and test criteria. Check that the stock/tool values in the prompts match the human baseline. Any mismatch invalidates the comparison.

**E.4 Comparative analysis and human verification (6)**
- [ ] `six_case_matrix.csv` filled for all six rows (2 workpieces × manual/Mode I/Mode II), separating initial proposal from human-corrected result.
- [ ] Gates **G1 Geometry, G2 Process, G3 Code, G4 Simulation** recorded per AI program with outcome (accept / edit and re-test / reject), reviewer name and date (`human_review_checklist.pdf`).
- [ ] **Q2.11**: ≥ 3 specific correct/incorrect/missed inferences across both parts.
- [ ] **Q2.13**: same measures for all three sources: recognised-feature coverage, dimensional discrepancies, number and severity of program issues, simulator-validated operations, human intervention count, development effort, **each with how it was measured**. Flag any timing or success rate that has no stated measurement method as a fabrication risk.
- [ ] **Q2.14**: one full failure-and-correction story for turning and one for milling (prompt/data → AI output → problem → human decision → re-simulation).
- [ ] *Extra (+10 %)*: note anything that plausibly earns the bonus (e.g. two Mode II pathways compared, automated simulator checks, quantified geometric deviation), but don't count it in the base score.

### Part F: Report, reproducibility and team contributions (5 marks)

- [ ] `Chapter02_Report.pdf`, roughly 8–15 pages excluding appendices, with sections (1)–(8): title/team/contributions; CAD and drawing evidence; setups and process plans; lathe and milling implementation; numerical and visual simulation results; AI comparison and human validation; limitations and improvements; **complete file inventory**.
- [ ] Report references artifacts by path instead of pasting long code blocks.
- [ ] Every file named in the report's inventory exists, and every significant file in the repo is in the inventory (diff the two lists).
- [ ] `team_contributions.csv` lists all 3–6 members with concrete contributions. Cross-check against `git shortlog` and commit content. Flag members with no visible contribution, and note that commits are not the only valid evidence (pair work, Onshape edits), so this is a prompt for discussion, not an accusation.
- [ ] Responsible-AI disclosure: what AI was used for **outside** Part E as well (report writing, code review, this evaluation prompt).
- [ ] Reproducibility test: could a stranger regenerate the Mode II manifest and re-run every simulation from the repo alone, without asking a team member? List every missing setting.

---

## 5. Automated NC checks (run every time)

Save the script below **outside the repository** (e.g. `/tmp/nc_lint.py`) and run `python3 /tmp/nc_lint.py <repo_root>`. It is a static checker, not a simulator. It flags structural issues for humans to verify in LatheLab/MillLab. (The team may choose to commit it as `tools/nc_lint.py`; if so, disclose it as AI-assisted tooling.)

```python
#!/usr/bin/env python3
"""Static sanity checker for APSD Chapter 2 NC files (LatheLab / MillLab).
Not a simulator: flags structural problems for a human to review.
Usage: python3 nc_lint.py <repo_root>   (scans *.nc, *.txt, *.gcode, *.tap, *.ngc containing G-code)"""
import re, sys, math, pathlib, json

WORD = re.compile(r'([A-Z])\s*([-+]?\d*\.?\d+)')
EXT = {'.nc', '.txt', '.gcode', '.tap', '.ngc'}

def strip(line):
    line = re.sub(r'\(.*?\)', '', line)          # (comments)
    line = line.split(';')[0]                     # ; comments
    return line.upper().strip()

def kind_of(path):
    p = str(path).lower()
    if 'lathe' in p: return 'lathe'
    if 'mill' in p: return 'mill'
    return 'unknown'

def lint(path):
    text = path.read_text(errors='replace').splitlines()
    if sum(1 for l in text if re.search(r'\b[GM]\s*\d', strip(l))) < 3:
        return None  # not a G-code file (e.g. onshape_link.txt)
    issues, notes = [], []
    k = kind_of(path)
    st = dict(units=None, dist=None, spindle=False, feed=None, tool=None, motion=None,
              x=None, y=None, z=None, ended=False, cut_seen=False, m05=False)
    xs, ys, zs = [], [], []
    gcode_lines = 0
    for n, raw in enumerate(text, 1):
        line = strip(raw)
        if not line: continue
        words = WORD.findall(line)
        if not words: continue
        gcode_lines += 1
        if st['ended']:
            issues.append(f'L{n}: code after program end (M30/M02)'); st['ended'] = False
        gs = [float(v) for c, v in words if c == 'G']
        ms = [int(float(v)) for c, v in words if c == 'M']
        d = {c: float(v) for c, v in words if c not in 'GMN'}
        for g in gs:
            if g == 20: st['units'] = 'inch'; issues.append(f'L{n}: G20 (inch) - course expects mm (G21)')
            if g == 21: st['units'] = 'mm'
            if g == 90: st['dist'] = 'abs'
            if g == 91: st['dist'] = 'inc'
            if g in (0, 1, 2, 3): st['motion'] = int(g)
        if 'T' in d: st['tool'] = d['T']
        if 'F' in d: st['feed'] = d['F']
        for m in ms:
            if m in (3, 4): st['spindle'] = True; st['m05'] = False
            if m == 5: st['spindle'] = False; st['m05'] = True
            if m in (30, 2): st['ended'] = True
        moved = any(a in d for a in 'XYZ')
        prev = (st['x'], st['y'], st['z'])
        if st['dist'] == 'inc':
            for a in 'XYZ':
                if a in d: st[a.lower()] = (st[a.lower()] or 0) + d[a]
        else:
            for a in 'XYZ':
                if a in d: st[a.lower()] = d[a]
        if moved and st['motion'] in (1, 2, 3):
            st['cut_seen'] = True
            if not st['spindle']: issues.append(f'L{n}: feed/arc move with spindle not running (no M03/M04 active)')
            if st['feed'] is None: issues.append(f'L{n}: feed move before any F word')
            if st['tool'] is None: issues.append(f'L{n}: feed move before any T tool call')
            if st['units'] is None: issues.append(f'L{n}: motion before units declared (G21)')
            if st['dist'] is None: issues.append(f'L{n}: motion before G90/G91 declared')
        if moved and st['motion'] in (2, 3):
            has_r = 'R' in d; ijk = [a for a in 'IJK' if a in d]
            if not has_r and not ijk:
                issues.append(f'L{n}: G02/G03 without R or I/J/K')
            elif ijk and st['dist'] == 'abs':
                # radius consistency check in the active plane (mill XY with I/J, lathe XZ with I/K)
                if k == 'lathe' or 'K' in d:
                    a0, b0 = prev[0], prev[2]; a1, b1 = st['x'], st['z']; ia, ib = d.get('I', 0), d.get('K', 0)
                    if k == 'lathe' and None not in (a0, a1):  # lathe X is usually diameter
                        a0, a1 = a0 / 2, a1 / 2
                else:
                    a0, b0 = prev[0], prev[1]; a1, b1 = st['x'], st['y']; ia, ib = d.get('I', 0), d.get('J', 0)
                if None not in (a0, b0, a1, b1):
                    cx, cy = a0 + ia, b0 + ib
                    r0 = math.hypot(a0 - cx, b0 - cy); r1 = math.hypot(a1 - cx, b1 - cy)
                    if abs(r0 - r1) > 0.01 * max(1, r0):
                        issues.append(f'L{n}: arc start radius {r0:.3f} != end radius {r1:.3f} (check I/J/K, diameter vs radius)')
        if moved and st['motion'] == 0 and k == 'mill' and st['z'] is not None and st['z'] < 0 and \
                ('X' in d or 'Y' in d):
            issues.append(f'L{n}: G00 rapid in XY while Z={st["z"]} is below Z0 - possible rapid into stock')
        if moved:
            if st['x'] is not None: xs.append(st['x'])
            if st['y'] is not None: ys.append(st['y'])
            if st['z'] is not None: zs.append(st['z'])
    if gcode_lines == 0:
        return None
    if not st['ended'] and gcode_lines: issues.append('END: no M30/M02 program end')
    if st['cut_seen'] and not st['m05']: notes.append('END: no M05 spindle stop before end (may be acceptable if M30 stops spindle in simulator)')
    rng = lambda v: [round(min(v), 3), round(max(v), 3)] if v else None
    if k == 'lathe' and xs and min(xs) < -2: issues.append(f'Lathe X reached {min(xs)} - check diameter/radius convention')
    elif k == 'lathe' and xs and min(xs) < 0: notes.append('Lathe X slightly below 0 (facing past centre) - OK if intended')
    return dict(file=str(path), kind=k, gcode_lines=gcode_lines, units=st['units'],
                extents=dict(X=rng(xs), Y=rng(ys), Z=rng(zs)), issues=issues, notes=notes)

def main(root):
    out = []
    for p in sorted(pathlib.Path(root).rglob('*')):
        if p.suffix.lower() in EXT and '.git' not in p.parts and p.is_file():
            r = lint(p)
            if r: out.append(r)
    print(json.dumps(out, indent=2))
    print(f'\nSUMMARY: {len(out)} NC files, {sum(len(r["issues"]) for r in out)} issues', file=sys.stderr)

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '.')
```

After running it, **interpret** the output yourself:
- **Extents sanity**: lathe max X should be ≈ stock diameter + clearance (not ≫), min Z should reach ≈ −210 (or the setup's machined length) but not run into the chuck; mill X/Y extents should match the part envelope plus cutter radius and approach; mill min Z should equal the deepest feature (e.g. −20 for through features plus breakthrough), not deeper than the stock.
- **Modal and safety review by eye** (the script can't catch these): G96 constant surface speed used with a G50/max-RPM limit where the dialect needs one; G98/G99 feed mode consistent with F values (mm/rev vs mm/min); tool change at a safe position; tool-nose/cutter compensation (G41/G42/G40) switched on and off correctly; canned cycles actually supported by LatheLab/MillLab per the team's own dialect test.
- **Human vs AI programs**: run the checker on `03_*`, `04_*`, `05_*`, `06_*` separately and put the issue counts into the comparison in Section 6. They can serve as one objective input to Q2.13 *if* the team records the method.

**Optional (if you have browser tools):** open `https://mohammadrezaconstructor.github.io/cnc-simulator/`, load one consolidated lathe program and one mill program with the stock and tool settings from the team's setup log, and compare Program-check warnings with the team's screenshots. Report what you observed and label it as your own run. If you can't do this, list it as a human check.

---

## 6. Cross-consistency checks (where teams usually lose marks)

Build a small table for each and flag every mismatch:

1. **Stock**: route sheet ↔ tool/stock sheet ↔ NC header comments ↔ LatheLab/MillLab setup log ↔ screenshots ↔ AI prompts (Mode I and II).
2. **Tools**: tool IDs, diameters/nose radii and offsets identical across tool sheet, NC files, simulator log and AI prompts.
3. **Datums**: work zero on setup diagram ↔ NC coordinates ↔ simulator offset ↔ AI prompt.
4. **Geometry**: instructor drawing ↔ team drawing ↔ Onshape model (screenshots/exports) ↔ Mode II manifest ↔ NC coordinates.
5. **Revisions**: the Onshape named version in `onshape_link.txt` is the one used for drawings, exports, manifest and AI prompts.
6. **Chronology (integrity)**: the human baselines in `03_*`/`04_*` should be committed **before** AI outputs in `05_*`/`06_*`. Use `git log --diff-filter=A --format='%ad %h' -- <path>` to check first-add dates. If AI files predate the human baseline, flag it for the team to explain (it may be legitimate, but they must disclose it).
7. **Report ↔ repo**: numbers quoted in the report (feature counts, issue counts, intervention counts, timings) match the CSVs and logs.

---

## 7. Questions coverage matrix

List every question with **Answered / Partial / Missing**, the file and page/section where the answer lives, and a one-line quality note (specific to these parts? backed by evidence?).

| Q | Topic | Where answered | Status | Quality note |
|---|---|---|---|---|
| Q2.1 | Two-axis turning feasibility of APSD-LATHE features; special tool/second setup/other machine | | | |
| Q2.2 | APSD-MILLING orientations, holes, pockets, profiles; inaccessible features; repositioning | | | |
| Q2.3 | Assembly mates and dimension chain; critical inspection dimensions | | | |
| Q2.4 | Stock shape and clamping; setup diagrams (turning + milling) | | | |
| Q2.5 | Operations in one setup vs later setups | | | |
| (Q2.6) | *Not present in the brief: do not penalise* | – | – | – |
| Q2.7 | Operation-by-operation lathe NC with line-level explanation | | | |
| Q2.8 | Lathe simulation evidence per operation; discrepancies | | | |
| Q2.9 | Cutter-centre trajectories (isometric + plan); radius, entry/exit, origin | | | |
| Q2.10 | Milling shape after reorientation; differences and corrections | | | |
| Q2.11 | Mode I correct/incorrect/missing inferences (≥ 3 instances) | | | |
| Q2.12 | Mode II pipeline architecture; reliably extracted vs human-annotated features | | | |
| Q2.13 | Quantitative comparison of manual vs Mode I vs Mode II, with measurement methods | | | |
| Q2.14 | Failure-and-correction sequence: one turning, one milling | | | |

---

## 8. Integrity and responsible-AI red flags

Check and report each (Clear / Concern / Not yet applicable):
- Simulation claims without a matching project-specific screenshot or log.
- Measurements, timings or success rates without a stated measurement method.
- AI-generated content (code, text, figures) not labelled as such; prompt or revision history missing or overwritten.
- Human baseline that looks AI-generated and undisclosed (e.g. identical structure/comments to files in `05_*`/`06_*`).
- Instructor reference screenshots (Figure 2.2) reused as if they were the team's own.
- Confidential/licensed CAD uploaded to public AI tools without permission.
- Credentials anywhere in the current tree **or git history**.
- Visually similar rendered shape claimed as a "fully validated finished part" (the brief explicitly forbids this equivalence).

---

## 9. Output: the evaluation report

Write the report to `evaluations/EVAL_<YYYY-MM-DD>_<HHMM>.md` (create the folder if needed) **and** print a short summary in chat. Use exactly this structure so successive runs can be compared:

```markdown
# Chapter 2 Evaluation: <date> <time>
Phase assumed: <Week X, Day Y> (source: user / inferred from git)
Commit evaluated: <short hash> on <branch>
Previous evaluation: <file name or "none">

## 0. Critical alerts
(secrets, integrity concerns, anything that could zero a part: or "None")

## 1. Executive summary
- Estimated score if submitted today: NN / 100 (confidence: low/medium/high)
- Schedule status: On track / At risk / Behind, with one-line reason
- Top 3 risks

## 2. Scorecard
| Part | Sub-criterion | Weight | Est. marks | Status | Δ vs last run | Key evidence |
|------|---------------|--------|-----------|--------|---------------|--------------|
| A | Two-part Onshape design | 8 | | | | |
| A | Two component drawings | 6 | | | | |
| A | Assembly drawing, mates, interface | 6 | | | | |
| B | Turning & milling routes | 5 | | | | |
| B | Stock, workholding, multi-setup | 5 | | | | |
| B | Tools & machining parameters | 5 | | | | |
| C | Lathe G-code coverage & clarity | 8 | | | | |
| C | Lathe stock/tools/offsets/setup | 4 | | | | |
| C | Lathe simulation & checks | 8 | | | | |
| D | Mill G-code coverage & clarity | 8 | | | | |
| D | Mill tools & multi-setup strategy | 4 | | | | |
| D | Mill simulation & checks | 8 | | | | |
| E | Mode I drawing-based approach | 4 | | | | |
| E | Mode II CAD-data workflow | 6 | | | | |
| E | Four AI attempts & logs | 4 | | | | |
| E | Comparative analysis & human verification | 6 | | | | |
| F | Report, reproducibility, AI disclosure, contributions | 5 | | | | |
| | **Total** | **100** | | | | |
| | *Extra-credit candidates (not counted)* | +10 | | | | |

## 3. Milestone tracker
(table from Section 2 with On track / At risk / Behind and missing items)

## 4. Structure & hygiene
(Pass/Fail list from Section 3)

## 5. Detailed findings by part
(For each part A–F: what's good, what's wrong (file:line), what's missing, and the fix)

## 6. NC checker results
(per-file issue counts and extents table; your interpretation; human vs AI comparison)

## 7. Cross-consistency tables
(Section 6 checks with mismatches highlighted)

## 8. Questions coverage
(matrix from Section 7)

## 9. Integrity & responsible-AI checks
(Section 8 list)

## 10. Needs human verification
(things you could not check: Onshape access, simulator re-runs, drawing legibility, etc.: who should check what)

## 11. Prioritised action list
| # | Priority (P0 blocker / P1 marks at stake / P2 polish) | Action | Files | Marks at stake | Effort (S ≤1h / M ≤4h / L >4h) | Suggested by (phase) |
|---|---|---|---|---|---|---|
(10–20 items, sorted by marks-at-stake ÷ effort; P0 first. Be concrete: "Add F word before line 12 of 03_Lathe/op_20_turning.nc", not "improve G-code".)

## 12. Progress since last run
- Resolved since last run: …
- New issues: …
- Still open from last run: … (mark items open for ≥ 2 runs as **stale**)
- Score trend: previous NN → now NN

## 13. Should we do something else?
(Anything the brief asks for that the team hasn't planned at all; opportunities for the +10 % extra; risks that will become blockers in the next phase.)
```

Scoring guidance for the estimated marks:
- `Missing` = 0. `Started` ≈ 10–30 % of weight. `Partial` ≈ 40–70 %. `Complete` (all checklist items present) ≈ 75–90 %. `Verified` (complete **and** you confirmed correctness against the drawing/simulation evidence) ≈ 90–100 %.
- Never award more than 50 % of a simulation criterion without project-specific simulator evidence.
- Never award marks for a Mode II workflow that has no runnable code or no committed manifest.
- Be calibrated: if evidence is ambiguous, give the lower estimate and say what would raise it.

---

## Appendix A: Condensed Chapter 2 brief (use if the PDF is not available)

- **Products**: APSD-LATHE (from Chapter 1, reuse/check/correct) and APSD-MILLING (new), both in **one Onshape document**, assembled and documented **before** CNC programming. APSD-STEPPE(R) is contextual only (Chapter 3).
- **Simulator**: `https://mohammadrezaconstructor.github.io/cnc-simulator/`, using LatheLab for turning and MillLab for milling (Reference, Tools & offsets, Stock, Program check, Inspection, Check part).
- **Team**: 3–6 students, all must participate meaningfully. **Duration**: two weeks (10 working days).
- **Rubric**: A 20 (8/6/6) · B 15 (5/5/5) · C 20 (8/4/8) · D 20 (8/4/8) · E 20 (4/6/4/6) + up to 10 extra · F 5.
- **Submission**: one ZIP `APSD_TeamXX_Chapter02_CNC.zip` with the structure in Section 3; Onshape kept accessible through a shared URL and named version.
- **Final checklist (brief)**: both parts and the assembly in one Onshape document; drawings adequately dimensioned; both manual NC baselines run to the level the simulator supports; operations, setups, tools and input material documented; all four AI attempts identifiable; the comparison is reproducible without asking a team member for missing settings.
- **AI research question**: How does the quality and reliability of AI-assisted CNC programming change between (I) a dimensioned isometric drawing and (II) machine-readable geometry extracted from CAD? Same part revision, stock, tools, frames and criteria in both modes. AI proposes and reviews; humans own geometry, strategy, approval and simulation. Gates G1 Geometry → G2 Process → G3 Code → G4 Simulation for every AI program.
- **Integrity**: provide the human baseline, identify AI-originated content, preserve prompt and revision history, verify all final code; no fabricated simulation results, measurements or parameters; no restricted CAD in public tools.
- **Assigned references**: APSD.Part 00 (assembly sheet 1, milling sheet 2, lathe sheet 3); APSD.Part 02 CAPP/CAM; APSD.Part 03 CNC Machining (slides 11, 16–23, 29–35).

## Appendix B: Reference dimensions as read from the instructor's sheets

> These were read from the drawing images for cross-checking only. Some callouts are small; **always confirm against the original sheet**. All dimensions in mm; first-angle projection.

**APSD-LATHE (sheet 3, scale 1:3)**
- Overall length **210**; flange **Ø100**, flange width **20**; **R5** fillets either side of the flange.
- Hub/step length **40** on the short side of the flange; end spigot length **20**; small-end callouts **23** and **4,1**.
- External thread region on the long side, pitch callout **5**, length **125** (section A–A).
- End-view callouts: **Ø30**, **Ø13** (one end); **Ø60**, **Ø70**, **Ø29,9**, hole **Ø3,52**, keyway/slot width **7,98**, offset **17,9** (other end).
- Section A–A: threaded blind bore at the spigot end, depth **41,42**, with a **2** step/chamfer; through-bore along the axis; counterbore at the threaded end **40** deep with diameter callouts **20 / 21 / 25**.
- Expected turning implications: OD turning of steps, flange and fillets; facing both ends (second setup); drilling/boring; internal and external threading; **off-axis holes, the keyway/slot and any flats are not two-axis turning operations**. They need live tooling, a mill or a second machine (relevant to Q2.1).

**APSD-MILLING (sheet 2, scale 1:2)**
- Thickness **20** at both bosses; large boss **Ø60** with **Ø30** bore and keyway **8** wide; small boss **Ø42** with **Ø20** bore.
- Curved arm: outer **R115**, inner **R60**; internal window/pocket with **R8** corners, wall/rib width **8**.
- Small holes **Ø3,5** around the large boss; small pins/steps **4** high with spacing callouts **18** and **23** (section B–B); tab/step **10** (section B–B); edge radii **R2** (sections A–A and B–B/C).
- Expected milling implications: face milling, outer profile contouring, window pocketing with cutter ≤ Ø16 (R8 corners), bore interpolation or drilling + boring, 8 mm keyway, small-hole drilling, R2 edge features possibly requiring a second setup or a form tool (relevant to Q2.2 and D4).

---

*End of evaluation prompt. Re-run after each significant commit. The value comes from the trend in Section 12 of each report, not from a single run.*
