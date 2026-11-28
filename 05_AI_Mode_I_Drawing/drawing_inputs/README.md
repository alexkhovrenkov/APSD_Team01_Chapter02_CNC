# Mode I drawing inputs

| File | Workpiece | Source |
|---|---|---|
| `APSD_LATHE_instructor_sheet3_p26_300dpi.png` | APSD-LATHE | brief PDF *APSD.Part 00 … P2*, p. 26 (instructor sheet 3) |
| `APSD_MILLING_instructor_sheet2_p25_300dpi.png` | APSD-MILLING | brief PDF, p. 25 (instructor sheet 2) |
| `APSD_LATHE_team_drawing_vdd8cc179_300dpi.png` | APSD-LATHE | team drawing *APSD-LATHE-Final*, exported 2026-11-28 (named version Ch2-Final) |
| `APSD_MILLING_team_drawing_vdd8cc179_300dpi.png` | APSD-MILLING | team drawing *APSD-MILLING*, exported 2026-11-28 (named version Ch2-Final) |

Hashes, render settings and source PDF hash: [input_manifest.json](input_manifest.json).

- **Rendering.** The sheets are vector drawings. They were rendered with PyMuPDF at 300 dpi, full sheet (A4 = 3509 × 2480 px;
  the lathe team drawing is a Letter sheet = 3300 × 2550 px), so every dimension label stays readable. No cropping, no edits.
- **Why the orthographic and section views are included.** The isometric view on each sheet carries **no dimensions**.
  All dimensions sit on the orthographic and section views of the same sheet. The brief (§2.7.1) allows essential
  orthographic and section drawings "when justified and clearly logged". This is the justification.
- **Pending decision (G1, team): which drawing Mode I uses.** The brief asks for the same final part revision in both modes.
  The team drawings come from the same named version (*Ch2-Final*) as the Mode II manifests, so they are the better
  choice. **Before using the lathe team drawing**, Part A should fix its title block: it says "DIMENSIONS ARE IN INCHES"
  with inch tolerances although every value is in mm, and the sheet is ANSI A (Letter) instead of A4/A3. Then re-export
  and re-render it. Record the choice in `input_manifest.json` (`decision`) and in every run.
- The PNGs are renders for the AI chat; the PDFs themselves belong in `01_Onshape_Drawings/` (Part A).
- Course material only. Do not upload it outside the course's permitted tools (brief §2.10).
