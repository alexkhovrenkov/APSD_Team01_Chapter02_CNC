# Mode I drawing inputs

| File | Workpiece | Source |
|---|---|---|
| `APSD_LATHE_instructor_sheet3_p26_300dpi.png` | APSD-LATHE | brief PDF *APSD.Part 00 … P2*, p. 26 (instructor sheet 3) |
| `APSD_MILLING_instructor_sheet2_p25_300dpi.png` | APSD-MILLING | brief PDF, p. 25 (instructor sheet 2) |

Hashes, render settings and source PDF hash: [input_manifest.json](input_manifest.json).

- **Rendering.** The sheets are vector drawings. They were rendered with PyMuPDF at 300 dpi (3509 × 2480 px, full A4),
  so every dimension label stays readable. No cropping, no edits.
- **Why the orthographic and section views are included.** The isometric view on each sheet carries **no dimensions**.
  All dimensions sit on the orthographic and section views of the same sheet. The brief (§2.7.1) allows essential
  orthographic and section drawings "when justified and clearly logged". This is the justification.
- **Pending decision (G1, team).** The brief asks for the same final part revision in both modes. The team drawings
  (Onshape tabs *APSD-LATHE-Final* and *APSD-MILLING*, which already exist in the document) are not exported to
  `01_Onshape_Drawings/` yet. If the team prefers them, export both PDFs from the **same named version** as the
  manifests, render them the same way and update `input_manifest.json`. Record which drawing was used in each run.
- These images are **not duplicates of 01_Onshape_Drawings**: that folder is empty, and these are the instructor sheets.
- Course material only. Do not upload it outside the course's permitted tools (brief §2.10).
