"""Repository locations used by the Part E tools (all relative to the repository root)."""

from __future__ import annotations

from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent.parent
VALIDATION_DIR = TOOLS_DIR.parent  # 07_Comparison_Validation
REPO = VALIDATION_DIR.parent

MODE_I_DIR = REPO / "05_AI_Mode_I_Drawing"
MODE_II_DIR = REPO / "06_AI_Mode_II_CAD"
LATHE_BASELINE_DIR = REPO / "03_Lathe"
MILL_BASELINE_DIR = REPO / "04_Mill"

CONFIG_DIR = VALIDATION_DIR / "experiment_config"
CONFIG_PATH = CONFIG_DIR / "shared_experiment_config.json"
DIALECT_PATH = CONFIG_DIR / "simulator_dialect.json"
TEMPLATE_PATH = CONFIG_DIR / "prompt_template.md"
REFERENCE_DIR = VALIDATION_DIR / "evaluation_reference"
REVIEW_DIR = VALIDATION_DIR / "human_review_records"
SIM_EVIDENCE_DIR = VALIDATION_DIR / "simulation_evidence"
REVISION_LOG = VALIDATION_DIR / "program_revision_log.csv"
EFFORT_LOG = VALIDATION_DIR / "effort_log.csv"
MATRIX_CSV = VALIDATION_DIR / "six_case_matrix.csv"

DRAWING_INPUTS = MODE_I_DIR / "drawing_inputs"
MANIFEST_DIR = MODE_II_DIR / "extractor_and_manifest" / "manifests"

PARTS = {"lathe": "APSD-LATHE", "milling": "APSD-MILLING"}
DIALECT_OF = {"lathe": "lathelab", "milling": "milllab"}
BASELINE_OF = {"lathe": LATHE_BASELINE_DIR, "milling": MILL_BASELINE_DIR}
MODE_DIR = {"I": MODE_I_DIR, "II": MODE_II_DIR}
# Mode I drawing: team drawings of named version Ch2-Final (team decision 2026-11-28, see 05/drawing_inputs/input_manifest.json)
DRAWING_OF = {"lathe": "APSD_LATHE_team_drawing_vdd8cc179_300dpi.png", "milling": "APSD_MILLING_team_drawing_vdd8cc179_300dpi.png"}
NC_SUFFIXES = {".nc", ".txt", ".gcode", ".ngc", ".tap"}
