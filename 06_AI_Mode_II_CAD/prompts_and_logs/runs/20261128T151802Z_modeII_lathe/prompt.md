" is NOT sent to the AI.
-->
=== PROMPT START ===
You are assisting a university team with CNC programming for a teaching simulator. You act as a PROPOSING agent: the team will check every feature, decision and NC line before anything is accepted. The programs are simulation-only candidates.

# Task
Workpiece: APSD-LATHE
Process: turning (2-axis lathe)

Mode: CAD DATA. The geometry source is a machine-readable feature manifest extracted by a Python script from the Onshape CAD model (JSON below). Every value carries a label: CAD_EXTRACTED, GEOMETRICALLY_INFERRED, HUMAN_ANNOTATED or UNKNOWN. Coordinates are in the CAD frame (mm); you must transform them into the machine work frame given in the configuration.

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
```json
{
 "schema": "apsd-cnc-feature-manifest",
 "schema_version": "1.0",
 "label_convention": {
  "CAD_EXTRACTED": "Read directly from the Onshape B-rep or feature list; only unit conversion (m -> mm) or radius -> diameter applied.",
  "GEOMETRICALLY_INFERRED": "Computed by apsd_cam from CAD values (projections, spans, distances, section loops, feature types, patterns). Deterministic and re-runnable, but an interpretation.",
  "HUMAN_ANNOTATED": "Supplied by a named team member with a cited source and date; never merged into the CAD values.",
  "UNKNOWN": "Not available from the CAD data or a verified human source; value is null."
 },
 "evidence_class": "LIVE_ONSHAPE_API",
 "part": {
  "id": "APSD-LATHE",
  "process": "turning",
  "name_in_cad": "LATHE",
  "body_count": 1,
  "material": {
   "value": null,
   "unit": null,
   "label": "UNKNOWN",
   "note": "no material assigned in Onshape (body properties material = null)"
  }
 },
 "units": {
  "length": "mm",
  "angle": "deg",
  "source_length_unit": "m (Onshape getPartStudioBodyDetails: 'All coordinates are in meters')",
  "conversion": "mm = m x 1000, rounded to 0.0001 mm"
 },
 "cad_source": {
  "method": "Onshape REST API (Part Studio body details, feature list, bounding boxes) - course option iii / Chapter 1 Path B",
  "host": "https://cad.onshape.com",
  "api_version": "v17",
  "document_id": "6877e7a6059a24d360e8c6e1",
  "element_id": "147da5f19a2ac767328e5f7f",
  "element_name": "APSD-LATHE-Final",
  "url_context": {
   "wvm": "v",
   "wvm_id": "dd8cc179d8265b20fe3f589e"
  },
  "snapshot_microversion": "dd8cc179d8265b20fe3f589e",
  "element_microversion": "6048fb80fb1f02ebe3846657",
  "named_version": "dd8cc179d8265b20fe3f589e",
  "revision_changed_during_extraction": false,
  "drawing_element": {
   "element_id": "39fec93b315c33208dd4a282",
   "name": "APSD-LATHE-Final",
   "data_type": "onshape-app/drawing",
   "element_microversion": "10f9ffea4217a02c745355ca"
  }
 },
 "extraction": {
  "run_id": "20261128T085834Z_hmac",
  "extracted_utc": "2026-11-28T08:58:34+00:00",
  "evidence_dir": "evidence/20261128T085834Z_hmac_lathe",
  "evidence_files": {
   "01_document.json": "e6b821c3d1f53e8b6f0fc8c978610255edd8ff26c017deb083270bcb0223df2d",
   "03_elements.json": "98bd84cc722f81eca930fa7a0153cb3743cdec756e986e19a8ae8ff5d49f55c7",
   "04_features.json": "a6e36b9605aa42b03d5e7971c2c2d5b85121af73d1ed2a5200d519378b59e1c8",
   "05_parts.json": "5d13653bef58d81f0c650b0ccdee3c44d47fe8d5ca74e5c9f373a060d2f9ce20",
   "06_configuration.json": "a9e1c8465fec04b7660bb75741ec93dfc075e7b7b53a57ec552971c200a52885",
   "07_bodydetails.json": "b790fe5cbe76a60ed564036fa18251c3380a7ec0880caea8503291f18a831eed",
   "08_boundingboxes.json": "58709cf600c7a4c22f9aacdaf4c33ae766739edeef52e0def09b8ccc7495ea4e",
   "09_document_end.json": "33559bf438bb0c75855e48affdd451b3f996ce32ac1ccd0731304478985b7cbe",
   "11_drawing_views.json": "344902e7b46cfe055a78d332f6d96ba03507d7d2476d2c740c618408c2239250",
   "extraction_record.json": "1942303dfe9bf58728fbc4d651803cc03c2ddc3dd508406b35b21ff5e969cf06"
  },
  "pipeline": "apsd_cam (Chapter 2 Part E) on top of vendored Chapter 1 apsd_pipeline",
  "pipeline_version": "1.0.0",
  "vendored_chapter1": {
   "source_commit": "17f6d607b21f0104d4658bf792caa6921f44d409",
   "source_branch": "juli-changes",
   "record": "scripts/vendor_ch1/VENDORED_FROM_CHAPTER1.json"
  },
  "endpoints": {
   "01_document": 200,
   "03_elements": 200,
   "04_features": 200,
   "05_parts": 200,
   "06_configuration": 200,
   "07_bodydetails": 200,
   "08_boundingboxes": 200,
   "11_drawing_views": 200,
   "09_document_end": 200
  },
  "manifest_built_utc": "2026-11-28T08:58:56+00:00",
  "chapter1_fact_builder": "apsd_pipeline.manifest.build_manifest (vendored, unchanged) - facts validated against the Chapter 1 schema"
 },
 "coordinate_system": {
  "frame": "Onshape Part Studio world coordinates (APSD-LATHE-Final tab)",
  "origin": "world origin [0.0, 0.0, 0.0] mm, on the rotation axis at the spigot (small) end face",
  "axes": {
   "rotation_axis_direction": {
    "value": [
     1.0,
     0.0,
     0.0
    ],
    "unit": null,
    "label": "GEOMETRICALLY_INFERRED",
    "evidence": [
     "07_bodydetails.json#/bodies/0/faces/2/surface",
     "07_bodydetails.json#/bodies/0/faces/4/surface",
     "07_bodydetails.json#/bodies/0/faces/6/surface",
     "07_bodydetails.json#/bodies/0/faces/8/surface",
     "07_bodydetails.json#/bodies/0/faces/10/surface",
     "07_bodydetails.json#/bodies/0/faces/24/surface"
    ]
   },
   "axial_coordinate": {
    "value": "a = world X; a = 0 at the spigot end face, a = 210 at the threaded end face",
    "unit": "mm",
    "label": "GEOMETRICALLY_INFERRED",
    "evidence": [
     "07_bodydetails.json#/bodies/0/faces/2/surface",
     "07_bodydetails.json#/bodies/0/faces/4/surface",
     "07_bodydetails.json#/bodies/0/faces/6/surface",
     "07_bodydetails.json#/bodies/0/faces/8/surface",
     "07_bodydetails.json#/bodies/0/faces/10/surface",
     "07_bodydetails.json#/bodies/0/faces/24/surface"
    ]
   },
   "radial_coordinate": {
    "value": "distance from the rotation axis (diameters are reported as diameters)",
    "unit": "mm",
    "label": "GEOMETRICALLY_INFERRED"
   }
  },
  "label": "GEOMETRICALLY_INFERRED",
  "note": "CAD frame only. The lathe work zero (e.g. Z0 on the finished front face, X as diameter in LatheLab) is a process decision in the shared experiment configuration, not CAD data."
 },
 "bounding_box": {
  "min_mm": [
   0.0,
   -50.0,
   -50.0
  ],
  "max_mm": [
   210.0,
   50.0,
   50.0
  ],
  "size_mm": [
   210.0,
   100.0,
   100.0
  ],
  "label": "GEOMETRICALLY_INFERRED",
  "method": "axial extent from analytic face boxes projected on the axis; radial extent = largest external coaxial cylinder (key top at 17.9 mm is inside it)",
  "evidence": [
   "07_bodydetails.json#/bodies/0/faces (analytic face boxes)",
   "08_boundingboxes.json"
  ],
  "cross_check": {
   "onshape_partstudio_boundingbox_mm": {
    "lowY": -50.0,
    "lowZ": -50.0,
    "highX": 212.3232,
    "highY": 50.0,
    "highZ": 50.0,
    "lowX": -0.8803
   },
   "note": "Onshape documents this box as approximate; reported for comparison only"
  }
 },
 "features": [
  {
   "id": "L-AXIS",
   "type": "rotation_axis",
   "description": "Principal rotation (turning) axis",
   "label": "GEOMETRICALLY_INFERRED",
   "dimensions": {
    "overall_axial_length": {
     "value": 210.0,
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces"
     ]
    },
    "max_diameter": {
     "value": 100.0,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/8"
     ]
    }
   },
   "location": {
    "origin": {
     "value": [
      0.0,
      0.0,
      0.0
     ],
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/2/surface",
      "07_bodydetails.json#/bodies/0/faces/4/surface",
      "07_bodydetails.json#/bodies/0/faces/6/surface",
      "07_bodydetails.json#/bodies/0/faces/8/surface",
      "07_bodydetails.json#/bodies/0/faces/10/surface",
      "07_bodydetails.json#/bodies/0/faces/24/surface"
     ]
    },
    "direction": {
     "value": [
      1.0,
      0.0,
      0.0
     ],
     "unit": null,
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/2/surface",
      "07_bodydetails.json#/bodies/0/faces/4/surface",
      "07_bodydetails.json#/bodies/0/faces/6/surface",
      "07_bodydetails.json#/bodies/0/faces/8/surface",
      "07_bodydetails.json#/bodies/0/faces/10/surface",
      "07_bodydetails.json#/bodies/0/faces/24/surface"
     ]
    }
   },
   "evidence": [
    "07_bodydetails.json#/bodies/0/faces/2/surface",
    "07_bodydetails.json#/bodies/0/faces/4/surface",
    "07_bodydetails.json#/bodies/0/faces/6/surface",
    "07_bodydetails.json#/bodies/0/faces/8/surface",
    "07_bodydetails.json#/bodies/0/faces/10/surface",
    "07_bodydetails.json#/bodies/0/faces/24/surface"
   ],
   "extraction_method": "9 coaxial rotational faces, largest total area of 7 axis groups; feature list: revolve FYIWnfYGm1s7a11_0 about sketch line Rj308cwR6Gtk",
   "confidence": "high",
   "uncertainty": "none identified",
   "needs_human_verification": false
  },
  {
   "id": "L-FACE-01",
   "type": "end_face",
   "description": "Planar face normal to the axis at a = 0 mm (594.705 mm2) - part end face",
   "label": "CAD_EXTRACTED",
   "dimensions": {
    "area": {
     "value": 594.705,
     "unit": "mm2",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/1"
     ]
    }
   },
   "location": {
    "axial_position": {
     "value": 0.0,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/1"
     ],
     "note": "plane origin along the world-aligned axis"
    }
   },
   "evidence": [
    "07_bodydetails.json#/bodies/0/faces/1"
   ],
   "extraction_method": "geometry_parser: plane normal parallel to the rotation axis",
   "confidence": "high",
   "uncertainty": "none identified",
   "needs_human_verification": false
  },
  {
   "id": "L-FACE-02",
   "type": "shoulder_face",
   "description": "Planar face normal to the axis at a = 20 mm (2041.92 mm2)",
   "label": "CAD_EXTRACTED",
   "dimensions": {
    "area": {
     "value": 2041.918,
     "unit": "mm2",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/11"
     ]
    }
   },
   "location": {
    "axial_position": {
     "value": 20.0,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/11"
     ],
     "note": "plane origin along the world-aligned axis"
    }
   },
   "evidence": [
    "07_bodydetails.json#/bodies/0/faces/11"
   ],
   "extraction_method": "geometry_parser: plane normal parallel to the rotation axis",
   "confidence": "high",
   "uncertainty": "none identified",
   "needs_human_verification": false
  },
  {
   "id": "L-FACE-03",
   "type": "shoulder_face",
   "description": "Planar face normal to the axis at a = 41.42 mm (7.472 mm2)",
   "label": "CAD_EXTRACTED",
   "dimensions": {
    "area": {
     "value": 7.472,
     "unit": "mm2",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/0"
     ]
    }
   },
   "location": {
    "axial_position": {
     "value": 41.42,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/0"
     ],
     "note": "plane origin along the world-aligned axis"
    }
   },
   "evidence": [
    "07_bodydetails.json#/bodies/0/faces/0"
   ],
   "extraction_method": "geometry_parser: plane normal parallel to the rotation axis",
   "confidence": "high",
   "uncertainty": "none identified",
   "needs_human_verification": false
  },
  {
   "id": "L-FACE-04",
   "type": "shoulder_face",
   "description": "Planar face normal to the axis at a = 41.42 mm (7.782 mm2)",
   "label": "CAD_EXTRACTED",
   "dimensions": {
    "area": {
     "value": 7.782,
     "unit": "mm2",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/37"
     ]
    }
   },
   "location": {
    "axial_position": {
     "value": 41.42,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/37"
     ],
     "note": "plane origin along the world-aligned axis"
    }
   },
   "evidence": [
    "07_bodydetails.json#/bodies/0/faces/37"
   ],
   "extraction_method": "geometry_parser: plane normal parallel to the rotation axis",
   "confidence": "high",
   "uncertainty": "none identified",
   "needs_human_verification": false
  },
  {
   "id": "L-FACE-05",
   "type": "shoulder_face",
   "description": "Planar face normal to the axis at a = 60 mm (4005.53 mm2)",
   "label": "CAD_EXTRACTED",
   "dimensions": {
    "area": {
     "value": 4005.531,
     "unit": "mm2",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/9"
     ]
    }
   },
   "location": {
    "axial_position": {
     "value": 60.0,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/9"
     ],
     "note": "plane origin along the world-aligned axis"
    }
   },
   "evidence": [
    "07_bodydetails.json#/bodies/0/faces/9"
   ],
   "extraction_method": "geometry_parser: plane normal parallel to the rotation axis",
   "confidence": "high",
   "uncertainty": "none identified",
   "needs_human_verification": false
  },
  {
   "id": "L-FACE-06",
   "type": "shoulder_face",
   "description": "Planar face normal to the axis at a = 80 mm (5026.55 mm2)",
   "label": "CAD_EXTRACTED",
   "dimensions": {
    "area": {
     "value": 5026.548,
     "unit": "mm2",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/7"
     ]
    }
   },
   "location": {
    "axial_position": {
     "value": 80.0,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/7"
     ],
     "note": "plane origin along the world-aligned axis"
    }
   },
   "evidence": [
    "07_bodydetails.json#/bodies/0/faces/7"
   ],
   "extraction_method": "geometry_parser: plane normal parallel to the rotation axis",
   "confidence": "high",
   "uncertainty": "none identified",
   "needs_human_verification": false
  },
  {
   "id": "L-FACE-07",
   "type": "shoulder_face",
   "description": "Planar face normal to the axis at a = 85 mm (235.052 mm2)",
   "label": "CAD_EXTRACTED",
   "dimensions": {
    "area": {
     "value": 235.052,
     "unit": "mm2",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/33"
     ]
    }
   },
   "location": {
    "axial_position": {
     "value": 85.0,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/33"
     ],
     "note": "plane origin along the world-aligned axis"
    }
   },
   "evidence": [
    "07_bodydetails.json#/bodies/0/faces/33"
   ],
   "extraction_method": "geometry_parser: plane normal parallel to the rotation axis",
   "confidence": "high",
   "uncertainty": "none identified",
   "needs_human_verification": false
  },
  {
   "id": "L-FACE-08",
   "type": "shoulder_face",
   "description": "Planar face normal to the axis at a = 170 mm (574.126 mm2)",
   "label": "CAD_EXTRACTED",
   "dimensions": {
    "area": {
     "value": 574.126,
     "unit": "mm2",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/3"
     ]
    }
   },
   "location": {
    "axial_position": {
     "value": 170.0,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/3"
     ],
     "note": "plane origin along the world-aligned axis"
    }
   },
   "evidence": [
    "07_bodydetails.json#/bodies/0/faces/3"
   ],
   "extraction_method": "geometry_parser: plane normal parallel to the rotation axis",
   "confidence": "high",
   "uncertainty": "none identified",
   "needs_human_verification": false
  },
  {
   "id": "L-FACE-09",
   "type": "end_face",
   "description": "Planar face normal to the axis at a = 210 mm (1021.59 mm2) - part end face",
   "label": "CAD_EXTRACTED",
   "dimensions": {
    "area": {
     "value": 1021.585,
     "unit": "mm2",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/5"
     ]
    }
   },
   "location": {
    "axial_position": {
     "value": 210.0,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/5"
     ],
     "note": "plane origin along the world-aligned axis"
    }
   },
   "evidence": [
    "07_bodydetails.json#/bodies/0/faces/5"
   ],
   "extraction_method": "geometry_parser: plane normal parallel to the rotation axis",
   "confidence": "high",
   "uncertainty": "none identified",
   "needs_human_verification": false
  },
  {
   "id": "L-OD-01",
   "type": "external_cylinder",
   "description": "External diameter Ø29.9 from a = 0 to 20 mm",
   "label": "CAD_EXTRACTED",
   "dimensions": {
    "diameter": {
     "value": 29.9,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/2"
     ],
     "note": "2 x cylinder radius"
    },
    "length": {
     "value": 20.0,
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/2"
     ]
    }
   },
   "location": {
    "axial_from": {
     "value": 0.0,
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/2"
     ]
    },
    "axial_to": {
     "value": 20.0,
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/2"
     ]
    }
   },
   "evidence": [
    "07_bodydetails.json#/bodies/0/faces/2"
   ],
   "extraction_method": "geometry_parser: external coaxial cylinder (orientation=true), span from face box projected on the axis",
   "confidence": "high",
   "uncertainty": "none identified",
   "needs_human_verification": false
  },
  {
   "id": "L-OD-02",
   "type": "external_cylinder",
   "description": "External diameter Ø60 from a = 20 to 55 mm",
   "label": "CAD_EXTRACTED",
   "dimensions": {
    "diameter": {
     "value": 60.0,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/10"
     ],
     "note": "2 x cylinder radius"
    },
    "length": {
     "value": 35.0,
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/10"
     ]
    }
   },
   "location": {
    "axial_from": {
     "value": 20.0,
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/10"
     ]
    },
    "axial_to": {
     "value": 55.0,
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/10"
     ]
    }
   },
   "evidence": [
    "07_bodydetails.json#/bodies/0/faces/10"
   ],
   "extraction_method": "geometry_parser: external coaxial cylinder (orientation=true), span from face box projected on the axis",
   "confidence": "high",
   "uncertainty": "none identified",
   "needs_human_verification": false
  },
  {
   "id": "L-OD-03",
   "type": "external_cylinder",
   "description": "External diameter Ø100 from a = 60 to 80 mm",
   "label": "CAD_EXTRACTED",
   "dimensions": {
    "diameter": {
     "value": 100.0,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/8"
     ],
     "note": "2 x cylinder radius"
    },
    "length": {
     "value": 20.0,
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/8"
     ]
    }
   },
   "location": {
    "axial_from": {
     "value": 60.0,
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/8"
     ]
    },
    "axial_to": {
     "value": 80.0,
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/8"
     ]
    }
   },
   "evidence": [
    "07_bodydetails.json#/bodies/0/faces/8"
   ],
   "extraction_method": "geometry_parser: external coaxial cylinder (orientation=true), span from face box projected on the axis",
   "confidence": "high",
   "uncertainty": "none identified",
   "needs_human_verification": false
  },
  {
   "id": "L-OD-04",
   "type": "external_cylinder",
   "description": "External diameter Ø50 from a = 85 to 210 mm",
   "label": "CAD_EXTRACTED",
   "dimensions": {
    "diameter": {
     "value": 50.0,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/6"
     ],
     "note": "2 x cylinder radius"
    },
    "length": {
     "value": 125.0,
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/6"
     ]
    }
   },
   "location": {
    "axial_from": {
     "value": 85.0,
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/6"
     ]
    },
    "axial_to": {
     "value": 210.0,
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/6"
     ]
    }
   },
   "evidence": [
    "07_bodydetails.json#/bodies/0/faces/6"
   ],
   "extraction_method": "geometry_parser: external coaxial cylinder (orientation=true), span from face box projected on the axis",
   "confidence": "high",
   "uncertainty": "none identified",
   "needs_human_verification": false
  },
  {
   "id": "L-BLEND-01",
   "type": "concave_fillet",
   "description": "Concave R5 blend between Ø60 and Ø100",
   "label": "CAD_EXTRACTED",
   "dimensions": {
    "radius": {
     "value": 5.0,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/24"
     ],
     "note": "torus minor radius"
    }
   },
   "location": {
    "axial_span": {
     "value": [
      55.0,
      60.0
     ],
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/24"
     ]
    }
   },
   "evidence": [
    "07_bodydetails.json#/bodies/0/faces/24"
   ],
   "extraction_method": "geometry_parser: coaxial torus, orientation=false (concave)",
   "confidence": "high",
   "uncertainty": "none identified",
   "needs_human_verification": false
  },
  {
   "id": "L-BLEND-02",
   "type": "concave_fillet",
   "description": "Concave R5 blend between Ø100 and Ø50",
   "label": "CAD_EXTRACTED",
   "dimensions": {
    "radius": {
     "value": 5.0,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/25"
     ],
     "note": "torus minor radius"
    }
   },
   "location": {
    "axial_span": {
     "value": [
      80.0,
      85.0
     ],
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/25"
     ]
    }
   },
   "evidence": [
    "07_bodydetails.json#/bodies/0/faces/25"
   ],
   "extraction_method": "geometry_parser: coaxial torus, orientation=false (concave)",
   "confidence": "high",
   "uncertainty": "none identified",
   "needs_human_verification": false
  },
  {
   "id": "L-BORE-01",
   "type": "internal_cylinder",
   "description": "Internal diameter Ø12 from a = 0 to 41.42 mm, open at a = 0",
   "label": "CAD_EXTRACTED",
   "dimensions": {
    "diameter": {
     "value": 12.0,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/38"
     ]
    },
    "length": {
     "value": 41.42,
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/38"
     ]
    }
   },
   "location": {
    "axial_from": {
     "value": 0.0,
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/38"
     ]
    },
    "axial_to": {
     "value": 41.42,
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/38"
     ]
    }
   },
   "evidence": [
    "07_bodydetails.json#/bodies/0/faces/38",
    "04_features.json#/features/5"
   ],
   "extraction_method": "geometry_parser: internal coaxial cylinder (orientation=false)",
   "confidence": "medium",
   "uncertainty": "feature-list Hole parameter says Ø14 x 41.42, evaluated geometry says Ø12; the evaluated geometry is used, the CAD owner should resolve the inconsistency",
   "needs_human_verification": true
  },
  {
   "id": "L-BORE-02",
   "type": "internal_cylinder",
   "description": "Internal diameter Ø13 from a = 41.42 to 170 mm, internal step (not open to an end face)",
   "label": "CAD_EXTRACTED",
   "dimensions": {
    "diameter": {
     "value": 13.0,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/26"
     ]
    },
    "length": {
     "value": 128.58,
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/26"
     ]
    }
   },
   "location": {
    "axial_from": {
     "value": 41.42,
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/26"
     ]
    },
    "axial_to": {
     "value": 170.0,
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/26"
     ]
    }
   },
   "evidence": [
    "07_bodydetails.json#/bodies/0/faces/26"
   ],
   "extraction_method": "geometry_parser: internal coaxial cylinder (orientation=false)",
   "confidence": "high",
   "uncertainty": "none identified",
   "needs_human_verification": false
  },
  {
   "id": "L-BORE-03",
   "type": "internal_cylinder",
   "description": "Internal diameter Ø30 from a = 170 to 210 mm, open at a = 210",
   "label": "CAD_EXTRACTED",
   "dimensions": {
    "diameter": {
     "value": 30.0,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/4"
     ]
    },
    "length": {
     "value": 40.0,
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/4"
     ]
    }
   },
   "location": {
    "axial_from": {
     "value": 170.0,
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/4"
     ]
    },
    "axial_to": {
     "value": 210.0,
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/4"
     ]
    }
   },
   "evidence": [
    "07_bodydetails.json#/bodies/0/faces/4"
   ],
   "extraction_method": "geometry_parser: internal coaxial cylinder (orientation=false)",
   "confidence": "high",
   "uncertainty": "none identified",
   "needs_human_verification": false
  },
  {
   "id": "L-THREAD-EXT-01",
   "type": "external_thread_modelled",
   "description": "External helical thread modelled in CAD (threadCreator), pitch 5 mm, near Ø50",
   "label": "CAD_EXTRACTED",
   "dimensions": {
    "pitch": {
     "value": 5.0,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "04_features.json#/features/10",
      "04_features.json#/features/10/parameters/5/value",
      "04_features.json#/features/10/parameters/7/expression"
     ]
    },
    "major_diameter_parameter": {
     "value": 25.0,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "04_features.json#/features/10",
      "04_features.json#/features/10/parameters/5/value",
      "04_features.json#/features/10/parameters/7/expression"
     ],
     "note": "third-party FeatureScript parameter; matches none of the diameters at the thread region - NOT a usable thread size"
    },
    "designation_standard_class": {
     "value": null,
     "unit": null,
     "label": "UNKNOWN",
     "note": "not in the CAD data: the reported label '1.9685-5.08' / profile 'ANSI_STD' is FeatureScript text, not a verified designation"
    },
    "handedness": {
     "value": "right-hand",
     "unit": null,
     "label": "CAD_EXTRACTED",
     "evidence": [
      "04_features.json#/features/10",
      "04_features.json#/features/10/parameters/5/value",
      "04_features.json#/features/10/parameters/7/expression"
     ]
    }
   },
   "location": {
    "axial_span_approx": {
     "value": [
      82.671,
      210.0
     ],
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/30",
      "07_bodydetails.json#/bodies/0/faces/31",
      "07_bodydetails.json#/bodies/0/faces/32"
     ],
     "note": "from LOOSE bounding boxes of non-analytic helical faces (can exceed true extent by ~1 mm)"
    },
    "nominal_diameter_region": {
     "value": [
      50.0
     ],
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/30",
      "07_bodydetails.json#/bodies/0/faces/31",
      "07_bodydetails.json#/bodies/0/faces/32"
     ]
    }
   },
   "evidence": [
    "04_features.json#/features/10",
    "04_features.json#/features/10/parameters/5/value",
    "04_features.json#/features/10/parameters/7/expression",
    "07_bodydetails.json#/bodies/0/faces/30",
    "07_bodydetails.json#/bodies/0/faces/31",
    "07_bodydetails.json#/bodies/0/faces/32"
   ],
   "extraction_method": "vendored feature_parser (threadCreator parameters) + locate_freeform_faces (helical faces)",
   "confidence": "medium",
   "uncertainty": "threadCreator parameter majorDiameter = 25 mm matches none of the diameters at the threaded region [50.0] mm; this third-party parameter is reported but not interpreted",
   "needs_human_verification": true
  },
  {
   "id": "L-THREAD-INT-01",
   "type": "internal_thread_modelled",
   "description": "Internal helical thread modelled in CAD (threadCreator), pitch 2 mm, near Ø12/13",
   "label": "CAD_EXTRACTED",
   "dimensions": {
    "pitch": {
     "value": 2.0,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "04_features.json#/features/11",
      "04_features.json#/features/11/parameters/5/value",
      "04_features.json#/features/11/parameters/7/expression"
     ]
    },
    "major_diameter_parameter": {
     "value": 25.0,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "04_features.json#/features/11",
      "04_features.json#/features/11/parameters/5/value",
      "04_features.json#/features/11/parameters/7/expression"
     ],
     "note": "third-party FeatureScript parameter; matches none of the diameters at the thread region - NOT a usable thread size"
    },
    "designation_standard_class": {
     "value": null,
     "unit": null,
     "label": "UNKNOWN",
     "note": "not in the CAD data: the reported label '0.5118-12.7' / profile 'ANSI_STD' is FeatureScript text, not a verified designation"
    },
    "handedness": {
     "value": "right-hand",
     "unit": null,
     "label": "CAD_EXTRACTED",
     "evidence": [
      "04_features.json#/features/11",
      "04_features.json#/features/11/parameters/5/value",
      "04_features.json#/features/11/parameters/7/expression"
     ]
    }
   },
   "location": {
    "axial_span_approx": {
     "value": [
      0.0,
      42.296
     ],
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/34",
      "07_bodydetails.json#/bodies/0/faces/35",
      "07_bodydetails.json#/bodies/0/faces/36"
     ],
     "note": "from LOOSE bounding boxes of non-analytic helical faces (can exceed true extent by ~1 mm)"
    },
    "nominal_diameter_region": {
     "value": [
      12.0,
      13.0
     ],
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/34",
      "07_bodydetails.json#/bodies/0/faces/35",
      "07_bodydetails.json#/bodies/0/faces/36"
     ]
    }
   },
   "evidence": [
    "04_features.json#/features/11",
    "04_features.json#/features/11/parameters/5/value",
    "04_features.json#/features/11/parameters/7/expression",
    "07_bodydetails.json#/bodies/0/faces/34",
    "07_bodydetails.json#/bodies/0/faces/35",
    "07_bodydetails.json#/bodies/0/faces/36"
   ],
   "extraction_method": "vendored feature_parser (threadCreator parameters) + locate_freeform_faces (helical faces)",
   "confidence": "medium",
   "uncertainty": "threadCreator parameter majorDiameter = 25 mm matches none of the diameters at the threaded region [12.0, 13.0] mm; this third-party parameter is reported but not interpreted",
   "needs_human_verification": true
  },
  {
   "id": "L-HOLES-01",
   "type": "axial_hole_pattern",
   "description": "6 x Ø3.52 blind holes parallel to the axis on PCD 46",
   "label": "GEOMETRICALLY_INFERRED",
   "dimensions": {
    "diameter": {
     "value": 3.52,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/12",
      "07_bodydetails.json#/bodies/0/faces/14",
      "07_bodydetails.json#/bodies/0/faces/16"
     ]
    },
    "count": {
     "value": 6,
     "unit": null,
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/12",
      "07_bodydetails.json#/bodies/0/faces/14",
      "07_bodydetails.json#/bodies/0/faces/16"
     ],
     "note": "one cylinder face per hole observed"
    },
    "pitch_circle_diameter": {
     "value": 46.0,
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/12",
      "07_bodydetails.json#/bodies/0/faces/14",
      "07_bodydetails.json#/bodies/0/faces/16"
     ]
    },
    "depth": {
     "value": 4.1,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "04_features.json#/features/3"
     ],
     "note": "extrude REMOVE, BLIND"
    }
   },
   "location": {
    "angular_positions": {
     "value": [
      0.0,
      60.0,
      120.0,
      180.0,
      240.0,
      300.0
     ],
     "unit": "deg",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/12",
      "07_bodydetails.json#/bodies/0/faces/14",
      "07_bodydetails.json#/bodies/0/faces/16"
     ],
     "note": "angle origin = first hole found; only the spacing is meaningful"
    },
    "hole_bottom_axial_position": {
     "value": 24.1,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json (6 small planes normal to the axis)"
     ]
    },
    "entry_face_axial_position": {
     "value": 20.0,
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "hole bottom - depth"
     ]
    }
   },
   "evidence": [
    "07_bodydetails.json#/bodies/0/faces/12",
    "07_bodydetails.json#/bodies/0/faces/14",
    "07_bodydetails.json#/bodies/0/faces/16",
    "04_features.json#/features/3"
   ],
   "extraction_method": "geometry_parser: off-axis cylinders parallel to the axis grouped by radius and distance; depth from the cut feature",
   "confidence": "high",
   "uncertainty": "none identified",
   "needs_human_verification": false
  },
  {
   "id": "L-KEY-01",
   "type": "raised_key",
   "description": "Raised key on the Ø29.9 spigot: flat top 17.9 mm from the axis, two parallel side flats 7.98 mm apart",
   "label": "GEOMETRICALLY_INFERRED",
   "dimensions": {
    "width": {
     "value": 7.98,
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/27",
      "07_bodydetails.json#/bodies/0/faces/28",
      "07_bodydetails.json#/bodies/0/faces/29",
      "04_features.json#/features/9"
     ],
     "note": "2 x distance of the side flats from the axis"
    },
    "top_distance_from_axis": {
     "value": 17.9,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/27",
      "07_bodydetails.json#/bodies/0/faces/28",
      "07_bodydetails.json#/bodies/0/faces/29",
      "04_features.json#/features/9"
     ]
    },
    "length": {
     "value": 20.0,
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/27",
      "07_bodydetails.json#/bodies/0/faces/28",
      "07_bodydetails.json#/bodies/0/faces/29",
      "04_features.json#/features/9"
     ]
    }
   },
   "location": {
    "axial_span": {
     "value": [
      0.0,
      20.0
     ],
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/27",
      "07_bodydetails.json#/bodies/0/faces/28",
      "07_bodydetails.json#/bodies/0/faces/29",
      "04_features.json#/features/9"
     ]
    }
   },
   "evidence": [
    "07_bodydetails.json#/bodies/0/faces/27",
    "07_bodydetails.json#/bodies/0/faces/28",
    "07_bodydetails.json#/bodies/0/faces/29",
    "04_features.json#/features/9"
   ],
   "extraction_method": "geometry_parser: planes parallel to the axis; ADD extrude 'ADD (extrude)' in the feature list",
   "confidence": "high",
   "uncertainty": "angular orientation of the key relative to the hole pattern is not reported by this extractor",
   "needs_human_verification": false
  }
 ],
 "relationships": [
  {
   "id": "L-REL-01",
   "description": "L/D ratio (overall length / max diameter)",
   "value": 2.1,
   "unit": null,
   "label": "GEOMETRICALLY_INFERRED",
   "method": "computed from the listed features",
   "evidence": [
    "features L-AXIS"
   ],
   "features": [
    "L-AXIS"
   ]
  },
  {
   "id": "L-REL-02",
   "description": "Flange (Ø100) thickness",
   "value": 20.0,
   "unit": "mm",
   "label": "GEOMETRICALLY_INFERRED",
   "method": "computed from the listed features",
   "evidence": [
    "features L-OD-03"
   ],
   "features": [
    "L-OD-03"
   ]
  }
 ],
 "human_annotations": [],
 "missing_data": [
  {
   "item": "material",
   "label": "UNKNOWN",
   "reason": "no material assigned in Onshape",
   "needed_for": "cutting speeds/feeds (G2), simulator material setting"
  },
  {
   "item": "raw stock form and size",
   "label": "UNKNOWN",
   "reason": "process decision (Part B route sheet), not CAD",
   "needed_for": "simulator stock, roughing passes"
  },
  {
   "item": "tolerances, fits, surface finish",
   "label": "UNKNOWN",
   "reason": "not in the B-rep; drawing annotations are not returned by the API",
   "needed_for": "finishing strategy, inspection"
  },
  {
   "item": "thread designations, standards and tolerance classes (external p=5, internal p=2)",
   "label": "UNKNOWN",
   "reason": "threadCreator text is not a verified designation; majorDiameter parameter inconsistent",
   "needed_for": "threading cycle (G76/G92) depth and diameters"
  },
  {
   "item": "chamfers / edge breaks",
   "label": "UNKNOWN",
   "reason": "none modelled in CAD (Chapter 1 fact 'chamfers' = absent); drawing notes are not available through the API",
   "needed_for": "finishing passes"
  },
  {
   "item": "angular orientation of the key relative to the Ø3.52 hole pattern",
   "label": "UNKNOWN",
   "reason": "not computed by this extractor",
   "needed_for": "milling/indexing of the key and holes (not turning)"
  }
 ],
 "limitations": [
  "Lathe facts come from the Chapter 1 builder (vendored unchanged); its own limitations apply (see vendor_ch1/apsd_pipeline/manifest.py).",
  "Thread regions are located with loose bounding boxes of helical faces; thread sizes are not derivable from this model.",
  "No drawing annotation text is available through the Onshape API; drawing-only information enters only as HUMAN_ANNOTATED entries.",
  "The CAD frame is not the machining frame: the lathe work zero and X-as-diameter convention are set in the shared experiment configuration."
 ]
}
```

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
