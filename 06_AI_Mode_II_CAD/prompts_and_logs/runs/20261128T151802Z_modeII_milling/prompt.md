" is NOT sent to the AI.
-->
=== PROMPT START ===
You are assisting a university team with CNC programming for a teaching simulator. You act as a PROPOSING agent: the team will check every feature, decision and NC line before anything is accepted. The programs are simulation-only candidates.

# Task
Workpiece: APSD-MILLING
Process: milling (3-axis vertical machining centre)

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
  "id": "APSD-MILLING",
  "process": "milling",
  "name_in_cad": "MILLING",
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
  "element_id": "20caaefd66e3a40229321161",
  "element_name": "APSD-MILLING",
  "url_context": {
   "wvm": "v",
   "wvm_id": "dd8cc179d8265b20fe3f589e"
  },
  "snapshot_microversion": "dd8cc179d8265b20fe3f589e",
  "element_microversion": "6e87bc46bde3f5e4ceb98f76",
  "named_version": "dd8cc179d8265b20fe3f589e",
  "revision_changed_during_extraction": false,
  "drawing_element": {
   "element_id": "d36cfe272e42345986bdfb77",
   "name": "APSD-MILLING",
   "data_type": "onshape-app/drawing",
   "element_microversion": "282a465b45d21e3562da09e1"
  }
 },
 "extraction": {
  "run_id": "20261128T085839Z_hmac",
  "extracted_utc": "2026-11-28T08:58:39+00:00",
  "evidence_dir": "evidence/20261128T085839Z_hmac_milling",
  "evidence_files": {
   "01_document.json": "33559bf438bb0c75855e48affdd451b3f996ce32ac1ccd0731304478985b7cbe",
   "03_elements.json": "46b2cf3620ccdb0f1266f6b10c07154d62ea739190a2d25653510fb29c125d93",
   "04_features.json": "300a599fa7f3aad72aa39ebdc302841ceb2b7bf3df5f6dc7c80adfc403930bbc",
   "05_parts.json": "02a887f816cdb78fefe232c23a85d9c9b74c72c4def4ae5342cac6aac115dfdd",
   "06_configuration.json": "a9e1c8465fec04b7660bb75741ec93dfc075e7b7b53a57ec552971c200a52885",
   "07_bodydetails.json": "46870d985d0fb3e97963afaa11ae8587686cee16e23cb29c36b301b88880b79b",
   "08_boundingboxes.json": "0e3e2e0d74fdc172934faca3be2417a18147b051816d3c6c672d0caa4da3612c",
   "09_document_end.json": "e6b821c3d1f53e8b6f0fc8c978610255edd8ff26c017deb083270bcb0223df2d",
   "11_drawing_views.json": "2f87ad2d857d0c3d2d7b7bffc2dc1c31206c51fb40be4807555131dfc0a3e512",
   "extraction_record.json": "3f7e1801b78610b5a0c97f671de2e28faa770222c2c514f4bd96c799af4a2b22"
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
  "prismatic_analysis": {
   "bands": [
    {
     "range_mm": [
      -10.0,
      -5.0
     ],
     "slice_height_mm": -7.5,
     "loop_count": 4,
     "void_loops": 2
    },
    {
     "range_mm": [
      -5.0,
      5.0
     ],
     "slice_height_mm": 0.0,
     "loop_count": 4,
     "void_loops": 3
    },
    {
     "range_mm": [
      5.0,
      10.0
     ],
     "slice_height_mm": 7.5,
     "loop_count": 4,
     "void_loops": 2
    },
    {
     "range_mm": [
      10.0,
      14.0
     ],
     "slice_height_mm": 12.0,
     "loop_count": 6,
     "void_loops": 0
    }
   ],
   "face_count": 43,
   "edge_count": 90,
   "vertex_count": 48
  }
 },
 "coordinate_system": {
  "frame": "Onshape Part Studio world coordinates (APSD-MILLING tab)",
  "origin": "world origin = centre of the Ø30 bore axis at mid-thickness of the Ø60 boss (all heights are symmetric about 0)",
  "axes": {
   "tool_axis": {
    "value": "+Z",
    "unit": null,
    "label": "GEOMETRICALLY_INFERRED",
    "evidence": [
     "07_bodydetails.json#/bodies/0/faces"
    ],
    "note": "largest total face area sharing one direction (21347.6 of 21649.4 mm2, 3 direction groups)"
   },
   "plane_axes": {
    "value": [
     "X",
     "Y"
    ],
    "unit": null,
    "label": "CAD_EXTRACTED",
    "note": "world axes perpendicular to the tool axis"
   },
   "is_2_5d": {
    "value": true,
    "unit": null,
    "label": "GEOMETRICALLY_INFERRED",
    "note": "every curved face parallel to the tool axis, every plane perpendicular or parallel to it"
   }
  },
  "label": "GEOMETRICALLY_INFERRED",
  "note": "CAD frame only. The MillLab work zero (G54, e.g. a stock corner with Z0 on the finished top) and the second-setup datum are process decisions in the shared experiment configuration."
 },
 "bounding_box": {
  "min_mm": [
   -30.0,
   -30.0,
   -10.0
  ],
  "max_mm": [
   126.0,
   42.7823,
   14.0
  ],
  "size_mm": [
   156.0,
   72.7823,
   24.0
  ],
  "label": "GEOMETRICALLY_INFERRED",
  "method": "min/max of analytic face boxes and vertices (43 analytic face boxes + 48 vertices)",
  "evidence": [
   "07_bodydetails.json#/bodies/0/faces",
   "07_bodydetails.json#/bodies/0/vertices"
  ],
  "cross_check": {
   "onshape_partstudio_boundingbox_mm": {
    "lowY": -30.0,
    "lowZ": -10.0,
    "highX": 126.0,
    "highY": 42.7823,
    "highZ": 14.0,
    "lowX": -30.0
   },
   "note": "Onshape documents this box as approximate; reported for comparison only"
  }
 },
 "features": [
  {
   "id": "M-LEVEL-01",
   "type": "planar_level",
   "description": "Up-facing planar face(s) at height 14 mm (6 face(s), 57.726 mm2)",
   "label": "CAD_EXTRACTED",
   "dimensions": {
    "total_area": {
     "value": 57.726,
     "unit": "mm2",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/21",
      "07_bodydetails.json#/bodies/0/faces/23",
      "07_bodydetails.json#/bodies/0/faces/25",
      "07_bodydetails.json#/bodies/0/faces/27",
      "07_bodydetails.json#/bodies/0/faces/29",
      "07_bodydetails.json#/bodies/0/faces/31"
     ]
    }
   },
   "location": {
    "height": {
     "value": 14.0,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/21",
      "07_bodydetails.json#/bodies/0/faces/23",
      "07_bodydetails.json#/bodies/0/faces/25",
      "07_bodydetails.json#/bodies/0/faces/27",
      "07_bodydetails.json#/bodies/0/faces/29",
      "07_bodydetails.json#/bodies/0/faces/31"
     ],
     "note": "coordinate along +Z"
    },
    "facing": {
     "value": "+Z",
     "unit": null,
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/21",
      "07_bodydetails.json#/bodies/0/faces/23",
      "07_bodydetails.json#/bodies/0/faces/25",
      "07_bodydetails.json#/bodies/0/faces/27",
      "07_bodydetails.json#/bodies/0/faces/29",
      "07_bodydetails.json#/bodies/0/faces/31"
     ],
     "note": "outward normal from plane normal and face orientation"
    }
   },
   "evidence": [
    "07_bodydetails.json#/bodies/0/faces/21",
    "07_bodydetails.json#/bodies/0/faces/23",
    "07_bodydetails.json#/bodies/0/faces/25",
    "07_bodydetails.json#/bodies/0/faces/27",
    "07_bodydetails.json#/bodies/0/faces/29",
    "07_bodydetails.json#/bodies/0/faces/31"
   ],
   "extraction_method": "prismatic: planes perpendicular to the tool axis grouped by height and facing side",
   "confidence": "high",
   "uncertainty": "none identified",
   "needs_human_verification": false,
   "access_direction": "+Z side (top setup)"
  },
  {
   "id": "M-LEVEL-02",
   "type": "planar_level",
   "description": "Up-facing planar face(s) at height 10 mm (2 face(s), 3108.69 mm2)",
   "label": "CAD_EXTRACTED",
   "dimensions": {
    "total_area": {
     "value": 3108.693,
     "unit": "mm2",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/1",
      "07_bodydetails.json#/bodies/0/faces/11"
     ]
    }
   },
   "location": {
    "height": {
     "value": 10.0,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/1",
      "07_bodydetails.json#/bodies/0/faces/11"
     ],
     "note": "coordinate along +Z"
    },
    "facing": {
     "value": "+Z",
     "unit": null,
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/1",
      "07_bodydetails.json#/bodies/0/faces/11"
     ],
     "note": "outward normal from plane normal and face orientation"
    }
   },
   "evidence": [
    "07_bodydetails.json#/bodies/0/faces/1",
    "07_bodydetails.json#/bodies/0/faces/11"
   ],
   "extraction_method": "prismatic: planes perpendicular to the tool axis grouped by height and facing side",
   "confidence": "high",
   "uncertainty": "none identified",
   "needs_human_verification": false,
   "access_direction": "+Z side (top setup)"
  },
  {
   "id": "M-LEVEL-03",
   "type": "planar_level",
   "description": "Up-facing planar face(s) at height 5 mm (2 face(s), 1335.18 mm2)",
   "label": "CAD_EXTRACTED",
   "dimensions": {
    "total_area": {
     "value": 1335.176,
     "unit": "mm2",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/4",
      "07_bodydetails.json#/bodies/0/faces/9"
     ]
    }
   },
   "location": {
    "height": {
     "value": 5.0,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/4",
      "07_bodydetails.json#/bodies/0/faces/9"
     ],
     "note": "coordinate along +Z"
    },
    "facing": {
     "value": "+Z",
     "unit": null,
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/4",
      "07_bodydetails.json#/bodies/0/faces/9"
     ],
     "note": "outward normal from plane normal and face orientation"
    }
   },
   "evidence": [
    "07_bodydetails.json#/bodies/0/faces/4",
    "07_bodydetails.json#/bodies/0/faces/9"
   ],
   "extraction_method": "prismatic: planes perpendicular to the tool axis grouped by height and facing side",
   "confidence": "high",
   "uncertainty": "none identified",
   "needs_human_verification": false,
   "access_direction": "+Z side (top setup)"
  },
  {
   "id": "M-LEVEL-04",
   "type": "planar_level",
   "description": "Down-facing planar face(s) at height -5 mm (2 face(s), 1335.18 mm2)",
   "label": "CAD_EXTRACTED",
   "dimensions": {
    "total_area": {
     "value": 1335.176,
     "unit": "mm2",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/3",
      "07_bodydetails.json#/bodies/0/faces/8"
     ]
    }
   },
   "location": {
    "height": {
     "value": -5.0,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/3",
      "07_bodydetails.json#/bodies/0/faces/8"
     ],
     "note": "coordinate along +Z"
    },
    "facing": {
     "value": "-Z",
     "unit": null,
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/3",
      "07_bodydetails.json#/bodies/0/faces/8"
     ],
     "note": "outward normal from plane normal and face orientation"
    }
   },
   "evidence": [
    "07_bodydetails.json#/bodies/0/faces/3",
    "07_bodydetails.json#/bodies/0/faces/8"
   ],
   "extraction_method": "prismatic: planes perpendicular to the tool axis grouped by height and facing side",
   "confidence": "high",
   "uncertainty": "none identified",
   "needs_human_verification": false,
   "access_direction": "-Z side (opposite setup)"
  },
  {
   "id": "M-LEVEL-05",
   "type": "planar_level",
   "description": "Down-facing planar face(s) at height -10 mm (2 face(s), 3166.42 mm2)",
   "label": "CAD_EXTRACTED",
   "dimensions": {
    "total_area": {
     "value": 3166.42,
     "unit": "mm2",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/2",
      "07_bodydetails.json#/bodies/0/faces/10"
     ]
    }
   },
   "location": {
    "height": {
     "value": -10.0,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/2",
      "07_bodydetails.json#/bodies/0/faces/10"
     ],
     "note": "coordinate along +Z"
    },
    "facing": {
     "value": "-Z",
     "unit": null,
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/2",
      "07_bodydetails.json#/bodies/0/faces/10"
     ],
     "note": "outward normal from plane normal and face orientation"
    }
   },
   "evidence": [
    "07_bodydetails.json#/bodies/0/faces/2",
    "07_bodydetails.json#/bodies/0/faces/10"
   ],
   "extraction_method": "prismatic: planes perpendicular to the tool axis grouped by height and facing side",
   "confidence": "high",
   "uncertainty": "none identified",
   "needs_human_verification": false,
   "access_direction": "-Z side (opposite setup)"
  },
  {
   "id": "M-CONTOUR-01",
   "type": "outer_contour",
   "description": "Outer profile between heights -5 and 5 mm: convex R30, concave R60, convex R21, convex R115",
   "label": "GEOMETRICALLY_INFERRED",
   "dimensions": {
    "min_concave_radius": {
     "value": 60.0,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/5",
      "07_bodydetails.json#/bodies/0/faces/7",
      "07_bodydetails.json#/bodies/0/faces/12",
      "07_bodydetails.json#/bodies/0/faces/6"
     ]
    }
   },
   "location": {
    "height_span": {
     "value": [
      -5.0,
      5.0
     ],
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/5",
      "07_bodydetails.json#/bodies/0/faces/7",
      "07_bodydetails.json#/bodies/0/faces/12",
      "07_bodydetails.json#/bodies/0/faces/6"
     ],
     "note": "band(s) where this section loop exists: [[-5.0, 5.0]]"
    },
    "extent": {
     "value": {
      "min": [
       -29.9856,
       -29.9868
      ],
      "max": [
       125.9993,
       42.7376
      ],
      "axes": [
       "X",
       "Y"
      ]
     },
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/5",
      "07_bodydetails.json#/bodies/0/faces/7",
      "07_bodydetails.json#/bodies/0/faces/12",
      "07_bodydetails.json#/bodies/0/faces/6"
     ]
    }
   },
   "evidence": [
    "07_bodydetails.json#/bodies/0/faces/5",
    "07_bodydetails.json#/bodies/0/faces/7",
    "07_bodydetails.json#/bodies/0/faces/12",
    "07_bodydetails.json#/bodies/0/faces/6"
   ],
   "extraction_method": "prismatic: section loop at band mid-height, containment depth 0 (material)",
   "confidence": "high",
   "uncertainty": "none identified",
   "needs_human_verification": false,
   "geometry_elements": [
    {
     "kind": "arc",
     "radius_mm": 30.0,
     "diameter_mm": 60.0,
     "centre_mm": [
      0.0,
      0.0
     ],
     "convex": true,
     "sweep_deg": 189.834,
     "start_mm": [
      -15.8218,
      25.4886
     ],
     "end_mm": [
      19.9429,
      -22.4117
     ],
     "direction_in_loop": "CCW (viewed from the +axis side)",
     "face_id": "Jaq",
     "pointer": "07_bodydetails.json#/bodies/0/faces/5"
    },
    {
     "kind": "arc",
     "radius_mm": 60.0,
     "diameter_mm": 120.0,
     "centre_mm": [
      59.8286,
      -67.235
     ],
     "convex": false,
     "sweep_deg": 75.559,
     "start_mm": [
      19.9429,
      -22.4117
     ],
     "end_mm": [
      93.2889,
      -17.4313
     ],
     "direction_in_loop": "CW (viewed from the +axis side)",
     "face_id": "Jam",
     "pointer": "07_bodydetails.json#/bodies/0/faces/7"
    },
    {
     "kind": "arc",
     "radius_mm": 21.0,
     "diameter_mm": 42.0,
     "centre_mm": [
      105.0,
      0.0
     ],
     "convex": true,
     "sweep_deg": 174.094,
     "start_mm": [
      93.2889,
      -17.4313
     ],
     "end_mm": [
      118.4426,
      16.1337
     ],
     "direction_in_loop": "CCW (viewed from the +axis side)",
     "face_id": "Jau",
     "pointer": "07_bodydetails.json#/bodies/0/faces/12"
    },
    {
     "kind": "arc",
     "radius_mm": 115.0,
     "diameter_mm": 230.0,
     "centre_mm": [
      44.8286,
      -72.2177
     ],
     "convex": true,
     "sweep_deg": 71.63,
     "start_mm": [
      118.4426,
      16.1338
     ],
     "end_mm": [
      -15.8218,
      25.4886
     ],
     "direction_in_loop": "CCW (viewed from the +axis side)",
     "face_id": "Jai",
     "pointer": "07_bodydetails.json#/bodies/0/faces/6"
    }
   ],
   "access_direction": "side walls parallel to the tool axis (contouring)"
  },
  {
   "id": "M-BOSS-01",
   "type": "cylindrical_boss",
   "description": "Cylindrical boss Ø60 centred at [0.0, 0.0], height -10..10 mm (free-standing above/below the arm, merged with the arm profile in between)",
   "label": "GEOMETRICALLY_INFERRED",
   "dimensions": {
    "diameter": {
     "value": 60.0,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/5"
     ]
    },
    "height": {
     "value": 20.0,
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/5"
     ]
    }
   },
   "location": {
    "centre": {
     "value": [
      0.0,
      0.0
     ],
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/5"
     ]
    },
    "height_span": {
     "value": [
      -10.0,
      10.0
     ],
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/5"
     ],
     "note": "union of the bands where this face bounds material"
    }
   },
   "evidence": [
    "07_bodydetails.json#/bodies/0/faces/5"
   ],
   "extraction_method": "prismatic: convex full-circle section loop + same face in the outer contour",
   "confidence": "high",
   "uncertainty": "none identified",
   "needs_human_verification": false
  },
  {
   "id": "M-BOSS-02",
   "type": "cylindrical_boss",
   "description": "Cylindrical boss Ø42 centred at [105.0, 0.0], height -10..10 mm (free-standing above/below the arm, merged with the arm profile in between)",
   "label": "GEOMETRICALLY_INFERRED",
   "dimensions": {
    "diameter": {
     "value": 42.0,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/12"
     ]
    },
    "height": {
     "value": 20.0,
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/12"
     ]
    }
   },
   "location": {
    "centre": {
     "value": [
      105.0,
      0.0
     ],
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/12"
     ]
    },
    "height_span": {
     "value": [
      -10.0,
      10.0
     ],
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/12"
     ],
     "note": "union of the bands where this face bounds material"
    }
   },
   "evidence": [
    "07_bodydetails.json#/bodies/0/faces/12"
   ],
   "extraction_method": "prismatic: convex full-circle section loop + same face in the outer contour",
   "confidence": "high",
   "uncertainty": "none identified",
   "needs_human_verification": false
  },
  {
   "id": "M-BORE-01",
   "type": "bore",
   "description": "Bore Ø30 at [0.0, 0.0], height -10..10 mm, open at both ends (through), interrupted by a slot (329.068 deg of circle remain)",
   "label": "GEOMETRICALLY_INFERRED",
   "dimensions": {
    "diameter": {
     "value": 30.0,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/0"
     ]
    },
    "depth": {
     "value": 20.0,
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/0",
      "07_bodydetails.json#/bodies/0/faces/33",
      "07_bodydetails.json#/bodies/0/faces/34",
      "07_bodydetails.json#/bodies/0/faces/32"
     ]
    }
   },
   "location": {
    "centre": {
     "value": [
      0.0,
      0.0
     ],
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/0"
     ]
    },
    "height_span": {
     "value": [
      -10.0,
      10.0
     ],
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/0",
      "07_bodydetails.json#/bodies/0/faces/33",
      "07_bodydetails.json#/bodies/0/faces/34",
      "07_bodydetails.json#/bodies/0/faces/32"
     ],
     "note": "band(s) where this section loop exists: [[-10.0, -5.0], [-5.0, 5.0], [5.0, 10.0]]"
    },
    "through": {
     "value": true,
     "unit": null,
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/0",
      "07_bodydetails.json#/bodies/0/faces/33",
      "07_bodydetails.json#/bodies/0/faces/34",
      "07_bodydetails.json#/bodies/0/faces/32"
     ],
     "note": "no floor/closed-top level face inside the loop"
    }
   },
   "evidence": [
    "07_bodydetails.json#/bodies/0/faces/0",
    "07_bodydetails.json#/bodies/0/faces/33",
    "07_bodydetails.json#/bodies/0/faces/34",
    "07_bodydetails.json#/bodies/0/faces/32"
   ],
   "extraction_method": "prismatic: void section loop with a >=300 deg concave arc plus planar walls",
   "confidence": "high",
   "uncertainty": "none identified",
   "needs_human_verification": false,
   "geometry_elements": [
    {
     "kind": "arc",
     "radius_mm": 15.0,
     "diameter_mm": 30.0,
     "centre_mm": [
      0.0,
      0.0
     ],
     "convex": false,
     "sweep_deg": 329.068,
     "start_mm": [
      -4.0,
      14.4568
     ],
     "end_mm": [
      4.0,
      14.4568
     ],
     "direction_in_loop": "CCW (viewed from the +axis side)",
     "face_id": "JZS",
     "pointer": "07_bodydetails.json#/bodies/0/faces/0"
    },
    {
     "kind": "line",
     "start_mm": [
      4.0,
      14.4568
     ],
     "end_mm": [
      4.0,
      18.0
     ],
     "length_mm": 3.5432,
     "face_id": "JZK",
     "pointer": "07_bodydetails.json#/bodies/0/faces/33"
    },
    {
     "kind": "line",
     "start_mm": [
      4.0,
      18.0
     ],
     "end_mm": [
      -4.0,
      18.0
     ],
     "length_mm": 8.0,
     "face_id": "JZG",
     "pointer": "07_bodydetails.json#/bodies/0/faces/34"
    },
    {
     "kind": "line",
     "start_mm": [
      -4.0,
      18.0
     ],
     "end_mm": [
      -4.0,
      14.4568
     ],
     "length_mm": 3.5432,
     "face_id": "JZC",
     "pointer": "07_bodydetails.json#/bodies/0/faces/32"
    }
   ],
   "related_features": [
    "M-KEYWAY-01"
   ]
  },
  {
   "id": "M-KEYWAY-01",
   "type": "keyway_slot",
   "description": "Keyway/slot in bore M-BORE-01: width 8.0 mm, closed end 18.0 mm from the bore axis",
   "label": "GEOMETRICALLY_INFERRED",
   "dimensions": {
    "width": {
     "value": 8.0,
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/33",
      "07_bodydetails.json#/bodies/0/faces/34",
      "07_bodydetails.json#/bodies/0/faces/32"
     ],
     "note": "distance between the facing walls JZK and JZC"
    },
    "end_wall_distance_from_bore_axis": {
     "value": 18.0,
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/33",
      "07_bodydetails.json#/bodies/0/faces/34",
      "07_bodydetails.json#/bodies/0/faces/32"
     ]
    },
    "depth_beyond_bore_surface": {
     "value": 3.0,
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/33",
      "07_bodydetails.json#/bodies/0/faces/34",
      "07_bodydetails.json#/bodies/0/faces/32"
     ]
    }
   },
   "location": {
    "direction_from_bore_axis": {
     "value": [
      0.0,
      1.0
     ],
     "unit": null,
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/33",
      "07_bodydetails.json#/bodies/0/faces/34",
      "07_bodydetails.json#/bodies/0/faces/32"
     ]
    },
    "height_span": {
     "value": [
      -10.0,
      10.0
     ],
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/0",
      "07_bodydetails.json#/bodies/0/faces/33",
      "07_bodydetails.json#/bodies/0/faces/34",
      "07_bodydetails.json#/bodies/0/faces/32"
     ],
     "note": "band(s) where this section loop exists: [[-10.0, -5.0], [-5.0, 5.0], [5.0, 10.0]]"
    }
   },
   "evidence": [
    "07_bodydetails.json#/bodies/0/faces/33",
    "07_bodydetails.json#/bodies/0/faces/34",
    "07_bodydetails.json#/bodies/0/faces/32"
   ],
   "extraction_method": "prismatic: anti-parallel facing walls (width) + perpendicular end wall",
   "confidence": "high",
   "uncertainty": "none identified",
   "needs_human_verification": false,
   "related_features": [
    "M-BORE-01"
   ]
  },
  {
   "id": "M-HOLE-01",
   "type": "hole",
   "description": "Cylindrical hole Ø20 at [105.0, 0.0], height -10..10 mm, through",
   "label": "GEOMETRICALLY_INFERRED",
   "dimensions": {
    "diameter": {
     "value": 20.0,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/13"
     ]
    },
    "depth": {
     "value": 20.0,
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/13"
     ]
    }
   },
   "location": {
    "centre": {
     "value": [
      105.0,
      0.0
     ],
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/13"
     ]
    },
    "height_span": {
     "value": [
      -10.0,
      10.0
     ],
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/13"
     ],
     "note": "band(s) where this section loop exists: [[-10.0, -5.0], [-5.0, 5.0], [5.0, 10.0]]"
    },
    "through": {
     "value": true,
     "unit": null,
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/13"
     ]
    }
   },
   "evidence": [
    "07_bodydetails.json#/bodies/0/faces/13"
   ],
   "extraction_method": "prismatic: concave full-circle void loop",
   "confidence": "high",
   "uncertainty": "none identified",
   "needs_human_verification": false
  },
  {
   "id": "M-WINDOW-01",
   "type": "through_window",
   "description": "Through window (internal opening) between heights -5 and 5 mm bounded by convex R30, concave R8, concave R107, concave R8, convex R21, concave R8, convex R68, concave R8",
   "label": "GEOMETRICALLY_INFERRED",
   "dimensions": {
    "min_concave_radius": {
     "value": 8.0,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/5",
      "07_bodydetails.json#/bodies/0/faces/15",
      "07_bodydetails.json#/bodies/0/faces/14",
      "07_bodydetails.json#/bodies/0/faces/19",
      "07_bodydetails.json#/bodies/0/faces/12",
      "07_bodydetails.json#/bodies/0/faces/18",
      "07_bodydetails.json#/bodies/0/faces/17",
      "07_bodydetails.json#/bodies/0/faces/16"
     ],
     "note": "smallest concave corner radius in the loop"
    },
    "depth": {
     "value": 10.0,
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/5",
      "07_bodydetails.json#/bodies/0/faces/15",
      "07_bodydetails.json#/bodies/0/faces/14",
      "07_bodydetails.json#/bodies/0/faces/19",
      "07_bodydetails.json#/bodies/0/faces/12",
      "07_bodydetails.json#/bodies/0/faces/18",
      "07_bodydetails.json#/bodies/0/faces/17",
      "07_bodydetails.json#/bodies/0/faces/16"
     ]
    }
   },
   "location": {
    "height_span": {
     "value": [
      -5.0,
      5.0
     ],
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/5",
      "07_bodydetails.json#/bodies/0/faces/15",
      "07_bodydetails.json#/bodies/0/faces/14",
      "07_bodydetails.json#/bodies/0/faces/19",
      "07_bodydetails.json#/bodies/0/faces/12",
      "07_bodydetails.json#/bodies/0/faces/18",
      "07_bodydetails.json#/bodies/0/faces/17",
      "07_bodydetails.json#/bodies/0/faces/16"
     ],
     "note": "band(s) where this section loop exists: [[-5.0, 5.0]]"
    },
    "extent": {
     "value": {
      "min": [
       20.2796,
       -2.5501
      ],
      "max": [
       91.1444,
       34.7801
      ],
      "axes": [
       "X",
       "Y"
      ]
     },
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/5",
      "07_bodydetails.json#/bodies/0/faces/15",
      "07_bodydetails.json#/bodies/0/faces/14",
      "07_bodydetails.json#/bodies/0/faces/19",
      "07_bodydetails.json#/bodies/0/faces/12",
      "07_bodydetails.json#/bodies/0/faces/18",
      "07_bodydetails.json#/bodies/0/faces/17",
      "07_bodydetails.json#/bodies/0/faces/16"
     ]
    },
    "floor_at": {
     "value": "none (open)",
     "unit": null,
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/5",
      "07_bodydetails.json#/bodies/0/faces/15",
      "07_bodydetails.json#/bodies/0/faces/14",
      "07_bodydetails.json#/bodies/0/faces/19",
      "07_bodydetails.json#/bodies/0/faces/12",
      "07_bodydetails.json#/bodies/0/faces/18",
      "07_bodydetails.json#/bodies/0/faces/17",
      "07_bodydetails.json#/bodies/0/faces/16"
     ]
    },
    "interior_point": {
     "value": [
      27.2622,
      12.7586
     ],
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/5",
      "07_bodydetails.json#/bodies/0/faces/15",
      "07_bodydetails.json#/bodies/0/faces/14",
      "07_bodydetails.json#/bodies/0/faces/19",
      "07_bodydetails.json#/bodies/0/faces/12",
      "07_bodydetails.json#/bodies/0/faces/18",
      "07_bodydetails.json#/bodies/0/faces/17",
      "07_bodydetails.json#/bodies/0/faces/16"
     ],
     "note": "a point inside the opening, useful for plunge/entry planning"
    }
   },
   "evidence": [
    "07_bodydetails.json#/bodies/0/faces/5",
    "07_bodydetails.json#/bodies/0/faces/15",
    "07_bodydetails.json#/bodies/0/faces/14",
    "07_bodydetails.json#/bodies/0/faces/19",
    "07_bodydetails.json#/bodies/0/faces/12",
    "07_bodydetails.json#/bodies/0/faces/18",
    "07_bodydetails.json#/bodies/0/faces/17",
    "07_bodydetails.json#/bodies/0/faces/16"
   ],
   "extraction_method": "prismatic: void section loop without a near-full circle; floor/closed-top tested against level faces",
   "confidence": "high",
   "uncertainty": "none identified",
   "needs_human_verification": false,
   "geometry_elements": [
    {
     "kind": "arc",
     "radius_mm": 30.0,
     "diameter_mm": 60.0,
     "centre_mm": [
      0.0,
      0.0
     ],
     "convex": true,
     "sweep_deg": 33.685,
     "start_mm": [
      29.6905,
      4.298
     ],
     "end_mm": [
      22.3217,
      20.0435
     ],
     "direction_in_loop": "CCW (viewed from the +axis side)",
     "face_id": "Jaq",
     "pointer": "07_bodydetails.json#/bodies/0/faces/5"
    },
    {
     "kind": "arc",
     "radius_mm": 8.0,
     "diameter_mm": 16.0,
     "centre_mm": [
      28.2742,
      25.3884
     ],
     "convex": false,
     "sweep_deg": 122.296,
     "start_mm": [
      22.3217,
      20.0435
     ],
     "end_mm": [
      26.9365,
      33.2758
     ],
     "direction_in_loop": "CW (viewed from the +axis side)",
     "face_id": "Jay",
     "pointer": "07_bodydetails.json#/bodies/0/faces/15"
    },
    {
     "kind": "arc",
     "radius_mm": 107.0,
     "diameter_mm": 214.0,
     "centre_mm": [
      44.8286,
      -72.2177
     ],
     "convex": false,
     "sweep_deg": 32.398,
     "start_mm": [
      26.9365,
      33.2758
     ],
     "end_mm": [
      86.2446,
      26.4419
     ],
     "direction_in_loop": "CW (viewed from the +axis side)",
     "face_id": "JRK",
     "pointer": "07_bodydetails.json#/bodies/0/faces/14"
    },
    {
     "kind": "arc",
     "radius_mm": 8.0,
     "diameter_mm": 16.0,
     "centre_mm": [
      83.148,
      19.0655
     ],
     "convex": false,
     "sweep_deg": 108.332,
     "start_mm": [
      86.2445,
      26.4419
     ],
     "end_mm": [
      89.1761,
      13.8061
     ],
     "direction_in_loop": "CW (viewed from the +axis side)",
     "face_id": "Ja2",
     "pointer": "07_bodydetails.json#/bodies/0/faces/19"
    },
    {
     "kind": "arc",
     "radius_mm": 21.0,
     "diameter_mm": 42.0,
     "centre_mm": [
      105.0,
      0.0
     ],
     "convex": true,
     "sweep_deg": 27.458,
     "start_mm": [
      89.1762,
      13.806
     ],
     "end_mm": [
      84.5928,
      4.9543
     ],
     "direction_in_loop": "CCW (viewed from the +axis side)",
     "face_id": "Jau",
     "pointer": "07_bodydetails.json#/bodies/0/faces/12"
    },
    {
     "kind": "arc",
     "radius_mm": 8.0,
     "diameter_mm": 16.0,
     "centre_mm": [
      76.8186,
      6.8416
     ],
     "convex": false,
     "sweep_deg": 89.272,
     "start_mm": [
      84.5928,
      4.9543
     ],
     "end_mm": [
      75.0302,
      -0.9559
     ],
     "direction_in_loop": "CW (viewed from the +axis side)",
     "face_id": "Ja6",
     "pointer": "07_bodydetails.json#/bodies/0/faces/18"
    },
    {
     "kind": "arc",
     "radius_mm": 68.0,
     "diameter_mm": 136.0,
     "centre_mm": [
      59.8286,
      -67.235
     ],
     "convex": true,
     "sweep_deg": 29.918,
     "start_mm": [
      75.0302,
      -0.956
     ],
     "end_mm": [
      39.947,
      -2.2064
     ],
     "direction_in_loop": "CCW (viewed from the +axis side)",
     "face_id": "JRO",
     "pointer": "07_bodydetails.json#/bodies/0/faces/17"
    },
    {
     "kind": "arc",
     "radius_mm": 8.0,
     "diameter_mm": 16.0,
     "centre_mm": [
      37.608,
      5.4441
     ],
     "convex": false,
     "sweep_deg": 98.763,
     "start_mm": [
      39.947,
      -2.2063
     ],
     "end_mm": [
      29.6905,
      4.298
     ],
     "direction_in_loop": "CW (viewed from the +axis side)",
     "face_id": "Ja+",
     "pointer": "07_bodydetails.json#/bodies/0/faces/16"
    }
   ]
  },
  {
   "id": "M-PINS-01",
   "type": "pin_pattern",
   "description": "6 x Ø3.5 pins (raised cylinders) on PCD 46 around [0.0, 0.0], height 10..14 mm",
   "label": "GEOMETRICALLY_INFERRED",
   "dimensions": {
    "diameter": {
     "value": 3.5,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/22",
      "07_bodydetails.json#/bodies/0/faces/20",
      "07_bodydetails.json#/bodies/0/faces/24",
      "07_bodydetails.json#/bodies/0/faces/30",
      "07_bodydetails.json#/bodies/0/faces/26",
      "07_bodydetails.json#/bodies/0/faces/28"
     ]
    },
    "count": {
     "value": 6,
     "unit": null,
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/22",
      "07_bodydetails.json#/bodies/0/faces/20",
      "07_bodydetails.json#/bodies/0/faces/24",
      "07_bodydetails.json#/bodies/0/faces/30",
      "07_bodydetails.json#/bodies/0/faces/26",
      "07_bodydetails.json#/bodies/0/faces/28"
     ]
    },
    "pitch_circle_diameter": {
     "value": 46.0,
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/22",
      "07_bodydetails.json#/bodies/0/faces/20",
      "07_bodydetails.json#/bodies/0/faces/24",
      "07_bodydetails.json#/bodies/0/faces/30",
      "07_bodydetails.json#/bodies/0/faces/26",
      "07_bodydetails.json#/bodies/0/faces/28"
     ]
    },
    "height": {
     "value": 4.0,
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/22",
      "07_bodydetails.json#/bodies/0/faces/20",
      "07_bodydetails.json#/bodies/0/faces/24",
      "07_bodydetails.json#/bodies/0/faces/30",
      "07_bodydetails.json#/bodies/0/faces/26",
      "07_bodydetails.json#/bodies/0/faces/28"
     ]
    }
   },
   "location": {
    "pattern_centre": {
     "value": [
      0.0,
      0.0
     ],
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/22",
      "07_bodydetails.json#/bodies/0/faces/20",
      "07_bodydetails.json#/bodies/0/faces/24",
      "07_bodydetails.json#/bodies/0/faces/30",
      "07_bodydetails.json#/bodies/0/faces/26",
      "07_bodydetails.json#/bodies/0/faces/28"
     ]
    },
    "angular_positions": {
     "value": [
      30.0,
      90.0,
      150.0,
      210.0,
      270.0,
      330.0
     ],
     "unit": "deg",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/22",
      "07_bodydetails.json#/bodies/0/faces/20",
      "07_bodydetails.json#/bodies/0/faces/24",
      "07_bodydetails.json#/bodies/0/faces/30",
      "07_bodydetails.json#/bodies/0/faces/26",
      "07_bodydetails.json#/bodies/0/faces/28"
     ],
     "note": "CCW from +X viewed from +Z"
    },
    "centres": {
     "value": [
      [
       -19.9186,
       -11.5
      ],
      [
       -19.9186,
       11.5
      ],
      [
       0.0,
       -23.0
      ],
      [
       0.0,
       23.0
      ],
      [
       19.9186,
       -11.5
      ],
      [
       19.9186,
       11.5
      ]
     ],
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/22",
      "07_bodydetails.json#/bodies/0/faces/20",
      "07_bodydetails.json#/bodies/0/faces/24",
      "07_bodydetails.json#/bodies/0/faces/30",
      "07_bodydetails.json#/bodies/0/faces/26",
      "07_bodydetails.json#/bodies/0/faces/28"
     ]
    },
    "height_span": {
     "value": [
      10.0,
      14.0
     ],
     "unit": "mm",
     "label": "GEOMETRICALLY_INFERRED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/22",
      "07_bodydetails.json#/bodies/0/faces/20",
      "07_bodydetails.json#/bodies/0/faces/24",
      "07_bodydetails.json#/bodies/0/faces/30",
      "07_bodydetails.json#/bodies/0/faces/26",
      "07_bodydetails.json#/bodies/0/faces/28"
     ]
    }
   },
   "evidence": [
    "07_bodydetails.json#/bodies/0/faces/22",
    "07_bodydetails.json#/bodies/0/faces/20",
    "07_bodydetails.json#/bodies/0/faces/24",
    "07_bodydetails.json#/bodies/0/faces/30",
    "07_bodydetails.json#/bodies/0/faces/26",
    "07_bodydetails.json#/bodies/0/faces/28"
   ],
   "extraction_method": "prismatic: equal full-circle loops equidistant from a bore/boss centre",
   "confidence": "high",
   "uncertainty": "none identified",
   "needs_human_verification": false,
   "access_direction": "+Z side (top setup)"
  },
  {
   "id": "M-FILLET-01",
   "type": "edge_fillet",
   "description": "8 concave R2 fillet faces (tori) around [0.0, 0.0] at height -7; [0.0, 0.0] at height 7; [105.0, 0.0] at height -7; [105.0, 0.0] at height 7",
   "label": "CAD_EXTRACTED",
   "dimensions": {
    "radius": {
     "value": 2.0,
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/36",
      "07_bodydetails.json#/bodies/0/faces/41",
      "07_bodydetails.json#/bodies/0/faces/38",
      "07_bodydetails.json#/bodies/0/faces/42",
      "07_bodydetails.json#/bodies/0/faces/35",
      "07_bodydetails.json#/bodies/0/faces/39",
      "07_bodydetails.json#/bodies/0/faces/37",
      "07_bodydetails.json#/bodies/0/faces/40"
     ],
     "note": "torus minor radius"
    }
   },
   "location": {
    "instances": {
     "value": [
      {
       "axis_centre_mm": [
        0.0,
        0.0
       ],
       "sweep_circle_radius_mm": 32.0,
       "height_mm": -7.0
      },
      {
       "axis_centre_mm": [
        0.0,
        0.0
       ],
       "sweep_circle_radius_mm": 32.0,
       "height_mm": 7.0
      },
      {
       "axis_centre_mm": [
        105.0,
        0.0
       ],
       "sweep_circle_radius_mm": 23.0,
       "height_mm": -7.0
      },
      {
       "axis_centre_mm": [
        105.0,
        0.0
       ],
       "sweep_circle_radius_mm": 23.0,
       "height_mm": 7.0
      }
     ],
     "unit": "mm",
     "label": "CAD_EXTRACTED",
     "evidence": [
      "07_bodydetails.json#/bodies/0/faces/36",
      "07_bodydetails.json#/bodies/0/faces/41",
      "07_bodydetails.json#/bodies/0/faces/38",
      "07_bodydetails.json#/bodies/0/faces/42",
      "07_bodydetails.json#/bodies/0/faces/35",
      "07_bodydetails.json#/bodies/0/faces/39",
      "07_bodydetails.json#/bodies/0/faces/37",
      "07_bodydetails.json#/bodies/0/faces/40"
     ]
    }
   },
   "evidence": [
    "07_bodydetails.json#/bodies/0/faces/36",
    "07_bodydetails.json#/bodies/0/faces/41",
    "07_bodydetails.json#/bodies/0/faces/38",
    "07_bodydetails.json#/bodies/0/faces/42",
    "07_bodydetails.json#/bodies/0/faces/35",
    "07_bodydetails.json#/bodies/0/faces/39",
    "07_bodydetails.json#/bodies/0/faces/37",
    "07_bodydetails.json#/bodies/0/faces/40"
   ],
   "extraction_method": "prismatic: torus faces with axis parallel to the tool axis",
   "confidence": "high",
   "uncertainty": "none identified",
   "needs_human_verification": false,
   "access_direction": "both sides (fillets at positive and negative heights)"
  }
 ],
 "relationships": [
  {
   "id": "M-REL-01",
   "description": "Centre distance between the two bosses / bores",
   "value": 105.0,
   "unit": "mm",
   "label": "GEOMETRICALLY_INFERRED",
   "method": "computed from the listed features' CAD values",
   "evidence": [
    "features M-BOSS-01, M-BOSS-02"
   ],
   "features": [
    "M-BOSS-01",
    "M-BOSS-02"
   ]
  },
  {
   "id": "M-REL-02",
   "description": "M-CONTOUR-01 (profile band) thickness",
   "value": 10.0,
   "unit": "mm",
   "label": "GEOMETRICALLY_INFERRED",
   "method": "computed from the listed features' CAD values",
   "evidence": [
    "features M-CONTOUR-01"
   ],
   "features": [
    "M-CONTOUR-01"
   ]
  },
  {
   "id": "M-REL-03",
   "description": "M-BOSS-01 thickness",
   "value": 20.0,
   "unit": "mm",
   "label": "GEOMETRICALLY_INFERRED",
   "method": "computed from the listed features' CAD values",
   "evidence": [
    "features M-BOSS-01"
   ],
   "features": [
    "M-BOSS-01"
   ]
  },
  {
   "id": "M-REL-04",
   "description": "M-BOSS-02 thickness",
   "value": 20.0,
   "unit": "mm",
   "label": "GEOMETRICALLY_INFERRED",
   "method": "computed from the listed features' CAD values",
   "evidence": [
    "features M-BOSS-02"
   ],
   "features": [
    "M-BOSS-02"
   ]
  },
  {
   "id": "M-REL-05",
   "description": "Radial wall thickness between concentric walls R30 and R15 about [0.0, 0.0]",
   "value": 15.0,
   "unit": "mm",
   "label": "GEOMETRICALLY_INFERRED",
   "method": "computed from the listed features' CAD values",
   "evidence": [
    "features M-CONTOUR-01, M-BORE-01"
   ],
   "features": [
    "M-CONTOUR-01",
    "M-BORE-01"
   ]
  },
  {
   "id": "M-REL-06",
   "description": "Radial wall thickness between concentric walls R68 and R60 about [59.8286, -67.235]",
   "value": 8.0,
   "unit": "mm",
   "label": "GEOMETRICALLY_INFERRED",
   "method": "computed from the listed features' CAD values",
   "evidence": [
    "features M-CONTOUR-01, M-WINDOW-01"
   ],
   "features": [
    "M-CONTOUR-01",
    "M-WINDOW-01"
   ]
  },
  {
   "id": "M-REL-07",
   "description": "Radial wall thickness between concentric walls R115 and R107 about [44.8286, -72.2177]",
   "value": 8.0,
   "unit": "mm",
   "label": "GEOMETRICALLY_INFERRED",
   "method": "computed from the listed features' CAD values",
   "evidence": [
    "features M-CONTOUR-01, M-WINDOW-01"
   ],
   "features": [
    "M-CONTOUR-01",
    "M-WINDOW-01"
   ]
  }
 ],
 "human_annotations": [],
 "missing_data": [
  {
   "item": "material",
   "label": "UNKNOWN",
   "reason": "no material assigned in Onshape",
   "needed_for": "cutting data (G2), MillLab material"
  },
  {
   "item": "raw stock block size and allowances",
   "label": "UNKNOWN",
   "reason": "process decision (Part B route sheet), not CAD",
   "needed_for": "MillLab workpiece, facing passes"
  },
  {
   "item": "tolerances, fits (Ø30/Ø20 bores, keyway, pins), surface finish",
   "label": "UNKNOWN",
   "reason": "not in the B-rep; drawing annotations are not returned by the API",
   "needed_for": "finishing / boring strategy, inspection"
  },
  {
   "item": "edge breaks / chamfers other than the modelled R2 fillets",
   "label": "UNKNOWN",
   "reason": "not modelled; title-block notes are not available through the API",
   "needed_for": "deburring passes"
  }
 ],
 "limitations": [
  "Only tool axes parallel to a world axis are analysed (true for the current model); an inclined axis is reported as an error, not guessed.",
  "Feature types (hole, bore with slot, window, pin, boss) are inferred from topology and geometry; the B-rep carries no manufacturing semantics (no tolerances, fits, surface finish, material, thread callouts). Those stay UNKNOWN unless a human annotation supplies them.",
  "Face 'orientation' is an undocumented Onshape field; its meaning is an observed convention.",
  "Curved edges are represented by their start, quarter, mid and end points when mapped to a face's parameter space; sections are exact for vertical side edges and approximate (piecewise linear) where a side edge is a blend curve. Slices are taken at band mid-heights, away from the R2 blends.",
  "Blends (tori) are reported separately as fillets and are not part of the section loops.",
  "Contour elements are CAD geometry, not toolpaths: entry points, direction, step-downs and cutter compensation are process decisions for the AI proposal and the human gates."
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
