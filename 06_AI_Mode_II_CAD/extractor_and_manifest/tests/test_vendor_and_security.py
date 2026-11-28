"""Reuse integrity (Chapter 1 code unchanged) and credential hygiene."""

from __future__ import annotations

import hashlib
import json
import re

from apsd_cam import EXTRACTOR_DIR, VENDOR_DIR


def test_vendored_chapter1_files_unchanged():
    rec = json.loads((VENDOR_DIR / "VENDORED_FROM_CHAPTER1.json").read_text(encoding="utf-8"))
    assert len(rec["files"]) >= 9
    for rel, meta in rec["files"].items():
        assert hashlib.sha256((VENDOR_DIR / rel).read_bytes()).hexdigest() == meta["sha256"], rel


def test_env_is_git_ignored():
    gi = (EXTRACTOR_DIR / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert ".env" in gi and "!.env.example" in gi


def test_example_env_has_no_values():
    for line in (EXTRACTOR_DIR / ".env.example").read_text(encoding="utf-8").splitlines():
        if line.startswith(("ONSHAPE_ACCESS_KEY", "ONSHAPE_SECRET_KEY")):
            assert line.split("=", 1)[1].strip() == ""


def test_no_credentials_in_evidence_or_manifests():
    pat = re.compile(r"(On [A-Za-z0-9]{10,}:HmacSHA256|Basic [A-Za-z0-9+/=]{20,}|secret_?key\"?\s*[:=]\s*\"[^\"<])", re.I)
    files = list((EXTRACTOR_DIR / "evidence").rglob("*.json")) + list((EXTRACTOR_DIR / "manifests").glob("*.json"))
    assert files
    for f in files:
        assert not pat.search(f.read_text(encoding="utf-8")), f


def test_request_log_has_no_auth_header():
    for rec in (EXTRACTOR_DIR / "evidence").glob("*/extraction_record.json"):
        data = json.loads(rec.read_text(encoding="utf-8"))
        for r in data["request_log"]:
            assert "authorization" not in json.dumps(r).lower()
