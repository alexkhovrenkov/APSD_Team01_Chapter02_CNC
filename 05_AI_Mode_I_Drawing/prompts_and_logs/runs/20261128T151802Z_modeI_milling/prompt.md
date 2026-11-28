" is NOT sent to the AI.
-->
=== PROMPT START ===
You are assisting a university team with CNC programming for a teaching simulator. You act as a PROPOSING agent: the team will check every feature, decision and NC line before anything is accepted. The programs are simulation-only candidates.

# Task
Workpiece: APSD-MILLING
Process: milling (3-axis vertical machining centre)

Mode: DRAWING. The geometry source is the attached dimensioned engineering drawing image (one drawing sheet: isometric view plus the orthographic/section views that carry the dimensions; first-angle projection). Read dimensions only from the dimension callouts.

Use ONLY the geometry source above for part geometry. Do not use prior knowledge of this part, and do not estimate dimensions from image scale or proportions. If a dimension, position or feature is unclear, missing or ambiguous, say so explicitly in "unclear_or_missing" and mark the dependent operations; do NOT invent a value. If you must assume something to continue, list it as an assumption with the reason.

# Machine, simulator, stock, tools, coordinates (same for every attempt)
The following configuration is fixed by the team. Values marked PENDING_HUMAN_REVIEW or null are not decided yet: do not fill them silently - state what you assumed and flag it.

