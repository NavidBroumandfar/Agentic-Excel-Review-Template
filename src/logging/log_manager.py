# ⚠️ Compliance Notice:
# Read-only: do not modify/delete existing logs or Excel files.
# Preserve traceability: keep original event ids/timestamps; include SHA256 checksums.
# Outputs: /logs/metrics_summary_YYYYMM.jsonl and /logs/monthly_metrics_summary.csv

from __future__ import annotations
import argparse, glob, hashlib, json, os
from datetime import datetime
from typing import List, Dict, Any, Tuple
import pandas as pd

try:
    import jsonlines
except Exception as e:
    raise SystemExit(
        "Missing dependency 'jsonlines'. Add it to requirements.txt and reinstall."
    ) from e

LOG_DIR = "logs"
SPARK_CHARS = "▁▂▃▄▅▆▇█"  # 8-level sparkline glyphs


# ---------- IO ----------
def load_jsonl(path: str) -> List[Dict[str, Any]]:
    """Safely load a JSONL file; skip corrupted lines but keep count externally."""
    records = []
    if not os.path.exists(path):
        return records
    with jsonlines.open(path, "r") as reader:
        for obj in reader.iter(type=dict, skip_invalid=True):
            records.append(obj)
    return records


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _to_naive_iso(ts: str | None) -> str | None:
    # Keep original string (best-effort normalization without rewriting logs)
    return ts if ts else None


# ---------- Sparkline Helpers ----------
def _downsample(values: List[float], max_len: int) -> List[float]:
    """
    Evenly sample the list down to max_len points (inclusive endpoints).
    Preserves overall trend for long months.
    """
    if max_len <= 0 or len(values) <= max_len:
        return values
    # Choose evenly spaced indices, always include first/last
    import math

    step = (len(values) - 1) / (max_len - 1)
    idxs = [round(i * step) for i in range(max_len)]
    return [values[i] for i in idxs]


def make_sparkline(values: List[float], max_len: int | None = None) -> str:
    """
    Return a unicode sparkline (▁▂▃▄▅▆▇█).
    If max_len is provided, downsample before rendering.
    """
    arr = pd.Series(values).dropna().astype(float)
    if arr.empty:
        return ""
    if max_len is not None:
        arr = pd.Series(_downsample(arr.tolist(), max_len))
    vmin, vmax = float(arr.min()), float(arr.max())
    if vmax == vmin:
        return SPARK_CHARS[0] * len(arr)
    scaled = (arr - vmin) / (vmax - vmin)  # 0..1
    idx = (
        (scaled * (len(SPARK_CHARS) - 1))
        .round()
        .astype(int)
        .clip(0, len(SPARK_CHARS) - 1)
    )
    return "".join(SPARK_CHARS[i] for i in idx)


