# CAD-data extractor and feature manifests (Mode II)

## Chosen pathway and why

**Option iii – Onshape REST API + Python**, extending the Team01 Chapter 1 pipeline instead of writing a second one.

| Option | Assessment for this project |
|---|---|
| i. STEP + geometry parser | No STEP export exists in the repository. A B-rep parser (e.g. OpenCascade) would add a heavy dependency and still give the same analytic surfaces the API already returns. |
| ii. STL + mesh analysis | Triangulation loses exact radii, arcs, thread metadata and topology. Not chosen. |
| **iii. Onshape API** | **Chosen.** The Chapter 1 client (read-only, HMAC-signed, redacting, microversion-pinned) already works with the team's keys. `bodydetails` returns *exact* analytic geometry (plane origins/normals, cylinder radius/axis, torus radii, edge arc sweeps and end points), and the feature list adds design parameters (thread pitch, hole depth). One document snapshot covers both parts. |

Limitations of the API route: it needs a key and network access (manifests and evidence are committed, so all tests run
offline); calls count against the account's annual quota (11 per part per extraction); the drawing API returns view
definitions only, **not dimension text**; manufacturing semantics (tolerances, fits, finish, material, thread
designations) are absent from the B-rep.

## Layout

```
extractor_and_manifest/
  requirements.txt            pinned (same versions as Chapter 1)
  .env.example                key template; .env is git-ignored
  scripts/
    apsd_cam/                 NEW for Chapter 2
      targets.py              Onshape tabs (APSD-LATHE-Final, APSD-MILLING), override with a named-version URL
      prismatic.py            2.5D milling analysis (levels, bands, section loops, feature typing, patterns)
      cnc_manifest.py         lathe + milling CNC manifests, labels, validation
      __main__.py             CLI: check-env | extract | manifest | validate | summary
    vendor_ch1/               Chapter 1 modules, byte-identical (VENDORED_FROM_CHAPTER1.json: commit 17f6d60 + SHA-256 per file)
  schemas/cnc_feature_manifest.schema.json
  evidence/<UTC>_hmac_<part>/ sanitised API responses + extraction_record.json (request log, no keys)
  manifests/lathe_manifest.json, milling_manifest.json
  tests/                      33 offline tests
```

## Run

```bash
cd scripts
python -m apsd_cam check-env --env-file ../.env          # shows set/not set only
python -m apsd_cam extract --part all --env-file ../.env # read-only GETs; new evidence folder per run, never overwritten
python -m apsd_cam manifest --part all                   # newest evidence -> manifests/*.json, validated against the schema
python -m apsd_cam summary --part milling
cd .. && python -m pytest -q tests
```

## Method

**Lathe.** The Chapter 1 rotational parser and OPITZ fact builder run unchanged on the new evidence. `cnc_manifest.build_lathe`
re-expresses those facts as CNC features: end faces and shoulders, OD segments, R5 blends, bores, modelled threads, the
axial hole pattern and the raised key.

**Milling** (new, `prismatic.py`), the way a 2.5D CAM system builds regions:
1. *Tool axis*: the direction shared by the largest planar/rotational face area (here +Z). The part counts as 2.5D because
   every curved face is parallel to that axis.
2. *Levels*: planes perpendicular to the axis, grouped by height and facing side. Up-facing levels are reachable from the
   top setup and down-facing levels from the flipped setup.
3. *Bands and sections*: the level heights split the part into bands. Each band is sliced at mid-height. For every wall
   face, its edge loops are mapped into the face's (angle, height) parameter space and cut by the slice line (even–odd
   rule). This gives exact arcs even when one face (a boss cylinder) bounds several regions.
4. *Loops*: the section curves are chained by end points. Containment depth gives the side (even = material, odd = void).
5. *Typing*: full circle → boss/pin (material) or hole (void); void with an arc ≥ 300° plus planar walls → bore with slot
   (width = gap between facing walls, depth = end wall to bore axis); other void → through window or pocket (floor tested
   against the level faces); equal circles equidistant from a centre → circular pattern; tori → fillets; concentric arcs →
   wall thickness.

## Labels and traceability

Every value is labelled `CAD_EXTRACTED` (read from the B-rep or feature list; unit conversion only),
`GEOMETRICALLY_INFERRED` (computed by the extractor), `HUMAN_ANNOTATED` (named person, source, date) or `UNKNOWN` (null).
Every feature carries evidence pointers of the form `07_bodydetails.json#/bodies/0/faces/12`. The test suite resolves
every one of them and checks the SHA-256 of every evidence file.

## Results (named version **Ch2-Final** `dd8cc179d8265b20fe3f589e`, extracted 2026-11-28; model state `4d05edae182b19aa4ea1f30d`)

The default target is now this named version (`targets.py`), so a re-run reads exactly the same model. The first extraction
(2026-11-26, live workspace at the same model state) is kept in `evidence/` as history and produced identical features.

| | Lathe (23 features) | Milling (14 features, 7 relationships) |
|---|---|---|
| Envelope | 210 × Ø100 | 156 × 72.78 × 24 (X −30…126, Y −30…42.78, Z −10…14) |
| Reliably extracted | Ø29.9/60/100/50 profile with spans, R5 ×2, bores Ø12/13/30 with spans, 6 × Ø3.52 holes on PCD 46 depth 4.1, key 7.98 wide / 17.9 from the axis, thread pitches 5 and 2 | bosses Ø60 at (0,0) and Ø42 at (105,0), thickness 20; arm band 10; bore Ø30 through + keyway 8 wide ending 18 from the axis; hole Ø20 through; through window (R107/R68 + 4 × R8 + exposed boss arcs); 6 × Ø3.5 **pins**, 4 high, PCD 46; 8 concave R2 fillets; rib widths 8 and 8; boss centre distance 105 |
| Needs human annotation / UNKNOWN | thread designations and sizes (CAD `majorDiameter` = 25 is inconsistent), Hole feature Ø14 vs evaluated Ø12, material, stock, tolerances, finish, chamfers, key orientation relative to the holes | material, stock, tolerances and fits, finish, edge breaks beyond R2 |

The lathe geometry is identical to the Chapter 1 final revision (same faces and values; checked 2026-11-26).