```json
{
 "common": {
  "units": {
   "value": "mm, degrees; G21 (metric) in every program",
   "class": "SIMULATOR_SETTING",
   "status": "CONFIRMED",
   "source": "simulator_dialect.json (G21 supported in both labs); CAD manifests in mm"
  },
  "simulator": {
   "value": "Course simulator https://mohammadrezaconstructor.github.io/cnc-simulator/ - LatheLab for turning, MillLab for milling",
   "class": "SIMULATOR_SETTING",
   "status": "CONFIRMED",
   "source": "brief 2.9"
  },
  "safety_scope": {
   "value": "Programs are SIMULATION-ONLY candidates. They will not be run on a physical machine before independent human verification.",
   "class": "HUMAN_APPROVED",
   "status": "PENDING_HUMAN_REVIEW",
   "source": "brief 2.10 integrity policy; team to confirm"
  },
  "required_output": {
   "value": "see prompt template section 'Required response format' (features JSON, operation plan JSON, toolpath assumptions, operation-labelled NC blocks, consolidated program per setup, uncertainty list)",
   "class": "HUMAN_APPROVED",
   "status": "PENDING_HUMAN_REVIEW",
   "source": "brief 2.7.1 (i)-(iv)"
  }
 },
 "APSD-MILLING": {
  "part_id": {
   "value": "APSD-MILLING",
   "class": "CAD_EXTRACTED",
   "status": "CONFIRMED",
   "source": "brief Table 2.1; Onshape tab APSD-MILLING"
  },
  "cad_revision": {
   "value": {
    "document": "6877e7a6059a24d360e8c6e1",
    "named_version": "Ch2-Final",
    "version_id": "dd8cc179d8265b20fe3f589e",
    "element": "20caaefd66e3a40229321161 (APSD-MILLING)",
    "model_microversion": "4d05edae182b19aa4ea1f30d"
   },
   "class": "CAD_EXTRACTED",
   "status": "CONFIRMED",
   "source": "Onshape named version 'Ch2-Final' (created 2026-11-28 by the team); 06 evidence 20261128T085839Z_hmac_milling"
  },
  "machine_type": {
   "value": "3-axis vertical machining centre with a vise, as modelled by MillLab",
   "class": "SIMULATOR_SETTING",
   "status": "CONFIRMED",
   "source": "simulator_dialect.json milllab.conventions.axes"
  },
  "controller_dialect": {
   "value": "Fanuc-style mill G-code as implemented by MillLab: G17/G18/G19, G90/G91 absolute/incremental, G94/G95, G54-G59, G43 Hnn tool length compensation (or AUTO TOOL COMP), G41/G42 Dnn cutter compensation only in G17, canned cycles G73/G74/G76/G81-G86/G89 + G80, M06 tool change; supported G/M lists in simulator_dialect.json",
   "class": "SIMULATOR_SETTING",
   "status": "CONFIRMED",
   "source": "simulator_dialect.json (static reading, 2026-11-26) - each used command still to be tested in MillLab"
  },
  "machine_limits": {
   "value": "max 8000 rpm, rapid 15000 mm/min",
   "class": "SIMULATOR_SETTING",
   "status": "CONFIRMED",
   "source": "simulator_dialect.json milllab.conventions.machine_limits (defaults)"
  },
  "stock": {
   "value": {
    "type": "rectangular block",
    "size_X_mm": 170,
    "size_Y_mm": 85,
    "height_Z_mm": 24,
    "top_facing_allowance_mm": 0,
    "height_above_vise_jaws_mm": 24
   },
   "class": "HUMAN_APPROVED",
   "status": "CONFIRMED",
   "source": "02_Process_Plans/tooling_stock_setups.pdf (Part B, Team01, 2026-11-24) section 2.1 (MillLab 'Workpiece (block)' dialog); 02_Process_Plans/milling_route_sheet.pdf (Part B, Team01, 2026-11-24) header; entered 2026-11-28 on the instruction of a team member; values copied, not changed"
  },
  "material": {
   "value": "Aluminium 6061 - MillLab material preset 'Aluminium 6061'",
   "class": "HUMAN_APPROVED",
   "status": "CONFIRMED",
   "source": "02_Process_Plans/tooling_stock_setups.pdf (Part B, Team01, 2026-11-24) section 2.1; 02_Process_Plans/milling_route_sheet.pdf (Part B, Team01, 2026-11-24); entered 2026-11-28 on the instruction of a team member; values copied, not changed"
  },
  "work_origin": {
   "value": {
    "setup_1": "G54 X0 Y0 at the front-left corner of the block (+X along the long side, +Y along the short side); Z0 on the top surface of the block (= finished top, nothing faced off).",
    "part_position_setup_1": "The part lies flat with the pins facing up (+Z). The axis of the larger boss (the one with the keyed bore) is at X40 Y40. The line through both boss axes is parallel to +X, with the second boss at larger X. The keyway points towards +Y.",
    "setup_2": "Part turned over about the Y axis, so every X becomes 170 - X and Y is unchanged (larger boss axis at X130 Y40). G54 at the front-left corner after flipping; Z0 on the bottom faces of the bosses (the finished opposite surface)."
   },
   "class": "HUMAN_APPROVED",
   "status": "CONFIRMED",
   "source": "02_Process_Plans/milling_route_sheet.pdf (revised 2026-11-28, matched to the 04_Mill programs); approved 2026-11-28 by a team member (Part E) in the Claude Code session"
  },
  "setups": {
   "value": {
    "setup_1": "First side up (pins facing +Z), block held in a fixture.",
    "setup_2": "Part turned over about the Y axis and held in a dedicated support fixture that protects the features made in setup 1; coordinate system re-established as in work_origin.",
    "programs": "Each setup is simulated on its own in MillLab, starting from the raw block (MillLab only loads a raw rectangular block)."
   },
   "class": "HUMAN_APPROVED",
   "status": "CONFIRMED",
   "source": "02_Process_Plans/milling_route_sheet.pdf (revised 2026-11-28, matched to the 04_Mill programs); 02_Process_Plans/tooling_stock_setups.pdf section 2.2; approved 2026-11-28 by a team member (Part E) in the Claude Code session"
  },
  "workholding": {
   "value": {
    "setup_1": "fixture; in MillLab a vise with the whole block height above the jaws",
    "setup_2": "dedicated support fixture protecting the setup-1 features"
   },
   "class": "HUMAN_APPROVED",
   "status": "CONFIRMED",
   "source": "02_Process_Plans/tooling_stock_setups.pdf (Part B, Team01, 2026-11-24) section 2.1; 02_Process_Plans/milling_route_sheet.pdf (Part B, Team01, 2026-11-24) headers; entered 2026-11-28 on the instruction of a team member; values copied, not changed"
  },
  "tools": {
   "value": {
    "magazine": [
     {
      "T": "T01",
      "type": "Face mill",
      "name": "Face mill D50 (5 inserts)",
      "diameter": 50,
      "corner_R": 0,
      "flutes": 5,
      "flute_length": 25,
      "length": 75,
      "H": 75,
      "D_radius": 25
     },
     {
      "T": "T02",
      "type": "Flat end mill",
      "name": "End mill D10 3-flute",
      "diameter": 10,
      "corner_R": 0,
      "flutes": 3,
      "flute_length": 25,
      "length": 75,
      "H": 75,
      "D_radius": 5
     },
     {
      "T": "T03",
      "type": "Flat end mill",
      "name": "End mill D6 3-flute",
      "diameter": 6,
      "corner_R": 0,
      "flutes": 3,
      "flute_length": 25,
      "length": 62,
      "H": 62,
      "D_radius": 3
     },
     {
      "T": "T04",
      "type": "Spot / centre drill",
      "name": "Spot drill D10 90deg",
      "diameter": 10,
      "corner_R": 0,
      "flutes": 2,
      "flute_length": 10,
      "length": 70,
      "H": 70,
      "D_radius": 5
     },
     {
      "T": "T05",
      "type": "Twist drill",
      "name": "Drill D6.8 (tap drill M8)",
      "diameter": 6.8,
      "corner_R": 0,
      "flutes": 2,
      "flute_length": 45,
      "length": 100,
      "H": 100,
      "D_radius": 3.4
     },
     {
      "T": "T06",
      "type": "Tap",
      "name": "Tap M8x1.25",
      "diameter": 8,
      "corner_R": 0,
      "flutes": 3,
      "flute_length": 20,
      "length": 95,
      "H": 95,
      "D_radius": 4
     },
     {
      "T": "T07",
      "type": "Twist drill",
      "name": "Drill D10",
      "diameter": 10,
      "corner_R": 0,
      "flutes": 2,
      "flute_length": 55,
      "length": 110,
      "H": 110,
      "D_radius": 5
     },
     {
      "T": "T08",
      "type": "Ball end mill",
      "name": "Ball end mill D8 (R4) - row inconsistent, see open_items",
      "diameter": 10,
      "corner_R": 0,
      "flutes": 2,
      "flute_length": 6,
      "length": 18,
      "H": 70,
      "D_radius": 4
     },
     {
      "T": "T09",
      "type": "Chamfer mill",
      "name": "Chamfer mill D12 90deg",
      "diameter": 12,
      "corner_R": 0,
      "flutes": 4,
      "flute_length": 6,
      "length": 70,
      "H": 70,
      "D_radius": 6
     },
     {
      "T": "T10",
      "type": "Bull-nose end mill",
      "name": "Bull-nose D12 R2",
      "diameter": 12,
      "corner_R": 2,
      "flutes": 4,
      "flute_length": 25,
      "length": 80,
      "H": 80,
      "D_radius": 6
     },
     {
      "T": "T11",
      "type": "Reamer",
      "name": "Reamer D8 H7",
      "diameter": 8,
      "corner_R": 0,
      "flutes": 6,
      "flute_length": 30,
      "length": 100,
      "H": 100,
      "D_radius": 4
     },
     {
      "T": "T12",
      "type": "Flat end mill",
      "name": "End mill D16 4-flute",
      "diameter": 16,
      "corner_R": 0,
      "flutes": 4,
      "flute_length": 32,
      "length": 92,
      "H": 92,
      "D_radius": 8
     }
    ],
    "units": "mm; H = length register used by G43 (H number = tool number), D = radius register used by G41/G42 (D number = tool number); wear = 0",
    "open_items": [
     "T08 row is inconsistent (named D8 R4 ball, entered as D10 with corner R 0 and length 18 vs H 70); no cutting data approved - not to be used"
    ]
   },
   "class": "HUMAN_APPROVED",
   "status": "CONFIRMED",
   "source": "02_Process_Plans/tooling_stock_setups.pdf (Part B, Team01, 2026-11-24) section 2.3, Figures 5-6 (MillLab 'Tool magazine & offsets'); entered 2026-11-28 on the instruction of a team member; values copied, not changed"
  },
  "cutting_data": {
   "value": {
    "modes": "feed per minute G94 (mm/min)",
    "per_tool": [
     {
      "T": "T02",
      "rpm": 4000,
      "feed_mm_min": 200
     },
     {
      "T": "T03",
      "rpm": 4000,
      "feed_mm_min": 150
     },
     {
      "T": "T10",
      "rpm": 4000,
      "feed_mm_min": 200
     }
    ],
    "max_step_down_mm": {
     "general_material_removal": 4,
     "small_features": 2,
     "note": "smaller passes where required"
    },
    "plunge_feed_mm_min": 60,
    "other_tools": "all other magazine tools have no approved cutting data"
   },
   "class": "HUMAN_APPROVED",
   "status": "CONFIRMED",
   "source": "02_Process_Plans/milling_route_sheet.pdf (Part B, Team01, 2026-11-24) speed/feed columns and assumptions; entered 2026-11-28 on the instruction of a team member; values copied, not changed"
  },
  "safety_clearances": {
   "value": {
    "safe_height": "All rapid XY moves at the safe height Z10 (10 mm above Z0).",
    "plunge": "Moves into material at the plunge feed (see cutting_data).",
    "tool_change": "Before every tool change: retract to Z10, stop the spindle (M05) and cancel tool length compensation (G49); change with M06; then G43 Hnn with nn = tool number."
   },
   "class": "HUMAN_APPROVED",
   "status": "CONFIRMED",
   "source": "02_Process_Plans/milling_route_sheet.pdf (revised 2026-11-28, matched to the 04_Mill programs); approved 2026-11-28 by a team member (Part E) in the Claude Code session"
  },
  "simulator_setup": {
   "value": "MillLab: Workpiece dialog = Part B block + origin + Z reference; Tools & offsets = Part B tools (H/D registers or AUTO comp stated); one simulation run per setup",
   "class": "SIMULATOR_SETTING",
   "status": "CONFIRMED",
   "source": "brief 2.6 D4/D5"
  }
 }
}
```