# ---------- Aggregation ----------
def summarize_inference_logs(pattern: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    files = sorted(glob.glob(pattern))
    rows, integrity = [], {"files": [], "missing_fields": 0}
    for fp in files:
        recs = load_jsonl(fp)
        integrity["files"].append(
            {"path": fp, "count": len(recs), "sha256": _sha256_file(fp)}
        )
        for r in recs:
            rows.append(
                {
                    "ts": _to_naive_iso(r.get("ts") or r.get("timestamp")),
                    "model_version": r.get("model_version"),
                    "confidence": r.get("confidence"),
                    "reason": r.get("reason"),
                    "run_id": r.get("run_id"),
                    "row_id": r.get("row_id"),
                    "level": (r.get("level") or "INFO").upper(),
                    "_source_file": os.path.basename(fp),
                }
            )
            if r.get("confidence") is None or r.get("reason") is None:
                integrity["missing_fields"] += 1
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(by="ts", kind="stable")
    return df, integrity


def summarize_writer_logs(pattern: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    files = sorted(glob.glob(pattern))
    rows, integrity = [], {"files": [], "missing_fields": 0}
    for fp in files:
        recs = load_jsonl(fp)
        integrity["files"].append(
            {"path": fp, "count": len(recs), "sha256": _sha256_file(fp)}
        )
        for r in recs:
            rows.append(
                {
                    "ts": _to_naive_iso(r.get("ts") or r.get("timestamp")),
                    "run_id": r.get("run_id"),
                    "rows_written": r.get("rows_written"),
                    "status": (r.get("status") or r.get("level") or "INFO").upper(),
                    "_source_file": os.path.basename(fp),
                }
            )
            if r.get("rows_written") is None:
                integrity["missing_fields"] += 1
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(by="ts", kind="stable")
    return df, integrity


def aggregate_metrics(
    df_inf: pd.DataFrame, df_wrt: pd.DataFrame, sparklen: int
) -> Dict[str, Any]:
    metrics: Dict[str, Any] = {}

    # Inference
    if not df_inf.empty:
        metrics["ai_suggestions_total"] = int(len(df_inf))
        metrics["avg_confidence"] = (
            float(pd.to_numeric(df_inf["confidence"], errors="coerce").dropna().mean())
            if "confidence" in df_inf
            else None
        )
        metrics["distinct_model_versions"] = (
            sorted(df_inf["model_version"].dropna().unique().tolist())
            if "model_version" in df_inf
            else []
        )
        metrics["errors_inference"] = (
            int((df_inf["level"].fillna("INFO").str.upper() == "ERROR").sum())
            if "level" in df_inf
            else 0
        )
        metrics["log_completeness_pct"] = round(
            100.0 * (df_inf["reason"].notna().mean()), 2
        )
        confidences = (
            pd.to_numeric(df_inf["confidence"], errors="coerce").dropna().tolist()
            if "confidence" in df_inf
            else []
        )
        metrics["confidence_sparkline"] = make_sparkline(
            confidences, max_len=sparklen if sparklen > 0 else None
        )
    else:
        metrics.update(
            dict(
                ai_suggestions_total=0,
                avg_confidence=None,
                distinct_model_versions=[],
                errors_inference=0,
                log_completeness_pct=0.0,
                confidence_sparkline="",
            )
        )

    # Writer
    if not df_wrt.empty:
        metrics["write_ops"] = int(len(df_wrt))
        metrics["rows_written_avg"] = (
            float(
                pd.to_numeric(df_wrt["rows_written"], errors="coerce").dropna().mean()
            )
            if "rows_written" in df_wrt
            else None
        )
        metrics["errors_writer"] = (
            int((df_wrt["status"].fillna("").str.upper() == "ERROR").sum())
            if "status" in df_wrt
            else 0
        )
    else:
        metrics.update(dict(write_ops=0, rows_written_avg=None, errors_writer=0))

    return metrics


def log_integrity_check(
    inf_int: Dict[str, Any], wrt_int: Dict[str, Any]
) -> Dict[str, Any]:
    return {
        "inference_missing_fields": inf_int.get("missing_fields", 0),
        "writer_missing_fields": wrt_int.get("missing_fields", 0),
        "files": {
            "inference": inf_int.get("files", []),
            "writer": wrt_int.get("files", []),
        },
    }


def compose_monthly_summary(month: str, sparklen: int) -> Dict[str, Any]:
    """month = 'YYYYMM' (e.g., '202510')."""
    inf_pat = os.path.join(LOG_DIR, f"mtcr_review_assistant_{month}.jsonl")
    wrt_pat = os.path.join(LOG_DIR, "mtcr_writer.jsonl")  # adjust if rotated monthly

    df_inf, inf_int = summarize_inference_logs(inf_pat)
    df_wrt, wrt_int = summarize_writer_logs(wrt_pat)
    metrics = aggregate_metrics(df_inf, df_wrt, sparklen=sparklen)
    integrity = log_integrity_check(inf_int, wrt_int)

    now = datetime.utcnow().isoformat() + "Z"
    return {
        "month": month,
        "generated_at_utc": now,
        "metrics": metrics,
        "integrity": integrity,
        "sop_context": {
            "correctly_filled_target_pct": 80,  # LLDC 029014 §4.3
            "dashboard_residual_target_pct": 2,  # LLDC 029014 §4.3
            "sampling_aql": 1.5,  # Attachment 2
        },
    }


# ---------- Save ----------
def save_summary_jsonl(data: Dict[str, Any], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with jsonlines.open(path, "w") as writer:
        writer.write(data)


def _row_for_csv(data: Dict[str, Any]) -> Dict[str, Any]:
    flat = {
        "month": data.get("month"),
        "generated_at_utc": data.get("generated_at_utc"),
        **{f"metric_{k}": v for k, v in data.get("metrics", {}).items()},
        "inf_missing_fields": data.get("integrity", {}).get("inference_missing_fields"),
        "wrt_missing_fields": data.get("integrity", {}).get("writer_missing_fields"),
    }
    return flat


def save_summary_csv(data: Dict[str, Any], path: str, append: bool = False) -> None:
    """
    Write row for the month. If append=True:
      - create file if missing
      - if month already exists, replace that row (de-duplicate by 'month')
      - otherwise append a new row
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    new_row = pd.DataFrame([_row_for_csv(data)])

    if not append or not os.path.exists(path):
        new_row.to_csv(path, index=False)
        return

    try:
        existing = pd.read_csv(path)
    except Exception:
        new_row.to_csv(path, index=False)
        return

    if "month" in existing.columns:
        # Convert both to string for comparison to handle int/string mismatch
        existing = existing[existing["month"].astype(str) != str(data.get("month"))]
    combined = pd.concat([existing, new_row], ignore_index=True)
    combined.to_csv(path, index=False)


# ---------- CLI ----------
def _parse_args(argv=None):
    p = argparse.ArgumentParser(
        prog="log_manager", description="MTCR Log Manager — monthly metrics"
    )
    p.add_argument("--month", required=True, help="YYYYMM (e.g., 202510)")
    p.add_argument(
        "--output_csv", default=os.path.join(LOG_DIR, "monthly_metrics_summary.csv")
    )
    p.add_argument(
        "--append",
        default="false",
        help="Append/update CSV row for the month (true/false).",
    )
    p.add_argument(
        "--sparklen",
        type=int,
        default=40,
        help="Max glyphs for confidence sparkline (downsample if exceeded).",
    )
    p.add_argument(
        "--output_jsonl",
        default=None,
        help="Optional path like logs/metrics_summary_YYYYMM.jsonl",
    )
    p.add_argument("--verbose", default="false")
    return p.parse_args(argv)


def main(argv=None):
    args = _parse_args(argv)
    summary = compose_monthly_summary(args.month, sparklen=int(args.sparklen))
    jsonl_path = args.output_jsonl or os.path.join(
        LOG_DIR, f"metrics_summary_{args.month}.jsonl"
    )
    save_summary_jsonl(summary, jsonl_path)
    save_summary_csv(
        summary,
        args.output_csv,
        append=str(args.append).lower() in ("1", "true", "yes", "y"),
    )
    if str(args.verbose).lower() in ("1", "true", "yes", "y"):
        print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
