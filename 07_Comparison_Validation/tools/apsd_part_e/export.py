"""Copy the repository into the professor's recommended ZIP layout (brief 2.11) WITHOUT
changing the repository. Renames only in the copy (03_Lathe -> 03_Lathe_Human, 04_Mill ->
04_Mill_Human) and leaves out internal tooling and local files."""

from __future__ import annotations

import fnmatch
import shutil
import zipfile
from pathlib import Path

from .paths import REPO

RENAME = {"03_Lathe": "03_Lathe_Human", "04_Mill": "04_Mill_Human"}
EXCLUDE = [".git", ".git/*", "*/.venv", "*/.venv/*", "*/__pycache__", "*/__pycache__/*", "*.pyc", ".DS_Store", "*/.DS_Store",
           ".env", "*/.env", "*/.pytest_cache", "*/.pytest_cache/*", "EVALUATION.md", "evaluations", "evaluations/*", "*/.tmp_*", "*/.tmp_*/*"]


def excluded(relpath: str) -> bool:
    return any(fnmatch.fnmatch(relpath, pat) for pat in EXCLUDE)


def export(out_dir: Path, team: str = "Team01", make_zip: bool = True) -> Path:
    name = f"APSD_{team}_Chapter02_CNC"
    out_dir = out_dir.resolve()
    if out_dir == REPO.resolve() or REPO.resolve() in out_dir.parents:
        raise SystemExit("export target must be OUTSIDE the repository")
    root = out_dir / name
    if root.exists():
        raise SystemExit(f"{root} exists - choose an empty location")
    n = 0
    for p in sorted(REPO.rglob("*")):
        r = p.relative_to(REPO).as_posix()
        if p.is_dir() or excluded(r) or p.name == ".gitkeep":
            continue
        top, _, rest = r.partition("/")
        dest = root / RENAME.get(top, top) / rest if rest else root / RENAME.get(top, top)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dest)
        n += 1
    for d in ("00_Report", "01_Onshape_Drawings", "02_Process_Plans", "03_Lathe_Human", "04_Mill_Human",
              "05_AI_Mode_I_Drawing", "06_AI_Mode_II_CAD", "07_Comparison_Validation"):
        (root / d).mkdir(parents=True, exist_ok=True)
    if make_zip:
        z = out_dir / f"{name}.zip"
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in sorted(root.rglob("*")):
                zf.write(p, p.relative_to(out_dir).as_posix())
        print(f"{n} files -> {root} and {z}")
    return root
