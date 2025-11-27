# ⚠️ Compliance Notice:
# This module operates in assistive mode only.
# Do NOT overwrite validated Excel cells or macros in the source workbook.
# AI outputs must be written only to new columns prefixed with "AI_".

"""
Excel Reader - Module 1 (M1)

Safe, read-only Excel reader for review workbooks with sheet profiling and CSV preview.

Created by: Navid Broumandfar
"""

from __future__ import annotations
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple
import pandas as pd

from src.utils.config_loader import load_config, Config


@dataclass
class SheetProfile:
    sheet_name: str
    header_row_index: int
    row_count: int
    col_count: int
    columns: list[str]
    missing_rate_by_col: dict[str, float]


def _ensure_out_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def _detect_header(df_raw: pd.DataFrame) -> int:
    # Count non-empty per row
    counts = df_raw.apply(lambda r: r.astype(str).str.strip().ne("").sum(), axis=1)
    # Choose the first row with the maximum non-empty count
    return int(counts.idxmax())


def _clean_df(df: pd.DataFrame) -> pd.DataFrame:
    # Drop fully empty columns
    df = df.dropna(axis=1, how="all")
    # Convert blank strings to NaN for uniformity
    df = df.applymap(lambda x: (None if (pd.isna(x) or str(x).strip() == "") else x))
    # Drop fully empty rows
    df = df.dropna(axis=0, how="all")
    # Normalize column names
    cols = []
    seen = {}
    for c in df.columns.astype(str).str.strip():
        base = c or "Unnamed"
        if base in seen:
            seen[base] += 1
            cols.append(f"{base}__{seen[base]}")
        else:
            seen[base] = 0
            cols.append(base)
    df.columns = cols
    return df


def _profile(df: pd.DataFrame, sheet_name: str, header_row_index: int) -> SheetProfile:
    mr = {c: float(pd.isna(df[c]).mean()) for c in df.columns}
    return SheetProfile(
        sheet_name=sheet_name,
        header_row_index=header_row_index,
        row_count=int(len(df)),
        col_count=int(len(df.columns)),
        columns=list(df.columns),
        missing_rate_by_col=mr,
    )


def read_review_sheet(config: Config) -> Tuple[pd.DataFrame, SheetProfile]:
    xlsx = Path(config.input_file)
    if not xlsx.exists():
        raise RuntimeError(f"Input file not found: {xlsx}")

    # Read raw sheet (no header) to detect header row robustly
    df_raw = pd.read_excel(
        xlsx, sheet_name=config.sheet_name, header=None, engine="openpyxl", dtype=str
    )
    if df_raw.empty:
        raise RuntimeError(f"Sheet '{config.sheet_name}' is empty in {xlsx.name}")

    header_idx = _detect_header(df_raw)

    # Re-read with detected header
    df = pd.read_excel(
        xlsx,
        sheet_name=config.sheet_name,
        header=header_idx,
        engine="openpyxl",
        dtype=str,
    )

    df = _clean_df(df)
    profile = _profile(df, config.sheet_name, header_idx)
    return df, profile


if __name__ == "__main__":
    try:
        cfg = load_config()
        df, prof = read_review_sheet(cfg)
        out_dir = _ensure_out_dir(cfg.out_dir)
        # Export preview
        preview_path = out_dir / "review_sheet_preview.csv"
        df.head(cfg.preview_rows).to_csv(preview_path, index=False, encoding="utf-8")
        print(
            f"Loaded {prof.sheet_name} with {prof.row_count} rows, {prof.col_count} columns."
        )
        print(f"Preview saved to: {preview_path}")
    except Exception as e:
        print(f"[M1] Error: {e}", file=sys.stderr)
        sys.exit(1)
