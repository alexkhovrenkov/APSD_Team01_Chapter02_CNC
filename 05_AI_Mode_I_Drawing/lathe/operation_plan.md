# Operation plan - Mode I - APSD-LATHE

Source: initial AI attempt `20261128T151802Z_modeI_lathe` (UNVERIFIED). G2 process-gate decisions go in 07_Comparison_Validation/human_review_records/.

| Setup | Op | Name | Tool | Strategy | Features | Simulator supported | NC file |
|---|---|---|---|---|---|---|---|
| S1 | OP10 | Face front end to Z0 | T01 | facing (G94 box cycle, 1 pass 1.0 mm) | F01 | True | op_10_face_front.nc |
| S1 | OP20 | Rough OD profile: D50, R5, flange right face, D100 | T01 | roughing (G71 type I) | F02, F03, F04 | True | op_20_rough_od.nc |
| S1 | OP30 | Finish OD profile | T02 | finishing contour with G42 | F02, F03, F04 | True | op_30_finish_od.nc |
| S1 | OP40 | Centre/spot drill front | T10 | drilling | F09 | True | op_40_centre_drill.nc |
| S1 | OP50 | Peck drill D13 from front to Z-65 (pilot for bore, first part of through hole) | T05 | drilling, peck 10 mm with full retract | F08, F09 | True | op_50_drill_d13.nc |
| S1 | OP60 | Rough bore D30 x 40 | T06 | roughing (G90 ID box cycle, 8 passes) | F08 | True | op_60_rough_bore.nc |
| S1 | OP70 | Finish bore D30 x 40 and bore bottom | T06 | finishing contour with G41 | F08 | True | op_70_finish_bore.nc |
| S1 | OP80 | External thread D50 x P5 (assumed metric 60 deg) | T04 | threading (G76 multi-pass + 2 spring passes) | F02 | True | op_80_thread_ext.nc |
| S2 | OP110 | Face rear end to Z0 (sets length 210) | T01 | facing (G94, 1 pass on simulated stock) | F01 | True | op_110_face_rear.nc |
| S2 | OP120 | Rough OD rear: spigot D29.9, shoulder, D60, R5, flange left face | T01 | roughing (G71 type I) | F05, F06, F07 | True | op_120_rough_od_rear.nc |
| S2 | OP130 | Finish OD rear profile | T02 | finishing contour with G42 | F05, F06, F07 | True | op_130_finish_od_rear.nc |
| S2 | OP140 | Centre/spot drill rear | T10 | drilling | F09, F10 | True | op_140_centre_drill_rear.nc |
| S2 | OP150 | Peck drill D13 from rear to Z-65 (core hole for F10, second part of through hole) | T05 | drilling, peck 10 mm with full retract | F09, F10 | True | op_150_drill_d13_rear.nc |
| S2 | OP160 | Internal thread in spigot end, 41.42 deep - BLOCKED | T09 | threading (G76 internal) - not programmed | F10 | True | None |
| S2 | OP170 | Complete D13 through hole between the two drilled ends - BLOCKED | T05 | drilling - not programmed | F09 | True | None |
| S3_OFF_LATHE | OP230 | Keyway 7.98 wide on spigot D29.9 | milling (not in lathe tool table) | slot milling | F12 | False | None |
| S3_OFF_LATHE | OP240 | 6 x D3.52 holes on PCD 46 in shoulder face, depth 4.1 (assumed) | milling/drilling (not in lathe tool table) | off-axis drilling | F11 | False | None |
| S3_OFF_LATHE | OP250 | Break all sharp edges and deburr (general note) | manual | deburring | F14 | False | None |

## AI assumptions (unverified)

- All dimensions in mm (team configuration) despite the 'inches' text in the title block.
- Thread major turned to nominal D50, not undersized; thread class unknown.
- External thread is metric 60 deg right-hand, P5: depth 0.6134 x 5 = 3.067 per side, minor dia 43.87.
- Thread ends at Z-122 (3 mm short of the fillet tangent) because no relief groove is drawn; the last turn is incomplete.
- Flange right face at S1 Z-130 and D60 body 40 long are derived values (see unclear_or_missing).
- Flange OD D100 is finished completely in S1 (turned to Z-152, 2 mm past the flange left face); S2 does not touch D100.
- Bore F08 = D30 with a flat bottom at Z-40.
- D13 is used as pilot for the bore and as core hole for the internal thread; drill tip depth limited to 65 mm (5 mm margin under the 70 mm flute length).
- T06 (bar D10) can enter the D13 pilot hole for the first G90 pass at D15; minimum bore diameter of T06 is not given in the tool table.
- Whole finishing contours run at the 'profile/radius' data (500 rpm, 0.1 mm/rev) because each contour contains an R5 radius.
- Bore cutting data: 0.10 mm/rev roughing, 0.08 mm/rev finishing (inside the approved 0.08-0.10 range).
- Roughing feed 0.20 mm/rev (upper end of the approved 0.15-0.20 range).
- Drill retracts on the spindle axis use G00: a drill retracting along its own axis is not read as a retract 'along a machined face'. Team to confirm.
- S2 is simulated on a fresh raw bar with the face at Z+1, as stated by the team. The real part carries about 29 mm extra length at the rear (240 - 210 - 1) that must be removed before OP110.
- No chamfers are programmed; edges are broken manually (OP250).
- Coolant M08/M09 is programmed for C45; LatheLab may ignore it.
