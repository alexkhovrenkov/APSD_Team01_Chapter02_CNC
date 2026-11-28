# Operation plan - Mode I - APSD-MILLING

Source: initial AI attempt `20261128T151802Z_modeI_milling` (UNVERIFIED). G2 process-gate decisions go in 07_Comparison_Validation/human_review_records/.

| Setup | Op | Name | Tool | Strategy | Features | Simulator supported | NC file |
|---|---|---|---|---|---|---|---|
| S1 | OP10 | Face the whole block to Z-4 around the pin ring (boss top faces) | T02 | roughing/facing, single level, zigzag + circular passes | F12, F04 | True | op_10_face_top_to_z4.nc |
| S1 | OP20 | Mill bore D30 through | T02 | centre plunge + circular interpolation rough (D29.6), finish pass D30 at full depth | F02 | True | op_20_bore_d30.nc |
| S1 | OP30 | Mill six pins D3.5 x 4 and clear the pin ring | T03 | two climb loops per pin per level (radius 10 and 4.75 about the pin axis) | F04, F12 | True | op_30_pins_d3_5.nc |
| S1 | OP40 | Mill keyway width 8, bottom 18 from axis, through | T03 | rectangular climb loop per level, entry in the bore void | F03 | True | op_40_keyway_w8.nc |
| S1 | OP45 | Keyway corners sharp per drawing (broaching/slotting, not on this machine) | none in magazine (broach or slotting tool) | secondary operation | F03 | False | None |
| S1 | OP50 | Rough outside both bosses from Z-4 to arm top Z-9 | T02 | roughing | F01, F05, F10 | True | op_50_rough_outside_bosses_to_z9.nc |
| S1 | OP60 | Rough outside the part outline and the window from Z-9 to Z-19 (arm level) | T02 | roughing, 0.3 mm wall allowance | F07, F08, F09, F10 | True | op_60_rough_arms_window_to_z19.nc |
| S1 | OP70 | Mill bore D20 through | T02 | as OP20 (tool-centre circle R4.8 rough / R5 finish) | F06 | True | op_70_bore_d20.nc |
| S1 | OP80 | Finish boss walls (Z-4 to Z-19), arm edges and window with R8 corners | T03 | finishing contour, climb | F01, F05, F07, F08, F09 | True | op_80_finish_walls_window_r8.nc |
| S1 | OP90 | R2 fillets, arm top faces to boss walls; finish arm top face Z-9 | T10 | 2.5D contour with bull-nose corner R2 along the boss walls | F11, F10 | True | op_90_fillets_r2_top.nc |
| S2 | OP110 | Clear outside both bosses Z0 to Z-5 (arm underside), finish lower boss walls | T02 | roughing + finishing pass | F01, F05, F07, F08, F10 | True | op_110_clear_bottom_outside_bosses_to_z5.nc |
| S2 | OP120 | R2 fillets, arm bottom faces to boss walls | T10 | 2.5D contour with bull-nose corner R2 | F11 | True | op_120_fillets_r2_bottom.nc |
| S2 | OP130 | Break sharp edges, remove burrs | manual (T09 chamfer mill has no approved cutting data) | manual deburring | F13 | False | None |

## AI assumptions (unverified)

- Z0 (block top, nothing faced) = pin tops, because pin height 4 + boss height 20 = stock height 24.
- Pins are integral to the part: 6 pins equally spaced at 30 + k*60 deg on radius 23, one on +Y (keyway side).
- B-B dimension 23 = boss axis to pin centre; 18 = boss axis to keyway bottom.
- Arms are centred in the boss height (S1 Z-9 to Z-19). Used only to describe the blocked operations.
- R115 is internally tangent and R60 externally tangent to both bosses. If confirmed, the arc centres relative to the large boss axis, with d = boss centre distance, are: C115 x = (d^2 - 1611)/(2d), y = -sqrt(7225 - x^2); C60 x = (d^2 + 1539)/(2d), y = -sqrt(8100 - x^2). Window edges are R107 about C115 and R68 about C60, closed by the D60/D42 walls with R8 blends.
- No value for d is assumed. All d-dependent NC is withheld rather than guessed.
- T02 and T03 are centre-cutting, so OP20 plunges at the bore centre.
- Through features are cut to Z-24.5 (0.5 mm breakthrough). The real fixture needs relief under both bores and the keyway.
- Tool-centre programming with G40 (no G41/G42). Offsets use the approved radii T02 R5 and T03 R3.
- No coolant is programmed because coolant is not in the approved data.
- MillLab accepts full circles (G02/G03, same start and end point, I/J centre).
- Not used: T01 and T12 (no cutting data), T04-T07, T09 and T11 (no cutting data), T08 (inconsistent row).
- The individual op files assume the preceding ops of the same setup are done. For MillLab (raw block start), run setup_01_complete.nc.
