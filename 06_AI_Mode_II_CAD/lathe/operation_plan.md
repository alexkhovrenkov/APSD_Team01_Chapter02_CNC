# Operation plan - Mode II - APSD-LATHE

Source: initial AI attempt `20261128T151802Z_modeII_lathe` (UNVERIFIED). G2 process-gate decisions go in 07_Comparison_Validation/human_review_records/.

| Setup | Op | Name | Tool | Strategy | Features | Simulator supported | NC file |
|---|---|---|---|---|---|---|---|
| S1 | OP10 | Face front end | T01 | facing | F02 | True | op_10_face_front.nc |
| S1 | OP20 | OD rough front profile | T01 | roughing | F04, F05, F06, F07 | True | op_20_od_rough.nc |
| S1 | OP30 | Spot drill centre | T10 | centre drilling | F15, F17 | True | op_30_spot_drill.nc |
| S1 | OP40 | Peck drill D13 to reach limit | T05 | drilling | F17, F15 | True | op_40_drill_d13.nc |
| S1 | OP50 | Bore D30 rough | T06 | roughing | F15, F16 | True | op_50_bore_d30_rough.nc |
| S1 | OP60 | Bore D30 finish incl. bottom face | T06 | finishing | F15, F16 | True | op_60_bore_d30_finish.nc |
| S1 | OP70 | OD finish front profile | T02 | finishing | F04, F05, F06, F07 | True | op_70_od_finish.nc |
| S1 | OP80 | External thread P5 RH on D50 | T04 | threading | F20 | True | op_80_thread_ext_p5.nc |
| S2 | OP110 | Face rear end and remove excess length | T01 | facing | F03 | True | op_110_face_rear.nc |
| S2 | OP120 | OD rough rear profile (spigot envelope, D60, R5, flange face) | T01 | roughing | F12, F13, F11, F10, F09, F08 | True | op_120_od_rough_rear.nc |
| S2 | OP130 | OD finish rear profile | T02 | finishing | F12, F13, F11, F10, F09, F08 | True | op_130_od_finish_rear.nc |
| S2 | OP140 | Bore D12, a=0..41.42 | none suitable in tool table | drilling/boring | F18 | False | None |
| S2 | OP150 | Internal thread P2 RH | T09 (not usable) | threading | F21 | False | None |
| S2 | OP160 | Bore D13 remainder, a=41.42..~145 | none (T05 reach 70) | drilling | F17, F19 | False | None |
| S3 | OP310 | Contour-mill spigot D29.9 around the key, incl. face a=20 inside D36.7 | mill tooling (not in lathe table) | milling | F12, F11 | False | None |
| S3 | OP320 | Mill key top (17.9 from axis) and side flats (7.98) | mill tooling | milling | F13 | False | None |
| S3 | OP330 | Drill 6 x D3.52 x 4.1 on PCD46 | mill tooling | drilling | F14 | False | None |

## AI assumptions (unverified)

- A1: S2 workholding grips the D50 section with protection; nothing protrudes in front of S2 Z-82. If the D100 flange is gripped, the X106 exit at Z-60 in OP120/OP130 must be re-checked.
- A2: The real S2 blank carries 29 mm excess beyond a=0 (240 - 210 - 1 faced in S1), so OP110 faces from Z+29. In LatheLab (raw end Z+1) the first 11 passes are air cuts. Delete them if the team saws to length instead.
- A3: Axial facing depth 2.5 mm per pass. Not approved; taken by analogy with the approved 2.5 mm radial roughing depth.
- A4: 'Roughing leaves 0.5 mm per side' is read as 0.5 mm normal to every surface, i.e. G71 U1.0 (diameter) W0.5; ID roughing 0.5 radial and 0.5 on the bore bottom.
- A5: G71 retract R1.0 mm. Not specified.
- A6: Feeds chosen inside the approved ranges: T01 roughing 0.20, T06 roughing 0.10 / finishing 0.08, T02 whole contour 0.10 at 500 rpm, because each contour contains an R5.
- A7: Peck depth 10 mm with full retract to Z5; rapid re-entry inside the drilled hole to 1 mm above the previous depth. Peck depth is not specified.
- A8: Drill tip depth Z-69, within reach 70; the 118 deg point (3.91 mm) gives full D13 to Z-65.1.
- A9: Spigot turned to a D36.7 envelope (key corners need >= D36.68). The final D29.9 and key are milled (OP310/OP320).
- A10: External thread = ISO 60 deg basic profile, external depth h3 = 0.6134 x 5 = 3.067 mm, major = turned D50, RH, end at Z-120 (a=90, 1 pitch before the fillet tangent). The F02/F22 groove area of 235 mm2 is plausible for a 60 deg groove of about 3 mm depth on D50, but that is only a plausibility check, not a designation.
- A11: The D100 in S1 is turned 2 mm past a=60 (to Z-152) so that the S2 face cut at a=60 blends without a step.
- A12: M03 for all tools; no coolant commanded (not in the configuration).
- A13: Nose-radius compensation only in finishing passes (G42 OD, G41 ID) with R/T from the offset page; roughing is uncompensated.
- A14: No G54 programmed; the work zero comes from the LatheLab stock dialog per the configuration.
- A15: Material C45 from the configuration (CAD material is null).
- A16: Unused: T03, T07, T08, T11, T12 (no approved cutting data); T09 is not usable (see OP150).
