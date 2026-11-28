"""apsd_cam - Chapter 2 Part E, Mode II: CAD data -> CNC feature manifests.

This package EXTENDS the team's Chapter 1 Onshape pipeline instead of duplicating it.
The Chapter 1 modules (Onshape client, extraction, rotational geometry parser, OPITZ
manifest builder) are vendored byte-for-byte in ``scripts/vendor_ch1`` and imported
from there; see ``vendor_ch1/VENDORED_FROM_CHAPTER1.json`` for the source commit and
SHA-256 of every copied file.

New in Chapter 2:
  * ``prismatic``    - 2.5D milling analysis of the evaluated B-rep (APSD-MILLING)
  * ``cnc_manifest`` - CNC-oriented feature manifests for both parts, with every
                       value labelled CAD_EXTRACTED / GEOMETRICALLY_INFERRED /
                       HUMAN_ANNOTATED / UNKNOWN
  * ``targets``      - the Onshape tabs used for Part E
"""

from __future__ import annotations

import sys
from pathlib import Path

__version__ = "1.0.0"

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
EXTRACTOR_DIR = SCRIPTS_DIR.parent
VENDOR_DIR = SCRIPTS_DIR / "vendor_ch1"
SCHEMA_PATH = EXTRACTOR_DIR / "schemas" / "cnc_feature_manifest.schema.json"
EVIDENCE_ROOT = EXTRACTOR_DIR / "evidence"
MANIFEST_DIR = EXTRACTOR_DIR / "manifests"

if str(VENDOR_DIR) not in sys.path:
    sys.path.insert(0, str(VENDOR_DIR))
