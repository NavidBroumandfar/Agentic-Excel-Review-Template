# ⚠️ Compliance Notice:
# This module operates in assistive mode only.
# Do NOT overwrite validated Excel cells or macros in the source workbook.
# AI outputs must be written only to new columns prefixed with "AI_".

from __future__ import annotations
import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    input_file: str = "data/Sample_Review_Workbook.xlsx"
    sheet_name: str = "ReviewSheet"
    out_dir: str = "out"
    preview_rows: int = 200


_DEF = Config()


def load_config(path: str | Path = "config.json") -> Config:
    cfg = dict()
    p = Path(path)
    if p.exists():
        cfg = json.loads(p.read_text(encoding="utf-8"))

    # env overrides
    cfg_env = {
        "input_file": os.getenv("EXCEL_REVIEW_INPUT_FILE"),
        "sheet_name": os.getenv("EXCEL_REVIEW_SHEET_NAME"),
        "out_dir": os.getenv("EXCEL_REVIEW_OUT_DIR"),
        "preview_rows": os.getenv("EXCEL_REVIEW_PREVIEW_ROWS"),
    }
    cfg.update({k: v for k, v in cfg_env.items() if v not in (None, "")})

    # coerce types
    pr = int(cfg.get("preview_rows", _DEF.preview_rows))
    return Config(
        input_file=cfg.get("input_file", _DEF.input_file),
        sheet_name=cfg.get("sheet_name", _DEF.sheet_name),
        out_dir=cfg.get("out_dir", _DEF.out_dir),
        preview_rows=pr,
    )
