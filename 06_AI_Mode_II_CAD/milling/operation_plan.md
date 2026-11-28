# Operation plan - Mode II - APSD-MILLING

Source: initial AI attempt `20261128T151802Z_modeII_milling` (UNVERIFIED). G2 process-gate decisions go in 07_Comparison_Validation/human_review_records/.

| Setup | Op | Name | Tool | Strategy | Features | Simulator supported | NC file |
|---|---|---|---|---|---|---|---|
| S1 | OP10 | Boss2 top face | T02 | facing (centre plunge + 2 circles) | F02, F08 | True | op_10_boss2_top.nc |
| S1 | OP20 | Boss walls and arm-top rings | T02 | contouring | F07, F08, F03 | True | op_20_boss_walls_rings.nc |
| S1 | OP30 | Window pocket | T02 | roughing+finishing (3 rows + offset loop, climb) | F12 | True | op_30_window.nc |
| S1 | OP40 | Outer contour channel | T02 | contouring (climb, tool-centre path) | F06, F07, F08 | True | op_40_outer_channel.nc |
| S1 | OP50 | Arm-top strips | T02 | roughing+finishing (centre-line arcs R111 / R64) | F03, F15 | True | op_50_arm_strips.nc |
| S1 | OP60 | Bore D30 | T02 | circular milling (centre plunge, r5, r10) | F09 | True | op_60_bore30.nc |
| S1 | OP70 | Hole D20 | T02 | circular milling (centre plunge, r5) | F11 | True | op_70_hole20.nc |
| S1 | OP80 | Boss1 top face around pins | T03 | facing + pin profiling (climb) | F02, F07, F13 | True | op_80_boss1_top_pins.nc |
| S1 | OP90 | Keyway | T03 | slotting (2 passes x=39/41) | F10 | True | op_90_keyway.nc |
| S1 | OP95 | Keyway sharp end corners | none (broach / EDM / hand file) | secondary operation | F10 | False | None |
| S1 | OP100 | R2 fillets, top side | T10 | finishing (bull-nose corner forms fillet) | F14, F03 | True | op_100_fillets_top.nc |
| S2 | OP110 | Boss walls and arm-bottom rings | T02 | contouring | F07, F08, F04 | True | op_110_boss_walls_rings_s2.nc |
| S2 | OP120 | Window pocket (bottom) | T02 | roughing+finishing | F12 | True | op_120_window_s2.nc |
| S2 | OP130 | Arm-bottom strips | T02 | roughing+finishing | F04, F15 | True | op_130_arm_strips_s2.nc |
| S2 | OP140 | Bore D30 (bottom) | T02 | circular milling | F09 | True | op_140_bore30_s2.nc |
| S2 | OP150 | Hole D20 (bottom) | T02 | circular milling | F11 | True | op_150_hole20_s2.nc |
| S2 | OP160 | Keyway (bottom) | T03 | slotting | F10 | True | op_160_keyway_s2.nc |
| S2 | OP170 | R2 fillets, bottom side | T10 | finishing | F14, F04 | True | op_170_fillets_bottom.nc |
| S2 | OP180 | Outer channel, separation | T02 | contouring (climb) | F06, F07, F08 | True | op_180_outer_channel_s2.nc |

## AI assumptions (unverified)

- Split plane between setups = arm bottom (CAD Z-5). All voids (window, channel, bore, hole, keyway) go 0.5 mm past it on both sides (S1 Z-19.5, S2 Z-5.5) for a clean break-through.
- Only T02, T03, T10 have approved cutting data; drills, tap, reamer, face mill, chamfer mill and D16 are not used. T08 excluded (open item).
- Tool-centre programming with G40; offsets computed by hand from magazine radii (T02 R5, T03 R3, T10 R6), wear 0. No G41/G42.
- T02 and T03 assumed centre-cutting (vertical plunges at the approved 60 mm/min).
- Single pass to final size; no finishing allowance, because no tolerances are given.
- Raw block faces are the finished pin tops and boss bottoms (allowance 0 as configured).
- Waste frame kept for clamping; the part is freed during the last S2 pass (OP180).
- No coolant programmed (not specified).
- Flat tools never go below CAD Z+/-7 within 2 mm of a boss wall in arm regions, so T10 can form the R2 fillets.