# Controller dialect summary (from the simulator's own reference)
Simulator: MillLab (static reading of the public source, 2026-11-26).
Supported G-codes: G00, G01, G02, G03, G04, G15, G16, G17, G18, G19, G20, G21, G28, G40, G41, G42, G43, G44, G49, G52, G53, G54, G55, G56, G57, G58, G59, G68, G69, G73, G74, G76, G80, G81, G82, G83, G84, G85, G86, G89, G90, G91, G94, G95, G98, G99
Supported M-codes: M00, M01, M02, M03, M04, M05, M06, M07, M08, M09, M19, M29, M30, M98, M99
Unsupported G-code -> simulator error; unsupported M-code -> ignored.
- axes: X table left/right, Y towards/away, Z spindle up/down; negative Z goes into the part (simulator lesson 1)
- G54: Work zero set automatically to the chosen top corner or centre of the block (default origin 'corner' = front-left); Z0 on the finished top (default) or raw top
- G90_G91: Absolute / incremental programming
- G94_G95: Feed per minute / per revolution
- G43_H: Tool length compensation; without G43 Hnn (or AUTO TOOL COMP) the tip runs one tool length lower - warning
- G41_G42_D: Cutter radius compensation, only simulated in G17; G41/G42 without D -> tool centre on the contour (warning)
- canned_cycles: G73, G74, G76, G81-G86, G89 with G98/G99 return; G80 cancel
- M06: Tool change; cancel G40 / G80 before M06
- stock_shape: rectangular block only


