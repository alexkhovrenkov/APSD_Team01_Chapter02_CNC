"""Build CNC feature manifests (schema apsd-cnc-feature-manifest 1.0) from saved Onshape evidence.

Lathe:   the vendored Chapter 1 builder (apsd_pipeline.manifest.build_manifest) produces the
         verified OPITZ fact set; this module re-expresses those facts as CNC features
         (profile segments, faces, blends, bores, threads, hole pattern, key) and adds the
         Chapter 2 labels.
Milling: apsd_cam.prismatic analyses the B-rep (2.5D section loops); this module turns the
         regions into CNC features.

Labels: CAD_EXTRACTED = value read from the CAD data (unit conversion / radius->diameter
only); GEOMETRICALLY_INFERRED = computed by the extractor (spans, distances, feature
types, patterns); HUMAN_ANNOTATED = supplied by a named team member; UNKNOWN = null.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema

from . import EXTRACTOR_DIR, SCHEMA_PATH, VENDOR_DIR, __version__
from .prismatic import analyse_prismatic
from .targets import PARTS

LABELS = {
    "CAD_EXTRACTED": "Read directly from the Onshape B-rep or feature list; only unit conversion (m -> mm) or radius -> diameter applied.",
    "GEOMETRICALLY_INFERRED": "Computed by apsd_cam from CAD values (projections, spans, distances, section loops, feature types, patterns). Deterministic and re-runnable, but an interpretation.",
    "HUMAN_ANNOTATED": "Supplied by a named team member with a cited source and date; never merged into the CAD values.",
    "UNKNOWN": "Not available from the CAD data or a verified human source; value is null.",
}

MFG_EXCLUSION_REASON = ("Process hints are an extractor interpretation, not geometry. Mode I receives no such hints, "
                        "so the Mode II prompt builder strips this section to keep the comparison about the INPUT "
                        "REPRESENTATION (drawing vs CAD facts). Kept here for the human G2 process gate.")


def V(value: Any, unit: str | None, label: str, evidence: list[str] | None = None, note: str | None = None) -> dict:
    d: dict[str, Any] = {"value": value, "unit": unit, "label": label}
    if evidence:
        d["evidence"] = evidence
    if note:
        d["note"] = note
    return d


def U(note: str, unit: str | None = None) -> dict:
    return V(None, unit, "UNKNOWN", note=note)


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _load(ev: Path, name: str) -> Any:
    p = ev / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _common(ev: Path, part_key: str) -> dict:
    rec = _load(ev, "extraction_record.json")
    if rec is None:
        raise FileNotFoundError(f"{ev} has no extraction_record.json")
    tab = PARTS[part_key]
    if rec["target"]["element_id"] != tab.element_id and rec.get("element_name") != tab.expected_element_name:
        raise ValueError(f"evidence {ev.name} is element {rec['target']['element_id']} ({rec.get('element_name')}), "
                         f"not the {part_key} tab {tab.element_id}")
    vend = json.loads((VENDOR_DIR / "VENDORED_FROM_CHAPTER1.json").read_text(encoding="utf-8"))
    files = {p.name: _sha(p) for p in sorted(ev.glob("*.json"))}
    drawing = rec.get("drawing")
    try:
        rel_ev = str(ev.resolve().relative_to(EXTRACTOR_DIR.resolve()))
    except ValueError:
        rel_ev = str(ev)
    url_wvm = rec["target"].get("url_wvm")
    return {
        "rec": rec,
        "cad_source": {
            "method": "Onshape REST API (Part Studio body details, feature list, bounding boxes) - course option iii / Chapter 1 Path B",
            "host": rec["target"]["host"], "api_version": rec["api_version"],
            "document_id": rec["target"]["document_id"], "element_id": rec["target"]["element_id"],
            "element_name": rec.get("element_name"),
            "url_context": {"wvm": url_wvm, "wvm_id": rec["target"].get("url_wvm_id")},
            "snapshot_microversion": (rec.get("snapshot") or {}).get("wvm_id"),
            "element_microversion": rec.get("element_microversion"),
            "named_version": rec["target"].get("url_wvm_id") if url_wvm == "v" else None,
            "revision_changed_during_extraction": rec.get("revision_changed_during_extraction"),
            "drawing_element": drawing,
        },
        "extraction": {
            "run_id": rec["run_id"], "extracted_utc": rec["started_utc"], "evidence_dir": rel_ev,
            "evidence_files": files, "pipeline": "apsd_cam (Chapter 2 Part E) on top of vendored Chapter 1 apsd_pipeline",
            "pipeline_version": __version__,
            "vendored_chapter1": {"source_commit": vend["source_commit"], "source_branch": vend["source_branch"],
                                  "record": "scripts/vendor_ch1/VENDORED_FROM_CHAPTER1.json"},
            "endpoints": {k: v.get("status") for k, v in (rec.get("endpoints") or {}).items()},
            "manifest_built_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        },
    }


def _feature_tree(ev: Path) -> list[dict]:
    data = _load(ev, "04_features.json") or {}
    out = []
    for i, f in enumerate(data.get("features") or []):
        m = f.get("message", f)
        out.append({"index": i, "type": m.get("featureType"), "name": m.get("name"), "suppressed": m.get("suppressed"),
                    "pointer": f"04_features.json#/features/{i}"})
    return out


def _skeleton(part_key: str, common: dict, evidence_class: str) -> dict:
    tab = PARTS[part_key]
    return {
        "schema": "apsd-cnc-feature-manifest", "schema_version": "1.0", "label_convention": LABELS,
        "evidence_class": evidence_class,
        "part": {"id": tab.part_id, "process": tab.process, "name_in_cad": None, "body_count": 0},
        "units": {"length": "mm", "angle": "deg", "source_length_unit": "m (Onshape getPartStudioBodyDetails: 'All coordinates are in meters')",
                  "conversion": "mm = m x 1000, rounded to 0.0001 mm"},
        "cad_source": common["cad_source"], "extraction": common["extraction"],
    }


# =============================================================================== LATHE
def build_lathe(ev: Path, evidence_class: str = "LIVE_ONSHAPE_API") -> dict:
    from apsd_pipeline.geometry_parser import parse_bodydetails  # vendored
    from apsd_pipeline.manifest import build_manifest as ch1_build  # vendored

    common = _common(ev, "lathe")
    m = _skeleton("lathe", common, evidence_class)
    ch1 = ch1_build(ev, evidence_class="LIVE_ONSHAPE_API" if evidence_class == "LIVE_ONSHAPE_API" else "SYNTHETIC_TEST_FIXTURE")
    F = ch1["facts"]
    bd = _load(ev, "07_bodydetails.json")
    g = parse_bodydetails(bd)
    m["extraction"]["feature_tree"] = _feature_tree(ev)
    m["extraction"]["chapter1_fact_builder"] = "apsd_pipeline.manifest.build_manifest (vendored, unchanged) - facts validated against the Chapter 1 schema"
    parts = _load(ev, "05_parts.json") or []
    m["part"].update({"name_in_cad": parts[0].get("name") if parts else None, "body_count": g.get("solid_body_count", 0),
                      "material": U("no material assigned in Onshape (body properties material = null)")})
    ax = F["rotation_axis"]["value"]
    axis_ev = [e["ref"] for e in F["rotation_axis"]["evidence"]]
    L = F["overall_axial_length"]["value"]
    m["coordinate_system"] = {
        "frame": "Onshape Part Studio world coordinates (APSD-LATHE-Final tab)",
        "origin": f"world origin {ax['origin_mm']} mm, on the rotation axis at the spigot (small) end face",
        "axes": {"rotation_axis_direction": V(ax["direction"], None, "GEOMETRICALLY_INFERRED", axis_ev),
                 "axial_coordinate": V("a = world X; a = 0 at the spigot end face, a = %g at the threaded end face" % L, "mm",
                                       "GEOMETRICALLY_INFERRED", axis_ev),
                 "radial_coordinate": V("distance from the rotation axis (diameters are reported as diameters)", "mm", "GEOMETRICALLY_INFERRED")},
        "label": "GEOMETRICALLY_INFERRED",
        "note": "CAD frame only. The lathe work zero (e.g. Z0 on the finished front face, X as diameter in LatheLab) is a process decision in the shared experiment configuration, not CAD data.",
    }
    envelope_ev = ["07_bodydetails.json#/bodies/0/faces (analytic face boxes)", "08_boundingboxes.json"]
    bb = _load(ev, "08_boundingboxes.json") or {}
    D = F["max_relevant_diameter"]["value"]
    m["bounding_box"] = {
        "min_mm": [0.0, -D / 2, -D / 2], "max_mm": [L, D / 2, D / 2], "size_mm": [L, D, D],
        "label": "GEOMETRICALLY_INFERRED",
        "method": "axial extent from analytic face boxes projected on the axis; radial extent = largest external coaxial cylinder (key top at 17.9 mm is inside it)",
        "evidence": envelope_ev,
        "cross_check": {"onshape_partstudio_boundingbox_mm": {k: round(v * 1000, 4) for k, v in bb.items() if isinstance(v, (int, float))},
                        "note": "Onshape documents this box as approximate; reported for comparison only"},
    }
    feats: list[dict] = []

    def feat(fid, ftype, desc, label, dims, loc, evid, method, conf="high", unc="", verify=False, **kw):
        f = {"id": fid, "type": ftype, "description": desc, "label": label, "dimensions": dims, "location": loc,
             "evidence": evid, "extraction_method": method, "confidence": conf, "uncertainty": unc or "none identified",
             "needs_human_verification": verify}
        f.update(kw)
        feats.append(f)

    feat("L-AXIS", "rotation_axis", "Principal rotation (turning) axis", "GEOMETRICALLY_INFERRED",
         {"overall_axial_length": V(L, "mm", "GEOMETRICALLY_INFERRED", [e["ref"] for e in F["overall_axial_length"]["evidence"]]),
          "max_diameter": V(D, "mm", "CAD_EXTRACTED", [e["ref"] for e in F["max_relevant_diameter"]["evidence"]])},
         {"origin": V(ax["origin_mm"], "mm", "CAD_EXTRACTED", axis_ev), "direction": V(ax["direction"], None, "GEOMETRICALLY_INFERRED", axis_ev)},
         axis_ev, F["rotation_axis"]["confidence_reason"])

    # end faces and shoulders (planes normal to the axis), excluding the small hole bottoms
    hole_pat = (F["axial_holes"]["value"] or {}).get("patterns") or []
    hole_bottom_area = None
    planes = sorted(g["planes_normal_to_axis"], key=lambda p: p["axial_position_mm"])
    from collections import Counter
    cnt = Counter(round(p["axial_position_mm"], 4) for p in planes)
    nface = 0
    for p in planes:
        a = round(p["axial_position_mm"], 4)
        if hole_pat and cnt[a] == hole_pat[0]["count_of_cylinder_faces"]:
            hole_bottom_area = a
            continue
        nface += 1
        kind = "end_face" if a in (0.0, round(L, 4)) else "shoulder_face"
        feat(f"L-FACE-{nface:02d}", kind,
             f"Planar face normal to the axis at a = {a:g} mm ({p['area_mm2']:g} mm2)" + (" - part end face" if kind == "end_face" else ""),
             "CAD_EXTRACTED", {"area": V(p["area_mm2"], "mm2", "CAD_EXTRACTED", [p["pointer"]])},
             {"axial_position": V(a, "mm", "CAD_EXTRACTED", [p["pointer"]], "plane origin along the world-aligned axis")},
             [p["pointer"]], "geometry_parser: plane normal parallel to the rotation axis")

    for i, seg in enumerate(F["principal_diameters"]["value"], 1):
        cyl = next((c for c in g["external_cylinders"] if abs(c["diameter_mm"] - seg["diameter_mm"]) < 1e-6
                    and c["axial_span_mm"] and abs(c["axial_span_mm"][0] - seg["axial_from_mm"]) < 1e-6), None)
        evp = [cyl["pointer"]] if cyl else [e["ref"] for e in F["principal_diameters"]["evidence"]]
        feat(f"L-OD-{i:02d}", "external_cylinder", f"External diameter Ø{seg['diameter_mm']:g} from a = {seg['axial_from_mm']:g} to {seg['axial_to_mm']:g} mm",
             "CAD_EXTRACTED", {"diameter": V(seg["diameter_mm"], "mm", "CAD_EXTRACTED", evp, "2 x cylinder radius"),
                               "length": V(seg["length_mm"], "mm", "GEOMETRICALLY_INFERRED", evp)},
             {"axial_from": V(seg["axial_from_mm"], "mm", "GEOMETRICALLY_INFERRED", evp), "axial_to": V(seg["axial_to_mm"], "mm", "GEOMETRICALLY_INFERRED", evp)},
             evp, "geometry_parser: external coaxial cylinder (orientation=true), span from face box projected on the axis")

    for i, b in enumerate(F["radii_fillets"]["value"], 1):
        blend = next((c for c in g["blends"] if c["axial_span_mm"] == b["axial_span_mm"]), None)
        evp = [blend["pointer"]] if blend else ["07_bodydetails.json"]
        feat(f"L-BLEND-{i:02d}", "concave_fillet", f"Concave R{b['radius_mm']:g} blend between Ø{b['between_diameters_mm'][0]:g} and Ø{b['between_diameters_mm'][1]:g}",
             "CAD_EXTRACTED", {"radius": V(b["radius_mm"], "mm", "CAD_EXTRACTED", evp, "torus minor radius")},
             {"axial_span": V(b["axial_span_mm"], "mm", "GEOMETRICALLY_INFERRED", evp)},
             evp, "geometry_parser: coaxial torus, orientation=false (concave)")

    bores = [b for b in F["bores_and_counterbores"]["value"]["items"] if b.get("kind", "").startswith("internal coaxial")]
    hole_param = next((b for b in F["bores_and_counterbores"]["value"]["items"] if b.get("kind", "").startswith("Hole feature")), None)
    for i, b in enumerate(bores, 1):
        opens = b.get("opens_at_end") or []
        unc = ""
        if hole_param and i == 1:
            unc = (f"feature-list Hole parameter says Ø{hole_param['hole_diameter_parameter_mm']:g} x {hole_param['hole_depth_mm']:g}, "
                   f"evaluated geometry says Ø{b['diameter_mm']:g}; the evaluated geometry is used, the CAD owner should resolve the inconsistency")
        feat(f"L-BORE-{i:02d}", "internal_cylinder", f"Internal diameter Ø{b['diameter_mm']:g} from a = {b['axial_from_mm']:g} to {b['axial_to_mm']:g} mm"
             + (f", open at a = {opens[0]:g}" if opens else ", internal step (not open to an end face)"),
             "CAD_EXTRACTED", {"diameter": V(b["diameter_mm"], "mm", "CAD_EXTRACTED", b["evidence"]), "length": V(b["length_mm"], "mm", "GEOMETRICALLY_INFERRED", b["evidence"])},
             {"axial_from": V(b["axial_from_mm"], "mm", "GEOMETRICALLY_INFERRED", b["evidence"]), "axial_to": V(b["axial_to_mm"], "mm", "GEOMETRICALLY_INFERRED", b["evidence"])},
             b["evidence"] + ([hole_param["evidence"][0]] if unc else []), "geometry_parser: internal coaxial cylinder (orientation=false)",
             conf="high" if not unc else "medium", unc=unc, verify=bool(unc))

    def thread_feature(fid, fact_key, role):
        items = F[fact_key]["value"]["items"]
        cad = next((t for t in items if t.get("source", "").startswith("threadCreator")), None)
        geo = [t for t in items if t.get("source", "").startswith("evaluated geometry")]
        if not cad:
            return
        spans = [t["axial_span_mm_approx"] for t in geo]
        span = [round(min(s[0] for s in spans), 3), round(max(s[1] for s in spans), 3)] if spans else None
        near = sorted({d for t in geo for d in t.get("near_diameters_mm", [])})
        gev = [e for t in geo for e in t["evidence"]]
        feat(fid, f"{role}_thread_modelled", f"{role.capitalize()} helical thread modelled in CAD (threadCreator), pitch {cad['pitch_mm']:g} mm"
             + (f", near Ø{'/'.join(f'{d:g}' for d in near)}" if near else ""),
             "CAD_EXTRACTED",
             {"pitch": V(cad["pitch_mm"], "mm", "CAD_EXTRACTED", cad["evidence"]),
              "major_diameter_parameter": V(cad["major_diameter_parameter_mm"], "mm", "CAD_EXTRACTED", cad["evidence"],
                                            "third-party FeatureScript parameter; matches none of the diameters at the thread region - NOT a usable thread size"),
              "designation_standard_class": U("not in the CAD data: the reported label '%s' / profile '%s' is FeatureScript text, not a verified designation" % (cad["label_as_reported"], cad["profile_as_reported"])),
              "handedness": V("right-hand" if cad.get("left_handed") is False else None, None, "CAD_EXTRACTED" if cad.get("left_handed") is False else "UNKNOWN",
                              cad["evidence"], None if cad.get("left_handed") is False else "not reported")},
             {"axial_span_approx": V(span, "mm", "GEOMETRICALLY_INFERRED", gev, "from LOOSE bounding boxes of non-analytic helical faces (can exceed true extent by ~1 mm)") if span else U("helical faces not located"),
              "nominal_diameter_region": V(near, "mm", "GEOMETRICALLY_INFERRED", gev) if near else U("no adjacent cylinder found")},
             cad["evidence"] + gev, "vendored feature_parser (threadCreator parameters) + locate_freeform_faces (helical faces)",
             conf="medium", unc="; ".join(F[fact_key]["value"].get("consistency_notes", [])), verify=True)

    thread_feature("L-THREAD-EXT-01", "external_thread_in_cad_model", "external")
    thread_feature("L-THREAD-INT-01", "internal_threads", "internal")

    for i, pat in enumerate(hole_pat, 1):
        fl = next(iter(F["axial_holes"]["value"].get("feature_list") or []), {})
        start = None
        if hole_bottom_area is not None and fl.get("depth_mm"):
            start = round(hole_bottom_area - fl["depth_mm"], 4)
        dims = {"diameter": V(pat["hole_diameter_mm"], "mm", "CAD_EXTRACTED", pat["evidence"]),
                "count": V(pat["count_of_cylinder_faces"], None, "GEOMETRICALLY_INFERRED", pat["evidence"], "one cylinder face per hole observed"),
                "pitch_circle_diameter": V(pat["pitch_circle_diameter_mm"], "mm", "GEOMETRICALLY_INFERRED", pat["evidence"]),
                "depth": V(fl.get("depth_mm"), "mm", "CAD_EXTRACTED", [fl.get("pointer", "04_features.json")], "extrude REMOVE, BLIND") if fl.get("depth_mm") else U("depth not reported")}
        loc = {"angular_positions": V(pat["angular_positions_deg"], "deg", "GEOMETRICALLY_INFERRED", pat["evidence"], "angle origin = first hole found; only the spacing is meaningful"),
               "hole_bottom_axial_position": V(hole_bottom_area, "mm", "CAD_EXTRACTED", ["07_bodydetails.json (6 small planes normal to the axis)"]) if hole_bottom_area is not None else U("not found"),
               "entry_face_axial_position": V(start, "mm", "GEOMETRICALLY_INFERRED", ["hole bottom - depth"]) if start is not None else U("not derivable")}
        feat(f"L-HOLES-{i:02d}", "axial_hole_pattern", f"{pat['count_of_cylinder_faces']} x Ø{pat['hole_diameter_mm']:g} blind holes parallel to the axis on PCD {pat['pitch_circle_diameter_mm']:g}",
             "GEOMETRICALLY_INFERRED", dims, loc, pat["evidence"] + [fl.get("pointer", "04_features.json")],
             "geometry_parser: off-axis cylinders parallel to the axis grouped by radius and distance; depth from the cut feature")

    psf = F["plane_surface_features"]["value"]
    flats = psf["planar_faces_parallel_to_axis"]
    if flats:
        top = max(flats, key=lambda p: p["distance_from_axis_mm"])
        sides = [p for p in flats if p is not top]
        cf = (psf.get("creating_features") or [{}])[0]
        evp = [e["ref"] for e in F["plane_surface_features"]["evidence"]]
        width = round(2 * sides[0]["distance_from_axis_mm"], 4) if len(sides) == 2 and abs(sides[0]["distance_from_axis_mm"] - sides[1]["distance_from_axis_mm"]) < 1e-6 else None
        feat("L-KEY-01", "raised_key", f"Raised key on the Ø{top['on_diameter_mm']:g} spigot: flat top {top['distance_from_axis_mm']:g} mm from the axis, two parallel side flats"
             + (f" {width:g} mm apart" if width else ""), "GEOMETRICALLY_INFERRED",
             {"width": V(width, "mm", "GEOMETRICALLY_INFERRED", evp, "2 x distance of the side flats from the axis") if width else U("side flats not symmetric"),
              "top_distance_from_axis": V(top["distance_from_axis_mm"], "mm", "CAD_EXTRACTED", evp),
              "length": V(round(top["axial_span_mm"][1] - top["axial_span_mm"][0], 4), "mm", "GEOMETRICALLY_INFERRED", evp)},
             {"axial_span": V(top["axial_span_mm"], "mm", "GEOMETRICALLY_INFERRED", evp)},
             evp, "geometry_parser: planes parallel to the axis; ADD extrude '%s' in the feature list" % cf.get("operation", ""),
             conf="high", unc="angular orientation of the key relative to the hole pattern is not reported by this extractor")
    m["features"] = feats

    # relationships
    rels = [
        ("L/D ratio (overall length / max diameter)", F["length_to_diameter_ratio"]["value"], None, ["L-AXIS"]),
    ]
    flange = F["flange"]["value"]
    rels.append(("Flange (Ø%g) thickness" % flange["diameter_mm"], flange["length_mm"], "mm", [f["id"] for f in feats if f["type"] == "external_cylinder" and f["dimensions"]["diameter"]["value"] == flange["diameter_mm"]]))
    m["relationships"] = [{"id": f"L-REL-{i:02d}", "description": d, "value": v, "unit": u, "label": "GEOMETRICALLY_INFERRED",
                           "method": "computed from the listed features", "evidence": ["features " + ", ".join(fs)], "features": fs}
                          for i, (d, v, u, fs) in enumerate(rels, 1)]

    m["human_annotations"] = []
    for i, h in enumerate(ch1.get("human_supplied_facts") or [], 1):
        m["human_annotations"].append({
            "id": f"H-L-{i:02d}", "fact": h["fact"], "value": h["value"], "unit": h.get("unit"), "label": "HUMAN_ANNOTATED",
            "provenance": "Chapter 1 human_inputs/drawing_supplement.json (vendored unchanged)", "source": h["source"],
            "verified_by": h["verified_by"], "verified_on": h["verified_on"],
            "approved_for_mode_II_prompt": False,
            "fairness_note": "Read from the team DRAWING. Sending it in Mode II would give Mode II drawing information; the CAD already contains the external thread (pitch 5). Default: NOT sent. The team may approve it at gate G1 and must then disclose it.",
            "related_features": ["L-THREAD-EXT-01"]})

    m["missing_data"] = [
        {"item": "material", "label": "UNKNOWN", "reason": "no material assigned in Onshape", "needed_for": "cutting speeds/feeds (G2), simulator material setting"},
        {"item": "raw stock form and size", "label": "UNKNOWN", "reason": "process decision (Part B route sheet), not CAD", "needed_for": "simulator stock, roughing passes"},
        {"item": "tolerances, fits, surface finish", "label": "UNKNOWN", "reason": "not in the B-rep; drawing annotations are not returned by the API", "needed_for": "finishing strategy, inspection"},
        {"item": "thread designations, standards and tolerance classes (external p=5, internal p=2)", "label": "UNKNOWN", "reason": "threadCreator text is not a verified designation; majorDiameter parameter inconsistent", "needed_for": "threading cycle (G76/G92) depth and diameters"},
        {"item": "chamfers / edge breaks", "label": "UNKNOWN", "reason": "none modelled in CAD (Chapter 1 fact 'chamfers' = absent); drawing notes are not available through the API", "needed_for": "finishing passes"},
        {"item": "angular orientation of the key relative to the Ø3.52 hole pattern", "label": "UNKNOWN", "reason": "not computed by this extractor", "needed_for": "milling/indexing of the key and holes (not turning)"},
    ]
    m["manufacturing_considerations"] = {"excluded_from_mode_II_prompt": True, "reason": MFG_EXCLUSION_REASON, "items": [
        {"id": "L-MC-01", "text": "The raised key and the off-axis Ø3.52 holes are not producible by two-axis turning (need live tooling / C-axis or a milling setup).", "label": "GEOMETRICALLY_INFERRED", "basis": "planes parallel to the axis and off-axis cylinders", "applies_to": ["L-KEY-01", "L-HOLES-01"]},
        {"id": "L-MC-02", "text": "The flange (maximum diameter) lies between both ends, and both end faces carry bores: two lathe setups (re-chucking) are expected.", "label": "GEOMETRICALLY_INFERRED", "basis": "max_diameter_position = interior; bores open at a = 0 and a = L", "applies_to": ["L-OD-03", "L-BORE-01", "L-BORE-03"]},
        {"id": "L-MC-03", "text": "Concave R5 blends limit the finishing tool nose radius to <= 5 mm and need G02/G03 or compensated profiling.", "label": "GEOMETRICALLY_INFERRED", "basis": "torus minor radius 5", "applies_to": ["L-BLEND-01", "L-BLEND-02"]},
        {"id": "L-MC-04", "text": "External (p=5) and internal (p=2) threads require OD and ID threading tools; thread size data is missing (see missing_data).", "label": "GEOMETRICALLY_INFERRED", "basis": "threadCreator features", "applies_to": ["L-THREAD-EXT-01", "L-THREAD-INT-01"]},
    ]}
    m["limitations"] = [
        "Lathe facts come from the Chapter 1 builder (vendored unchanged); its own limitations apply (see vendor_ch1/apsd_pipeline/manifest.py).",
        "Thread regions are located with loose bounding boxes of helical faces; thread sizes are not derivable from this model.",
        "No drawing annotation text is available through the Onshape API; drawing-only information enters only as HUMAN_ANNOTATED entries.",
        "The CAD frame is not the machining frame: the lathe work zero and X-as-diameter convention are set in the shared experiment configuration.",
    ]
    return m


# =============================================================================== MILLING
def build_milling(ev: Path, evidence_class: str = "LIVE_ONSHAPE_API") -> dict:
    common = _common(ev, "milling")
    m = _skeleton("milling", common, evidence_class)
    bd = _load(ev, "07_bodydetails.json")
    a = analyse_prismatic(bd)
    if a.get("error"):
        raise ValueError(f"prismatic analysis failed: {a['error']}")
    m["extraction"]["feature_tree"] = _feature_tree(ev)
    m["extraction"]["prismatic_analysis"] = {"bands": a["bands"], "face_count": a["face_count"], "edge_count": a["edge_count"],
                                             "vertex_count": a["vertex_count"]}
    parts = _load(ev, "05_parts.json") or []
    body = bd["bodies"][a["body_index"]]
    mat = ((body.get("properties") or {}).get("material") or {})
    m["part"].update({"name_in_cad": parts[0].get("name") if parts else None, "body_count": a["solid_body_count"],
                      "material": V(mat.get("displayName") or mat.get("name"), None, "CAD_EXTRACTED", ["07_bodydetails.json#/bodies/0/properties/material"]) if mat
                      else U("no material assigned in Onshape (body properties material = null)")})
    ta = a["tool_axis"]
    m["coordinate_system"] = {
        "frame": "Onshape Part Studio world coordinates (APSD-MILLING tab)",
        "origin": "world origin = centre of the Ø30 bore axis at mid-thickness of the Ø60 boss (all heights are symmetric about 0)",
        "axes": {"tool_axis": V(ta["name"], None, "GEOMETRICALLY_INFERRED", ["07_bodydetails.json#/bodies/0/faces"], ta["basis"]),
                 "plane_axes": V(ta["plane_axes"], None, "CAD_EXTRACTED", None, "world axes perpendicular to the tool axis"),
                 "is_2_5d": V(ta["is_2_5d"], None, "GEOMETRICALLY_INFERRED", None, "every curved face parallel to the tool axis, every plane perpendicular or parallel to it")},
        "label": "GEOMETRICALLY_INFERRED",
        "note": "CAD frame only. The MillLab work zero (G54, e.g. a stock corner with Z0 on the finished top) and the second-setup datum are process decisions in the shared experiment configuration.",
    }
    env = a["envelope"]
    bb = _load(ev, "08_boundingboxes.json") or {}
    m["bounding_box"] = {"min_mm": env["min_mm"], "max_mm": env["max_mm"], "size_mm": env["size_mm"], "label": "GEOMETRICALLY_INFERRED",
                         "method": "min/max of analytic face boxes and vertices (" + env["basis"] + ")",
                         "evidence": ["07_bodydetails.json#/bodies/0/faces", "07_bodydetails.json#/bodies/0/vertices"],
                         "cross_check": {"onshape_partstudio_boundingbox_mm": {k: round(v * 1000, 4) for k, v in bb.items() if isinstance(v, (int, float))},
                                         "note": "Onshape documents this box as approximate; reported for comparison only"}}
    feats: list[dict] = []

    def feat(fid, ftype, desc, label, dims, loc, evid, method, conf="high", unc="", verify=False, **kw):
        f = {"id": fid, "type": ftype, "description": desc, "label": label, "dimensions": dims, "location": loc,
             "evidence": evid, "extraction_method": method, "confidence": conf, "uncertainty": unc or "none identified",
             "needs_human_verification": verify}
        f.update(kw)
        feats.append(f)

    up = ta["name"]
    for i, lv in enumerate(a["levels"], 1):
        evp = [f["pointer"] for f in lv["faces"]]
        feat(f"M-LEVEL-{i:02d}", "planar_level", f"{'Up' if lv['facing'] == '+' else 'Down'}-facing planar face(s) at height {lv['height_mm']:g} mm ({len(lv['faces'])} face(s), {lv['total_area_mm2']:g} mm2)",
             "CAD_EXTRACTED", {"total_area": V(lv["total_area_mm2"], "mm2", "CAD_EXTRACTED", evp)},
             {"height": V(lv["height_mm"], "mm", "CAD_EXTRACTED", evp, f"coordinate along {up}"),
              "facing": V(lv["facing"] + up[1], None, "GEOMETRICALLY_INFERRED", evp, "outward normal from plane normal and face orientation")},
             evp, "prismatic: planes perpendicular to the tool axis grouped by height and facing side", access_direction=lv["reachable_from"])

    regions = a["regions"]
    rid = {}
    ref = lambda t: [e["pointer"] for e in t["elements"]]  # noqa: E731

    def elements(t):
        return [{k: e[k] for k in ("kind", "radius_mm", "diameter_mm", "centre_mm", "convex", "sweep_deg", "start_mm", "end_mm", "length_mm", "direction_in_loop", "face_id", "pointer") if k in e}
                for e in t["elements"]]

    def span_v(t):
        return V(t["height_span_mm"], "mm", "GEOMETRICALLY_INFERRED", ref(t), "band(s) where this section loop exists: " + str(t["bands_mm"]))

    contour = [t for t in regions if t["type"] == "outer_contour"]
    for i, t in enumerate(contour, 1):
        rid[t["region_index"]] = f"M-CONTOUR-{i:02d}"
        feat(f"M-CONTOUR-{i:02d}", "outer_contour", f"Outer profile between heights {t['height_span_mm'][0]:g} and {t['height_span_mm'][1]:g} mm: "
             + ", ".join(f"{'convex' if e.get('convex') else 'concave'} R{e['radius_mm']:g}" if e["kind"] != "line" else f"line {e['length_mm']:g}" for e in t["elements"]),
             "GEOMETRICALLY_INFERRED",
             {"min_concave_radius": V(t["min_concave_radius_mm"], "mm", "CAD_EXTRACTED", ref(t)) if t.get("min_concave_radius_mm") else U("no concave element")},
             {"height_span": span_v(t), "extent": V(t["extent_mm"], "mm", "GEOMETRICALLY_INFERRED", ref(t))},
             ref(t), "prismatic: section loop at band mid-height, containment depth 0 (material)", geometry_elements=elements(t),
             access_direction="side walls parallel to the tool axis (contouring)")

    # bosses: group free-standing full circles by face, include the contour element of the same face
    boss_groups: dict[str, list] = {}
    for t in regions:
        if t["type"] == "boss":
            boss_groups.setdefault(t["elements"][0]["face_id"], []).append(t)
    for i, (fid, ts) in enumerate(sorted(boss_groups.items(), key=lambda kv: kv[1][0]["ref_centre_mm"]), 1):
        e = ts[0]["elements"][0]
        spans = [t["height_span_mm"] for t in ts] + [c["height_span_mm"] for c in contour if any(el["face_id"] == fid for el in c["elements"])]
        lo, hi = min(s[0] for s in spans), max(s[1] for s in spans)
        for t in ts:
            rid[t["region_index"]] = f"M-BOSS-{i:02d}"
        feat(f"M-BOSS-{i:02d}", "cylindrical_boss", f"Cylindrical boss Ø{e['diameter_mm']:g} centred at {e['centre_mm']}, height {lo:g}..{hi:g} mm (free-standing above/below the arm, merged with the arm profile in between)",
             "GEOMETRICALLY_INFERRED",
             {"diameter": V(e["diameter_mm"], "mm", "CAD_EXTRACTED", [e["pointer"]]), "height": V(round(hi - lo, 4), "mm", "GEOMETRICALLY_INFERRED", [e["pointer"]])},
             {"centre": V(e["centre_mm"], "mm", "CAD_EXTRACTED", [e["pointer"]]), "height_span": V([lo, hi], "mm", "GEOMETRICALLY_INFERRED", [e["pointer"]], "union of the bands where this face bounds material")},
             [e["pointer"]], "prismatic: convex full-circle section loop + same face in the outer contour")

    n = {"bore_with_slot": 0, "hole": 0, "through_window": 0, "pocket": 0}
    for t in regions:
        if t["type"] == "bore_with_slot":
            n["bore_with_slot"] += 1
            k = n["bore_with_slot"]
            bore = next(e for e in t["elements"] if e["kind"] in ("arc", "full_circle") and e["sweep_deg"] >= 300)
            s = t["slot"]
            rid[t["region_index"]] = f"M-BORE-{k:02d}"
            through = t["spans_full_part_height"] or (t["open_both_ends"])
            feat(f"M-BORE-{k:02d}", "bore", f"Bore Ø{bore['diameter_mm']:g} at {bore['centre_mm']}, height {t['height_span_mm'][0]:g}..{t['height_span_mm'][1]:g} mm, "
                 + ("open at both ends (through)" if t["open_both_ends"] else "with floor/closed end") + f", interrupted by a slot ({bore['sweep_deg']:g} deg of circle remain)",
                 "GEOMETRICALLY_INFERRED",
                 {"diameter": V(bore["diameter_mm"], "mm", "CAD_EXTRACTED", [bore["pointer"]]), "depth": V(round(t["height_span_mm"][1] - t["height_span_mm"][0], 4), "mm", "GEOMETRICALLY_INFERRED", ref(t))},
                 {"centre": V(bore["centre_mm"], "mm", "CAD_EXTRACTED", [bore["pointer"]]), "height_span": span_v(t),
                  "through": V(bool(through), None, "GEOMETRICALLY_INFERRED", ref(t), "no floor/closed-top level face inside the loop")},
                 ref(t), "prismatic: void section loop with a >=300 deg concave arc plus planar walls", geometry_elements=elements(t),
                 related_features=[f"M-KEYWAY-{k:02d}"])
            feat(f"M-KEYWAY-{k:02d}", "keyway_slot", f"Keyway/slot in bore M-BORE-{k:02d}: width {s.get('width_mm')} mm, closed end {s.get('end_wall_distance_from_bore_axis_mm')} mm from the bore axis",
                 "GEOMETRICALLY_INFERRED",
                 {"width": V(s.get("width_mm"), "mm", "GEOMETRICALLY_INFERRED", s["walls"], s.get("width_basis")),
                  "end_wall_distance_from_bore_axis": V(s.get("end_wall_distance_from_bore_axis_mm"), "mm", "GEOMETRICALLY_INFERRED", s["walls"]),
                  "depth_beyond_bore_surface": V(s.get("depth_beyond_bore_surface_mm"), "mm", "GEOMETRICALLY_INFERRED", s["walls"])},
                 {"direction_from_bore_axis": V(s.get("direction_from_bore_axis"), None, "GEOMETRICALLY_INFERRED", s["walls"]),
                  "height_span": span_v(t)},
                 s["walls"], "prismatic: anti-parallel facing walls (width) + perpendicular end wall", related_features=[f"M-BORE-{k:02d}"])
        elif t["type"] == "hole":
            n["hole"] += 1
            k = n["hole"]
            e = t["elements"][0]
            rid[t["region_index"]] = f"M-HOLE-{k:02d}"
            feat(f"M-HOLE-{k:02d}", "hole", f"Cylindrical hole Ø{e['diameter_mm']:g} at {e['centre_mm']}, height {t['height_span_mm'][0]:g}..{t['height_span_mm'][1]:g} mm"
                 + (", through" if t["open_both_ends"] else ", blind"), "GEOMETRICALLY_INFERRED",
                 {"diameter": V(e["diameter_mm"], "mm", "CAD_EXTRACTED", [e["pointer"]]), "depth": V(round(t["height_span_mm"][1] - t["height_span_mm"][0], 4), "mm", "GEOMETRICALLY_INFERRED", [e["pointer"]])},
                 {"centre": V(e["centre_mm"], "mm", "CAD_EXTRACTED", [e["pointer"]]), "height_span": span_v(t),
                  "through": V(bool(t["open_both_ends"]), None, "GEOMETRICALLY_INFERRED", [e["pointer"]])},
                 [e["pointer"]], "prismatic: concave full-circle void loop")
        elif t["type"] in ("through_window", "pocket"):
            n[t["type"]] += 1
            k = n[t["type"]]
            fid = f"M-{'WINDOW' if t['type'] == 'through_window' else 'POCKET'}-{k:02d}"
            rid[t["region_index"]] = fid
            feat(fid, t["type"], ("Through window (internal opening) " if t["type"] == "through_window" else "Pocket ")
                 + f"between heights {t['height_span_mm'][0]:g} and {t['height_span_mm'][1]:g} mm bounded by "
                 + ", ".join(f"{'convex' if e.get('convex') else 'concave'} R{e['radius_mm']:g}" if e["kind"] != "line" else f"line {e['length_mm']:g}" for e in t["elements"]),
                 "GEOMETRICALLY_INFERRED",
                 {"min_concave_radius": V(t.get("min_concave_radius_mm"), "mm", "CAD_EXTRACTED", ref(t), "smallest concave corner radius in the loop") if t.get("min_concave_radius_mm") else U("no concave element"),
                  "depth": V(round(t["height_span_mm"][1] - t["height_span_mm"][0], 4), "mm", "GEOMETRICALLY_INFERRED", ref(t))},
                 {"height_span": span_v(t), "extent": V(t["extent_mm"], "mm", "GEOMETRICALLY_INFERRED", ref(t)),
                  "floor_at": V(t["floor_at_mm"], "mm", "GEOMETRICALLY_INFERRED", ref(t)) if t.get("floor_at_mm") is not None else V("none (open)", None, "GEOMETRICALLY_INFERRED", ref(t)),
                  "interior_point": V(t["interior_probe_mm"], "mm", "GEOMETRICALLY_INFERRED", ref(t), "a point inside the opening, useful for plunge/entry planning")},
                 ref(t), "prismatic: void section loop without a near-full circle; floor/closed-top tested against level faces",
                 geometry_elements=elements(t))

    for i, p in enumerate(a["patterns"], 1):
        members = [t for t in regions if t["region_index"] in p["region_indices"]]
        evp = [t["elements"][0]["pointer"] for t in members]
        centres = [t["elements"][0]["centre_mm"] for t in members]
        feat(f"M-PINS-{i:02d}" if p["element"] == "pin" else f"M-HOLES-{i:02d}", f"{p['element']}_pattern",
             f"{p['count']} x Ø{p['diameter_mm']:g} {'pins (raised cylinders)' if p['element'] == 'pin' else 'holes'} on PCD {p['pitch_circle_diameter_mm']:g} around {p['pattern_centre_mm']}, height {p['height_span_mm'][0]:g}..{p['height_span_mm'][1]:g} mm",
             "GEOMETRICALLY_INFERRED",
             {"diameter": V(p["diameter_mm"], "mm", "CAD_EXTRACTED", evp), "count": V(p["count"], None, "GEOMETRICALLY_INFERRED", evp),
              "pitch_circle_diameter": V(p["pitch_circle_diameter_mm"], "mm", "GEOMETRICALLY_INFERRED", evp),
              ("height" if p["element"] == "pin" else "depth"): V(round(p["height_span_mm"][1] - p["height_span_mm"][0], 4), "mm", "GEOMETRICALLY_INFERRED", evp)},
             {"pattern_centre": V(p["pattern_centre_mm"], "mm", "GEOMETRICALLY_INFERRED", evp), "angular_positions": V(p["angular_positions_deg"], "deg", "GEOMETRICALLY_INFERRED", evp, "CCW from +X viewed from " + up),
              "centres": V(centres, "mm", "CAD_EXTRACTED", evp), "height_span": V(p["height_span_mm"], "mm", "GEOMETRICALLY_INFERRED", evp)},
             evp, "prismatic: equal full-circle loops equidistant from a bore/boss centre",
             access_direction=f"{up} side (top setup)" if p["height_span_mm"][0] >= 0 else "opposite side")

    if a["blends"]:
        groups: dict[tuple, list] = {}
        for b in a["blends"]:
            groups.setdefault((b["fillet_radius_mm"], b["concave"]), []).append(b)
        for i, ((r, concave), bs) in enumerate(sorted(groups.items()), 1):
            evp = [b["pointer"] for b in bs]
            where = sorted({(tuple(b["centre_mm"]), b["sweep_circle_radius_mm"], b["height_mm"]) for b in bs})
            feat(f"M-FILLET-{i:02d}", "edge_fillet", f"{len(bs)} {'concave' if concave else 'convex'} R{r:g} fillet faces (tori) around " + "; ".join(f"{list(c)} at height {h:g}" for c, _, h in where),
                 "CAD_EXTRACTED", {"radius": V(r, "mm", "CAD_EXTRACTED", evp, "torus minor radius")},
                 {"instances": V([{"axis_centre_mm": list(c), "sweep_circle_radius_mm": R, "height_mm": h} for c, R, h in where], "mm", "CAD_EXTRACTED", evp)},
                 evp, "prismatic: torus faces with axis parallel to the tool axis",
                 access_direction="both sides (fillets at positive and negative heights)" if any(h > 0 for *_, h in where) and any(h < 0 for *_, h in where) else "")
    m["features"] = feats

    # relationships
    rels = []
    bosses = [f for f in feats if f["type"] == "cylindrical_boss"]
    if len(bosses) >= 2:
        c0, c1 = bosses[0]["location"]["centre"]["value"], bosses[1]["location"]["centre"]["value"]
        import math
        rels.append(("Centre distance between the two bosses / bores", round(math.dist(c0, c1), 4), "mm", [bosses[0]["id"], bosses[1]["id"]]))
    lv = {(round(l["location"]["height"]["value"], 4), l["location"]["facing"]["value"][0]) for l in feats if l["type"] == "planar_level"}
    ups = sorted(h for h, s in lv if s == "+")
    downs = sorted(h for h, s in lv if s == "-")
    for f in (x for x in feats if x["type"] == "outer_contour"):
        s = f["location"]["height_span"]["value"]
        rels.append((f"{f['id']} (profile band) thickness", round(s[1] - s[0], 4), "mm", [f["id"]]))
    for b in bosses:
        s = b["location"]["height_span"]["value"]
        rels.append((f"{b['id']} thickness", round(s[1] - s[0], 4), "mm", [b["id"]]))
    # concentric wall pairs (rib widths): arcs sharing a centre inside one contour/window
    arcs = [(f["id"], e) for f in feats for e in f.get("geometry_elements", []) if e.get("kind") == "arc"]
    seen = set()
    for i, (fa, ea) in enumerate(arcs):
        for fb, eb in arcs[i + 1:]:
            if fa != fb and ea["centre_mm"] == eb["centre_mm"] and ea["radius_mm"] != eb["radius_mm"]:
                key = (tuple(ea["centre_mm"]), *sorted((ea["radius_mm"], eb["radius_mm"])))
                if key in seen:
                    continue
                seen.add(key)
                rels.append((f"Radial wall thickness between concentric walls R{max(ea['radius_mm'], eb['radius_mm']):g} and R{min(ea['radius_mm'], eb['radius_mm']):g} about {ea['centre_mm']}",
                             round(abs(ea["radius_mm"] - eb["radius_mm"]), 4), "mm", [fa, fb]))
    m["relationships"] = [{"id": f"M-REL-{i:02d}", "description": d, "value": v, "unit": u, "label": "GEOMETRICALLY_INFERRED",
                           "method": "computed from the listed features' CAD values", "evidence": ["features " + ", ".join(fs)], "features": fs}
                          for i, (d, v, u, fs) in enumerate(rels, 1)]
    m["human_annotations"] = []
    m["missing_data"] = [
        {"item": "material", "label": "UNKNOWN", "reason": "no material assigned in Onshape", "needed_for": "cutting data (G2), MillLab material"},
        {"item": "raw stock block size and allowances", "label": "UNKNOWN", "reason": "process decision (Part B route sheet), not CAD", "needed_for": "MillLab workpiece, facing passes"},
        {"item": "tolerances, fits (Ø30/Ø20 bores, keyway, pins), surface finish", "label": "UNKNOWN", "reason": "not in the B-rep; drawing annotations are not returned by the API", "needed_for": "finishing / boring strategy, inspection"},
        {"item": "edge breaks / chamfers other than the modelled R2 fillets", "label": "UNKNOWN", "reason": "not modelled; title-block notes are not available through the API", "needed_for": "deburring passes"},
    ]
    mc = []
    if ups and downs and any(h for h in ups if h < max(ups)) and any(h for h in downs if h > min(downs)):
        mc.append({"id": "M-MC-01", "text": "Recessed levels face both directions (up-facing below the top and down-facing above the bottom): at least two setups (flip about a horizontal axis) are needed, or the down-facing faces stay unmachined.",
                   "label": "GEOMETRICALLY_INFERRED", "basis": f"up-facing heights {ups}, down-facing heights {downs}", "applies_to": [f["id"] for f in feats if f["type"] == "planar_level"]})
    win = [f for f in feats if f["type"] in ("through_window", "pocket")]
    for w in win:
        r = w["dimensions"]["min_concave_radius"]["value"]
        if r:
            mc.append({"id": f"M-MC-{len(mc) + 1:02d}", "text": f"{w['id']}: smallest concave corner R{r:g} -> finishing cutter diameter <= {2 * r:g} mm (smaller to avoid full-radius engagement).",
                       "label": "GEOMETRICALLY_INFERRED", "basis": "min concave radius of the section loop", "applies_to": [w["id"]]})
    for f in feats:
        if f["type"] == "keyway_slot" and f["dimensions"]["width"]["value"]:
            mc.append({"id": f"M-MC-{len(mc) + 1:02d}", "text": f"{f['id']}: slot width {f['dimensions']['width']['value']:g} mm -> cutter diameter <= that width; the slot's square closed end cannot be made exactly by a rotating cutter (corner radius = cutter radius) unless broached/slotted.",
                       "label": "GEOMETRICALLY_INFERRED", "basis": "facing walls + perpendicular end wall", "applies_to": [f["id"]]})
        if f["type"] == "edge_fillet":
            mc.append({"id": f"M-MC-{len(mc) + 1:02d}", "text": f"{f['id']}: R{f['dimensions']['radius']['value']:g} fillets between horizontal and vertical faces need a ball/bull-nose cutter or are left as a documented simulator limitation.",
                       "label": "GEOMETRICALLY_INFERRED", "basis": "torus faces", "applies_to": [f["id"]]})
        if f["type"] == "pin_pattern":
            mc.append({"id": f"M-MC-{len(mc) + 1:02d}", "text": f"{f['id']}: the pins stand above the boss top, so the boss top must be machined AROUND them (contour each pin); the raw stock top must lie at or above the pin tops.",
                       "label": "GEOMETRICALLY_INFERRED", "basis": "pins occupy the highest band", "applies_to": [f["id"]]})
    m["manufacturing_considerations"] = {"excluded_from_mode_II_prompt": True, "reason": MFG_EXCLUSION_REASON, "items": mc}
    m["limitations"] = list(a["limitations"])
    return m


# =============================================================================== validation / io
def validate(manifest: dict) -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(manifest, schema, cls=jsonschema.Draft202012Validator)
    ids = [f["id"] for f in manifest["features"]]
    if len(ids) != len(set(ids)):
        raise jsonschema.ValidationError(f"duplicate feature ids: {sorted({i for i in ids if ids.count(i) > 1})}")
    ev_dir = manifest["extraction"]["evidence_files"]
    for f in manifest["features"]:
        for ref in f["evidence"]:
            fname = ref.split("#")[0].split(" ")[0]
            if fname.endswith(".json") and fname not in ev_dir:
                raise jsonschema.ValidationError(f"{f['id']}: evidence file {fname} is not part of the extraction run")


def write(manifest: dict, path: Path) -> None:
    validate(manifest)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


BUILDERS = {"lathe": build_lathe, "milling": build_milling}
