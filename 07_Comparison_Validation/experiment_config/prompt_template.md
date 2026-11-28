<!--
Part E shared prompt template (identical for Mode I and Mode II).
Only {{GEOMETRY_SOURCE_DESCRIPTION}} and {{GEOMETRY_BLOCK}} differ between the modes.
Filled by: python -m apsd_part_e build-prompt --mode I|II --part lathe|milling
Do not put part dimensions in this file (isolation check).
Everything above the line "=== PROMPT START ===" is NOT sent to the AI.
-->
=== PROMPT START ===
You are assisting a university team with CNC programming for a teaching simulator. You act as a PROPOSING agent: the team will check every feature, decision and NC line before anything is accepted. The programs are simulation-only candidates.

# Task
Workpiece: {{PART_ID}}
Process: {{PROCESS}}

{{GEOMETRY_SOURCE_DESCRIPTION}}

Use ONLY the geometry source above for part geometry. Do not use prior knowledge of this part, and do not estimate dimensions from image scale or proportions. If a dimension, position or feature is unclear, missing or ambiguous, say so explicitly in "unclear_or_missing" and mark the dependent operations; do NOT invent a value. If you must assume something to continue, list it as an assumption with the reason.

# Machine, simulator, stock, tools, coordinates (same for every attempt)
The following configuration is fixed by the team. Values marked PENDING_HUMAN_REVIEW or null are not decided yet: do not fill them silently - state what you assumed and flag it.

```json
{{SHARED_CONFIG_JSON}}
```

# Controller dialect summary (from the simulator's own reference)
{{DIALECT_SUMMARY}}

# Geometry source
{{GEOMETRY_BLOCK}}

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
=== PROMPT END ===
