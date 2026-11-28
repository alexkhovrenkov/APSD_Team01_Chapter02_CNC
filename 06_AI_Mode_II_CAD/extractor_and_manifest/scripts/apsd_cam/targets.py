"""Onshape tabs used in Part E (non-secret identifiers).

All ids were observed in the element list of the team document on 2026-11-26
(read-only extraction, see evidence/*/03_elements.json). Override a part's tab with
APSD_LATHE_URL / APSD_MILLING_URL, e.g. to point at a NAMED VERSION
(https://cad.onshape.com/documents/<did>/v/<vid>/e/<eid>) once the Part A owner has
created one - that is the preferred way to freeze "the same final part revision".
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from apsd_pipeline.config import OnshapeTarget, parse_document_url  # vendored Chapter 1 code

HOST = "https://cad.onshape.com"
DOCUMENT_ID = "6877e7a6059a24d360e8c6e1"
WORKSPACE_ID = "008a5bb3f73e5b75f4629e14"


@dataclass(frozen=True)
class PartTab:
    key: str  # "lathe" | "milling"
    part_id: str  # course identifier
    process: str
    element_id: str  # Part Studio tab
    expected_element_name: str
    drawing_element_id: str  # drawing tab of the same part (view list only; no dimension text via API)

    @property
    def default_url(self) -> str:
        return f"{HOST}/documents/{DOCUMENT_ID}/w/{WORKSPACE_ID}/e/{self.element_id}"

    def target(self) -> OnshapeTarget:
        url = os.environ.get(f"APSD_{self.key.upper()}_URL", "").strip() or self.default_url
        return parse_document_url(url)


PARTS: dict[str, PartTab] = {
    "lathe": PartTab("lathe", "APSD-LATHE", "turning", "147da5f19a2ac767328e5f7f", "APSD-LATHE-Final",
                     "39fec93b315c33208dd4a282"),
    "milling": PartTab("milling", "APSD-MILLING", "milling", "20caaefd66e3a40229321161", "APSD-MILLING",
                       "d36cfe272e42345986bdfb77"),
}