# Geometry source
The drawing is attached to this message as an image. No other geometry data is provided.

# What to deliver
(i) the geometric features and dimensions you extracted, (ii) a manufacturing operation sequence with setups, (iii) toolpath assumptions, (iv) operation-labelled NC code for the simulator, plus one consolidated program per setup where appropriate. Keep operations the simulator cannot represent (e.g. off-axis holes on a 2-axis lathe, fillets needing a form/ball tool) in the operation plan and mark them "simulator_supported": false instead of dropping them.

# Required response format
Answer with exactly these sections, in this order, using fenced code blocks exactly as shown so the team's import script can archive them unchanged.

## 1. Recognized features
```json features
{"features": [{"id": "F01", "type": "...", "description": "...", "dimensions": {"<name>_mm": 0.0}, "location": "...", "source": "<drawing view/callout OR manifest feature id>", "confidence": "high|medium|low", "needs_human_verification": true}],
 "unclear_or_missing": [{"item": "...", "why": "...", "affects": ["OP.."]}]}
```

## 2. Operation plan
```json operations
{"setups": [{"id": "S1", "orientation_and_workholding": "...", "work_zero": "...", "operations": [{"id": "OP10", "name": "...", "features": ["F01"], "tool": "T..", "strategy": "roughing|finishing|drilling|...", "spindle": "...", "feed": "...", "depth_of_cut": "...", "simulator_supported": true, "nc_file": "op_10_<name>.nc"}]}],
 "assumptions": ["..."]}
```

## 3. Toolpath assumptions
Bullet list: approach/retract points, step-downs, radial engagement, compensation use, safe heights, why each tool fits the feature.

## 4. NC programs
One block per operation, then one consolidated block per setup. The info string MUST name the file:
```gcode file=op_10_<name>.nc setup=S1 op=OP10
(...)
```
```gcode file=setup_01_complete.nc setup=S1 op=ALL
(...)
```
Comment every block's purpose in parentheses. Use only codes listed as supported in the dialect summary.

## 5. Uncertainty and limitations
Bullet list of everything the team must verify first (geometry gate G1, process gate G2, code gate G3).
