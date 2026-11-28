" is NOT sent to the AI.
-->
=== PROMPT START ===
You are assisting a university team with CNC programming for a teaching simulator. You act as a PROPOSING agent: the team will check every feature, decision and NC line before anything is accepted. The programs are simulation-only candidates.

# Task
Workpiece: APSD-LATHE
Process: turning (2-axis lathe)

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
 "APSD-LATHE": {
  "part_id": {
   "value": "APSD-LATHE",
   "class": "CAD_EXTRACTED",
   "status": "CONFIRMED",
   "source": "brief Table 2.1; Onshape tab APSD-LATHE-Final"
  },
  "cad_revision": {
   "value": {
    "document": "6877e7a6059a24d360e8c6e1",
    "named_version": "Ch2-Final",
    "version_id": "dd8cc179d8265b20fe3f589e",
    "element": "147da5f19a2ac767328e5f7f (APSD-LATHE-Final)",
    "model_microversion": "4d05edae182b19aa4ea1f30d"
   },
   "class": "CAD_EXTRACTED",
   "status": "CONFIRMED",
   "source": "Onshape named version 'Ch2-Final' (created 2026-11-28 by the team); 06 evidence 20261128T085834Z_hmac_lathe"
  },
  "machine_type": {
   "value": "2-axis CNC slant-bed lathe, turret behind the centre line (rear tool post), as modelled by LatheLab",
   "class": "SIMULATOR_SETTING",
   "status": "CONFIRMED",
   "source": "simulator_dialect.json lathelab.conventions.tool_post"
  },
  "controller_dialect": {
   "value": "Fanuc-style lathe G-code as implemented by LatheLab: X = DIAMETER (X0 spindle centre line), Z axial; U/W incremental; G90 = OD/ID turning BOX CYCLE (not absolute mode), G91 unsupported; G94 facing cycle; G98/G99 feed per min/rev; G96 CSS with G50 S limit; T0101 tool/offset format; cycles G70-G76, G92; supported G/M lists in simulator_dialect.json",
   "class": "SIMULATOR_SETTING",
   "status": "CONFIRMED",
   "source": "simulator_dialect.json (static reading of the simulator source, 2026-11-26) - the team must still test each used command in LatheLab (brief 2.5 'Lathe programming checks')"
  },
  "machine_limits": {
   "value": "max 4000 rpm, rapid 12000 mm/min",
   "class": "SIMULATOR_SETTING",
   "status": "CONFIRMED",
   "source": "simulator_dialect.json lathelab.conventions.machine_limits (defaults)"
  },
  "stock": {
   "value": {
    "type": "solid round bar",
    "diameter_mm": 105,
    "length_mm": 240,
    "existing_bore_mm": 0,
    "face_allowance_beyond_Z0_mm": 1,
    "length_held_in_jaws_mm": 25,
    "note": "LatheLab: the bar sticks out of the chuck by (length - grip); Z0 is the finished front face, the raw bar ends at Z+1."
   },
   "class": "HUMAN_APPROVED",
   "status": "CONFIRMED",
   "source": "02_Process_Plans/tooling_stock_setups.pdf (Part B, Team01, 2026-11-24) section 1.1 (LatheLab 'Workpiece (bar stock)' dialog); 02_Process_Plans/lathe_route_sheet.pdf (Part B, Team01, 2026-11-24) header; entered 2026-11-28 on the instruction of a team member; values copied, not changed"
  },
  "material": {
   "value": "Steel C45 (1045) - LatheLab material preset 'Steel C45 (1045)'",
   "class": "HUMAN_APPROVED",
   "status": "CONFIRMED",
   "source": "02_Process_Plans/tooling_stock_setups.pdf (Part B, Team01, 2026-11-24) section 1.1; 02_Process_Plans/lathe_route_sheet.pdf (Part B, Team01, 2026-11-24); entered 2026-11-28 on the instruction of a team member; values copied, not changed"
  },
  "work_origin": {
   "value": {
    "setup_1": "X0 on the spindle centre line (X programmed as DIAMETER); Z0 on the finished front face; -Z towards the chuck.",
    "setup_2": "Part reversed. X0 on the spindle centre line; Z0 on the finished rear face; -Z towards the chuck."
   },
   "class": "HUMAN_APPROVED",
   "status": "CONFIRMED",
   "source": "02_Process_Plans/tooling_stock_setups.pdf (Part B, Team01, 2026-11-24) section 1.2; 02_Process_Plans/lathe_route_sheet.pdf (Part B, Team01, 2026-11-24) headers of setups 1 and 2; entered 2026-11-28 on the instruction of a team member; values copied, not changed"
  },
  "setups": {
   "value": {
    "setup_1": "Raw bar in the chuck (25 mm held). Machines the 'front' end = the end that carries the external thread. Facing establishes Z0 (finished front face).",
    "setup_2": "Part reversed; finished surfaces protected. Machines the opposite ('rear') end. The rear facing cut establishes Z0 (finished rear face).",
    "programs": "One separate program per setup. Each setup is simulated on its own in LatheLab (the stock dialog only loads a raw bar).",
    "off_lathe_features": "Features that 2-axis turning cannot produce (off-axis holes, keys, flats) are made later on a 3-axis mill in a secondary setup (Part B route sheet ops 230-250). They are OUT OF SCOPE for the lathe NC programs: list them as such, do not program them."
   },
   "class": "HUMAN_APPROVED",
   "status": "CONFIRMED",
   "source": "02_Process_Plans/lathe_route_sheet.pdf setups 1-2 and ops 230-250; human lathe programs 03_Lathe/setup_01_complete.nc and setup_02_complete.nc (values as used there); approved 2026-11-28 by a team member (Part E) in the Claude Code session"
  },
  "workholding": {
   "value": {
    "setup_1": "3-jaw chuck, 25 mm of the raw bar held",
    "setup_2": "protected chuck arrangement on a finished surface; grip surface and grip length are not specified by the team (accepted)"
   },
   "class": "HUMAN_APPROVED",
   "status": "CONFIRMED",
   "source": "02_Process_Plans/lathe_route_sheet.pdf headers; 02_Process_Plans/tooling_stock_setups.pdf section 1.1; approved 2026-11-28 by a team member (Part E) in the Claude Code session"
  },
  "tools": {
   "value": {
    "turret": [
     {
      "T": "T01",
      "type": "OD turning",
      "name": "OD rough CNMG 80deg R0.8",
      "nose_R": 0.8,
      "tip": 3,
      "insert_angle": 80,
      "approach_angle": 95,
      "reach": 15
     },
     {
      "T": "T02",
      "type": "OD turning",
      "name": "OD finish VNMG 35deg R0.4",
      "nose_R": 0.4,
      "tip": 3,
      "insert_angle": 35,
      "approach_angle": 93,
      "reach": 15
     },
     {
      "T": "T03",
      "type": "OD grooving",
      "name": "OD groove 3 mm",
      "nose_R": 0.2,
      "tip": 3,
      "width": 3,
      "reach": 12
     },
     {
      "T": "T04",
      "type": "OD threading",
      "name": "OD thread 60deg",
      "nose_R": 0.05,
      "tip": 8,
      "thread_angle": 60,
      "reach": 15
     },
     {
      "T": "T05",
      "type": "Drill (on centre)",
      "name": "Drill D13",
      "diameter": 13,
      "point_angle": 118,
      "reach": 70
     },
     {
      "T": "T06",
      "type": "Boring bar (ID)",
      "name": "Boring bar D10 DCMT07 55deg R0.4",
      "nose_R": 0.4,
      "tip": 2,
      "insert_angle": 55,
      "approach_angle": 93,
      "bar_diameter": 10,
      "reach": 80
     },
     {
      "T": "T07",
      "type": "Parting-off",
      "name": "Part-off 3 mm",
      "nose_R": 0.1,
      "tip": 3,
      "width": 3,
      "reach": 30
     },
     {
      "T": "T08",
      "type": "OD turning",
      "name": "OD finish DNMG 55deg R0.4",
      "nose_R": 0.4,
      "tip": 3,
      "insert_angle": 55,
      "approach_angle": 93,
      "reach": 15
     },
     {
      "T": "T09",
      "type": "ID threading",
      "name": "ID thread 60deg",
      "nose_R": 0.05,
      "tip": 6,
      "thread_angle": 60,
      "bar_diameter": 12,
      "reach": 15
     },
     {
      "T": "T10",
      "type": "Drill (on centre)",
      "name": "Centre / spot drill D6 90deg",
      "diameter": 6,
      "point_angle": 90,
      "reach": 10
     },
     {
      "T": "T11",
      "type": "ID grooving",
      "name": "ID groove 3 mm",
      "nose_R": 0.2,
      "tip": 2,
      "width": 3,
      "reach": 60
     },
     {
      "T": "T12",
      "type": "Boring bar (ID)",
      "name": "Boring bar D16 CCMT09 80deg R0.8",
      "nose_R": 0.8,
      "tip": 2,
      "insert_angle": 80,
      "approach_angle": 95,
      "bar_diameter": 16,
      "reach": 80
     }
    ],
    "units": "mm and degrees; reach = max. groove depth / drill flute length / bar length",
    "offsets": "offset number = station (T0101 ... T1212); wear X/Z = 0; offset R/T = nose radius / tip number (used by G41/G42)",
    "note": "Tool table used exactly as configured in LatheLab; no tool was changed for reach (team decision)."
   },
   "class": "HUMAN_APPROVED",
   "status": "CONFIRMED",
   "source": "02_Process_Plans/tooling_stock_setups.pdf (Part B, Team01, 2026-11-24) section 1.3, Figures 2-3 (LatheLab 'Tools & offsets'); 02_Process_Plans/lathe_route_sheet.pdf (Part B, Team01, 2026-11-24) assumptions; approved 2026-11-28 by a team member (Part E) in the Claude Code session"
  },
  "cutting_data": {
   "value": {
    "modes": "constant spindle speed G97 (rpm) as planned; feed per revolution G99 (mm/rev)",
    "per_tool": [
     {
      "T": "T01",
      "use": "facing",
      "rpm": 500,
      "feed_mm_rev": 0.15
     },
     {
      "T": "T01",
      "use": "roughing / shoulders",
      "rpm": 500,
      "feed_mm_rev": "0.15-0.20"
     },
     {
      "T": "T02",
      "use": "straight finishing passes",
      "rpm": 800,
      "feed_mm_rev": 0.1
     },
     {
      "T": "T02",
      "use": "profile / radius finishing",
      "rpm": 500,
      "feed_mm_rev": "0.10-0.15"
     },
     {
      "T": "T04",
      "use": "external threading",
      "rpm": 150,
      "feed_mm_rev": "= thread pitch; several passes + spring pass"
     },
     {
      "T": "T05",
      "use": "drilling, incremental (peck)",
      "rpm": 600,
      "feed_mm_rev": 0.12
     },
     {
      "T": "T06",
      "use": "internal roughing and finishing",
      "rpm": 600,
      "feed_mm_rev": "0.08-0.10"
     },
     {
      "T": "T09",
      "use": "internal threading",
      "rpm": 150,
      "feed_mm_rev": "= thread pitch; several passes"
     },
     {
      "T": "T10",
      "use": "centre / spot drilling, 2 mm deep",
      "rpm": 800,
      "feed_mm_rev": 0.08
     }
    ],
    "depth_of_cut": {
     "external_roughing_radial_mm": 2.5,
     "internal_roughing_radial_mm": 1,
     "finishing_allowance": "roughing leaves 0.5 mm per side for the finishing pass"
    },
    "other_tools": "T03, T07, T08, T11, T12 have no approved cutting data"
   },
   "class": "HUMAN_APPROVED",
   "status": "CONFIRMED",
   "source": "02_Process_Plans/lathe_route_sheet.pdf (Part B, Team01, 2026-11-24) speed/feed columns and assumptions; entered 2026-11-28 on the instruction of a team member; values copied, not changed"
  },
  "safety_clearances": {
   "value": {
    "start_and_approach": "Approach point X110 Z2 (outside the bar, 2 mm in front of the face) before every cut; drilling tools approach on the axis at X0 Z2 and retract to Z5.",
    "threading": "Thread passes start from Z10 to give the carriage room to synchronise.",
    "tool_change": "Before every tool change: return to the machine reference with G28 U0 W0 and stop the spindle (M05); then call the next tool.",
    "rapids": "G00 only outside the material; feed moves (G01) for every cut and for retracts along a machined face."
   },
   "class": "HUMAN_APPROVED",
   "status": "CONFIRMED",
   "source": "human lathe programs 03_Lathe/setup_01_complete.nc and setup_02_complete.nc (values as used there); approved 2026-11-28 by a team member (Part E) in the Claude Code session"
  },
  "simulator_setup": {
   "value": "LatheLab: Stock dialog = Part B stock; Tools & offsets = Part B tools; Program check + Operations + Inspection; Check part only with a correctly configured target",
   "class": "SIMULATOR_SETTING",
   "status": "CONFIRMED",
   "source": "brief 2.5 C2/C4"
  }
 }
}
```

# Controller dialect summary (from the simulator's own reference)
Simulator: LatheLab (static reading of the public source, 2026-11-26).
Supported G-codes: G00, G01, G02, G03, G04, G18, G20, G21, G28, G32, G33, G40, G41, G42, G50, G54, G55, G56, G57, G58, G59, G70, G71, G72, G73, G74, G75, G76, G90, G92, G94, G96, G97, G98, G99
Supported M-codes: M00, M01, M02, M03, M04, M05, M07, M08, M09, M30, M40, M41, M42, M43, M44, M98, M99
Unsupported G-code -> simulator error; unsupported M-code -> ignored.
- X: Absolute position in X - always a DIAMETER on a lathe. X0 is the spindle centre line. (simulator reference)
- Z: Absolute axial position. Z0 is normally the finished front face; negative Z is towards the chuck. (simulator reference)
- U_W: Incremental X (diameter change) / incremental Z. Absolute vs incremental is chosen by the ADDRESS (X/Z vs U/W), not by G90/G91.
- G90: OD/ID turning box cycle (NOT absolute mode). G91 is NOT supported.
- G94_G98_G99: G94 = facing box cycle. G98/G99 = feed per minute / per revolution.
- T: Tool call TttOO, e.g. T0101 = tool 01 with offset 01 (nose radius R and tip T from the offset page)
- G96_G50: G96 constant surface speed should be limited with G50 S.. (warning otherwise)
- threading: G76 multiple threading cycle, G92 single pass, G32 single move; use G97 for threading
- tool_post: slant-bed lathe, turret behind the centre line (rear tool post); G02/G03 as in the usual lathe picture (+X up, +Z right)


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
