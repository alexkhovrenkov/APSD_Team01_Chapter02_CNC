# Human review checklist – gates G1–G4 (brief §2.7.3)

Apply to **every AI-generated program** (initial and each revision). Record the outcome in that program's JSON in
[human_review_records/](human_review_records/README.md). Only a team member sets a status, a reviewer name and a date.
Allowed statuses: `PENDING_HUMAN_REVIEW`, `APPROVED`, `REJECTED`, `REQUIRES_CORRECTION`, `PENDING_SIMULATION`.
Issue severities: **critical** (alarm, crash or certainly wrong geometry), **major** (likely wrong part, unsafe, or
rejected by the gate), **minor** (robustness or style). See [evaluation_methodology.md](evaluation_methodology.md).

## G1 – Geometry gate (before any code is considered)
Use `<05|06>/<part>/recognized_features.json` together with the [evaluation reference](evaluation_reference/).
- [ ] Every reference feature mapped: `CORRECT | PARTIAL | INCORRECT | MISSED | FLAGGED_AS_UNCLEAR | INVENTED_VALUE`.
- [ ] Every AI dimension compared with the reference (`ai_value`, `reference_value`); errors in mm.
- [ ] Feature **types** right. Milling: the six Ø3.5 features are raised **pins**, not holes; the opening in the arm is a
      **through window**; the keyway is closed at 18 mm from the bore axis. Lathe: the key on the spigot is **raised**;
      the Ø3.52 holes are axial and blind.
- [ ] Locations and **coordinate origins**: the AI's work zero matches the shared config; CAD → work-frame transformation
      checked (Mode II: CAD origin = bore axis at mid-thickness / spigot end face).
- [ ] Machine axes: lathe X = diameter, −Z towards the chuck; mill +Z up, Z0 on the finished top.
- [ ] Missing information listed by the AI (`unclear_or_missing`) is really missing, and every value the AI supplied for
      undimensioned items (e.g. boss centre distance in Mode I) is marked `INVENTED_VALUE`.

## G2 – Process gate
- [ ] Operation order (roughing before finishing, datum faces first, holes after faces).
- [ ] Setup orientation and re-clamping: lathe two setups (flange in the middle, bores at both ends); milling top and
      flipped setups (recessed faces on both sides), with the datum stated for each setup.
- [ ] Tool geometry fits the feature: window corners R8 → cutter ≤ Ø16; keyway 8 → cutter ≤ Ø8; R5 blends → nose radius
      ≤ 5; R2 fillets → ball/bull-nose or documented limitation; threads → correct threading tool.
- [ ] Machining access (pins: the boss top is machined around them; off-axis lathe holes and key are not 2-axis turning).
- [ ] Workholding matches Part B (grip length, jaw height, clamping on finished faces).
- [ ] Spindle speeds and feeds equal the approved Part B values (or the deviation is justified); units per minute or per rev.

## G3 – Code gate (start from `automatic_checks.json`; it is static only)
- [ ] Modal states: G21; lathe G18 G40 G99/G98; mill G17 G40 G49 G80 G90 G94; G96 with G50 limit.
- [ ] Coordinate signs and diameters (lathe X positive diameters; **G90 on the lathe is a turning cycle**; no G91 on the lathe).
- [ ] Arc definitions (R or I/J/K; I is a radius on the lathe; G02/G03 direction with the rear tool post).
- [ ] Compensation: G41/G42 started on a linear lead-in outside the part, D register (mill), cancelled with G40 before G28/M06/end.
- [ ] Tool changes at a safe position; T0101 format (lathe); M06 + G43 Hnn (mill).
- [ ] Non-cutting moves: no G00 inside the stock; clearance/R-planes above the stock top; retract before tool change.
- [ ] Program termination: M05, home return, M30.

## G4 – Simulation gate (LatheLab / MillLab)
- [ ] Stock dialog equals the shared config (screenshot).
- [ ] Tools & offsets equal the shared config (screenshot).
- [ ] Program check: every warning and error copied into `simulation_log.json`.
- [ ] Remaining material compared with the CAD profile per feature (cross-section, Split view, Inspection, Check part).
- [ ] Feature-level conformance within the agreed tolerance (`acceptance_tolerance_simulation` in the config).
- [ ] Decision: accept, or edit and re-test (store with `revise`), or reject. A visually similar render is **not** a validated part.
