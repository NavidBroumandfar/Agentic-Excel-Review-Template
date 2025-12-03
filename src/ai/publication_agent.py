# ⚠️ Compliance Notice:
# Assistive mode only. This module prepares draft HTML emails and logs QA metadata.
# It must NOT send emails or alter validated Excel/TWD/Tableau assets.
# New outputs go under /outputs/publication and /logs/.
from __future__ import annotations
import argparse, hashlib, json, os, sys, textwrap, glob
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional, Tuple, Dict, Any
import pandas as pd
from dateutil.relativedelta import relativedelta
from dateutil.parser import isoparse
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TEMPLATES_DIR = os.path.join(ROOT, "templates")
OUTPUT_DIR = os.path.join(ROOT, "outputs", "publication")
LOGS_DIR = os.path.join(ROOT, "logs")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

NORMALIZE_MAP = {
    "subsidiary": "subsidiary",
    "sub": "subsidiary",
    "country": "subsidiary",
    "total_reviewed": "total_reviewed",
    "reviewed": "total_reviewed",
    "count_reviewed": "total_reviewed",
    "total_correct": "total_correct",
    "correct": "total_correct",
    "match_rate": "match_rate",
    "match%": "match_rate",
    "match_rate_pct": "match_rate",
    "accuracy": "match_rate",
    "overrides_pct": "overrides_pct",
    "overrides%": "overrides_pct",
    "override_rate": "overrides_pct",
    "overridden%": "overrides_pct",
    "avg_ai_confidence": "avg_ai_confidence",
    "ai_confidence_avg": "avg_ai_confidence",
    "mean_confidence": "avg_ai_confidence",
}


@dataclass
class KpiRow:
    subsidiary: str
    total_reviewed: int
    total_correct: int
    match_rate: float  # 0..1 or 0..100 — we normalize to 0..1 internally
    overrides_pct: float  # normalized to 0..1
    avg_ai_confidence: float  # 0..1


@dataclass
class KpiSummary:
    month_label_en: str
    month_label_fr: str
    match_rate: float
    overrides_pct: float
    avg_ai_confidence: float
    total_reviewed: int
    total_correct: int


def _yyyymm_from_month_arg(month_str: str) -> str:
    # month_str accepts "YYYY-MM" or "YYYYMM" or full ISO date
    if "-" in month_str and len(month_str) == 7:
        return month_str.replace("-", "")
    if len(month_str) == 6 and month_str.isdigit():
        return month_str
    dt = isoparse(month_str)
    return dt.strftime("%Y%m")


def _labels_from_yyyymm(yyyymm: str) -> Tuple[str, str]:
    dt = datetime.strptime(yyyymm, "%Y%m")
    month_en = dt.strftime("%B %Y")  # e.g., October 2025
    # French month names
    fr_map = {
        1: "janvier",
        2: "février",
        3: "mars",
        4: "avril",
        5: "mai",
        6: "juin",
        7: "juillet",
        8: "août",
        9: "septembre",
        10: "octobre",
        11: "novembre",
        12: "décembre",
    }
    month_fr = f"{fr_map[dt.month].capitalize()} {dt.year}"
    return month_en, month_fr


def _find_default_csv(yyyymm: str) -> Optional[str]:
    candidates = [
        os.path.join(ROOT, "outputs", "m8", f"correction_summary_{yyyymm}.csv"),
        os.path.join(ROOT, "outputs", f"correction_summary_{yyyymm}.csv"),
        os.path.join(ROOT, "data", "exports", f"correction_summary_{yyyymm}.csv"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    # try glob if someone renamed slightly
    g = glob.glob(os.path.join(ROOT, "**", f"*{yyyymm}*.csv"), recursive=True)
    for p in g:
        if "correction" in os.path.basename(p).lower():
            return p
    return None


def _normalize_headers(df: pd.DataFrame) -> pd.DataFrame:
    cols = {}
    for c in df.columns:
        key = c.strip().lower().replace(" ", "_").replace("-", "_")
        cols[c] = NORMALIZE_MAP.get(key, key)
    df = df.rename(columns=cols)
    # fill common missing columns with safe defaults
    for needed, default in [
        ("subsidiary", "Unknown"),
        ("total_reviewed", 0),
        ("total_correct", 0),
        ("match_rate", 0.0),
        ("overrides_pct", 0.0),
        ("avg_ai_confidence", 0.0),
    ]:
        if needed not in df.columns:
            df[needed] = default
    return df


def _to_unit_fraction(x):
    try:
        x = float(x)
    except Exception:
        return 0.0
    if x > 1.0:  # if passed 82 for 82%
        return x / 100.0
    return x


def load_kpis(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df = _normalize_headers(df)
    # normalize percent-ish columns
    df["match_rate"] = df["match_rate"].map(_to_unit_fraction)
    df["overrides_pct"] = df["overrides_pct"].map(_to_unit_fraction)
    df["avg_ai_confidence"] = df["avg_ai_confidence"].map(_to_unit_fraction)
    # numeric ints
    for c in ["total_reviewed", "total_correct"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
    return df


def summarize(
    df: pd.DataFrame, month_en: str, month_fr: str
) -> Tuple[KpiSummary, pd.DataFrame]:
    total_reviewed = int(df["total_reviewed"].sum())
    total_correct = int(df["total_correct"].sum())
    match_rate = (total_correct / total_reviewed) if total_reviewed > 0 else 0.0
    overrides_pct = float(
        (df["overrides_pct"] * df["total_reviewed"]).sum() / max(total_reviewed, 1)
    )
    avg_conf = float(
        (df["avg_ai_confidence"] * df["total_reviewed"]).sum() / max(total_reviewed, 1)
    )

    summary = KpiSummary(
        month_label_en=month_en,
        month_label_fr=month_fr,
        match_rate=match_rate,
        overrides_pct=overrides_pct,
        avg_ai_confidence=avg_conf,
        total_reviewed=total_reviewed,
        total_correct=total_correct,
    )
    # per-subsidiary table
    table = df.copy()
    table = table[
        [
            "subsidiary",
            "total_reviewed",
            "total_correct",
            "match_rate",
            "overrides_pct",
            "avg_ai_confidence",
        ]
    ]
    table = table.sort_values(by=["subsidiary"]).reset_index(drop=True)
    return summary, table


def compare(prev: KpiSummary, curr: KpiSummary) -> Dict[str, Any]:
    def delta(a, b):
        return b - a

    def arrow(x):
        return "▲" if x > 0 else ("▼" if x < 0 else "→")

    dm = delta(prev.match_rate, curr.match_rate)
    do = delta(prev.overrides_pct, curr.overrides_pct)
    dc = delta(prev.avg_ai_confidence, curr.avg_ai_confidence)
    return {
        "match_rate_delta": dm,
        "match_rate_arrow": arrow(dm),
        "overrides_delta": do,
        "overrides_arrow": arrow(do),
        "confidence_delta": dc,
        "confidence_arrow": arrow(dc),
    }


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _env():
    return Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(enabled_extensions=("html",)),
    )


def render_email(locale: str, context: Dict[str, Any]) -> str:
    template_name = (
        "email_publication_fr.html"
        if locale.lower().startswith("fr")
        else "email_publication_en.html"
    )
    env = _env()
    tpl = env.get_template(template_name)
    return tpl.render(**context)


def write_outputs(yyyymm: str, en_html: str, fr_html: str) -> Dict[str, str]:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    en_path = os.path.join(OUTPUT_DIR, f"publication_email_{yyyymm}_en.html")
    fr_path = os.path.join(OUTPUT_DIR, f"publication_email_{yyyymm}_fr.html")
    bi_path = os.path.join(OUTPUT_DIR, f"publication_email_{yyyymm}_bilingual.html")
    with open(en_path, "w", encoding="utf-8") as f:
        f.write(en_html)
    with open(fr_path, "w", encoding="utf-8") as f:
        f.write(fr_html)
    with open(bi_path, "w", encoding="utf-8") as f:
        f.write("<hr/>".join([en_html, fr_html]))
    return {"en": en_path, "fr": fr_path, "bi": bi_path}


def log_jsonl(yyyymm: str, reviewer: str, files: Dict[str, str], meta: Dict[str, Any]):
    log_path = os.path.join(LOGS_DIR, f"publication_agent_{yyyymm}.jsonl")
    record = {
        "module": "M9_PublicationAgent",
        "month": yyyymm,
        "reviewer": reviewer,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "outputs": files,
        "sha256": {
            k: _sha256_text(open(v, "r", encoding="utf-8").read())
            for k, v in files.items()
        },
        "metadata": meta,
        "model_version": "N/A (formatting only)",
        "assistive_mode": True,
    }
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"[M9] Log appended -> {log_path}")


def discover_inputs(
    yyyymm: str, csv: Optional[str], prev_csv: Optional[str]
) -> Tuple[str, Optional[str]]:
    csv_path = csv or _find_default_csv(yyyymm)
    if not csv_path or not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"Could not locate current CSV for {yyyymm}. Pass --csv explicitly."
        )
    prev_yyyymm = (
        datetime.strptime(yyyymm, "%Y%m") - relativedelta(months=1)
    ).strftime("%Y%m")
    prev_path = prev_csv or _find_default_csv(prev_yyyymm)
    return csv_path, prev_path


def main():
    ap = argparse.ArgumentParser(
        description="M9 Publication Agent — generate bilingual HTML draft"
    )
    ap.add_argument("--month", required=True, help="Target month (YYYY-MM or YYYYMM)")
    ap.add_argument(
        "--reviewer", required=True, help="Reviewer/Preparer name (for QA log)"
    )
    ap.add_argument("--csv", help="Path to current month CSV")
    ap.add_argument("--prev-csv", help="Path to previous month CSV")
    args = ap.parse_args()

    yyyymm = _yyyymm_from_month_arg(args.month)
    month_en, month_fr = _labels_from_yyyymm(yyyymm)

    csv_path, prev_path = discover_inputs(yyyymm, args.csv, args.prev_csv)
    curr_df = load_kpis(csv_path)
    curr_summary, curr_table = summarize(curr_df, month_en, month_fr)

    if prev_path and os.path.exists(prev_path):
        prev_df = load_kpis(prev_path)
        prev_summary, _ = summarize(
            prev_df,
            *(
                _labels_from_yyyymm(
                    (
                        datetime.strptime(yyyymm, "%Y%m") - relativedelta(months=1)
                    ).strftime("%Y%m")
                )
            ),
        )
        deltas = compare(prev_summary, curr_summary)
    else:
        deltas = {
            "match_rate_delta": None,
            "match_rate_arrow": "→",
            "overrides_delta": None,
            "overrides_arrow": "→",
            "confidence_delta": None,
            "confidence_arrow": "→",
        }

    # prepare context shared
    def pct(x):
        if x is None:
            return "N/A"
        return f"{x*100:.0f}%"

    def pct1(x):
        if x is None:
            return "N/A"
        return f"{x*100:.1f}%"

    context_common = {
        "month_en": month_en,
        "month_fr": month_fr,
        "match_rate": pct1(curr_summary.match_rate),
        "overrides_pct": pct1(curr_summary.overrides_pct),
        "avg_ai_confidence": f"{curr_summary.avg_ai_confidence:.2f}",
        "total_reviewed": curr_summary.total_reviewed,
        "total_correct": curr_summary.total_correct,
        "delta_match": (
            f"{deltas['match_rate_arrow']} {pct(deltas['match_rate_delta']) if deltas['match_rate_delta'] is not None else '—'}"
            if deltas["match_rate_delta"] is not None
            else "—"
        ),
        "delta_overrides": (
            f"{deltas['overrides_arrow']} {pct(deltas['overrides_delta']) if deltas['overrides_delta'] is not None else '—'}"
            if deltas["overrides_delta"] is not None
            else "—"
        ),
        "delta_conf": (
            f"{deltas['confidence_arrow']} {pct1(deltas['confidence_delta']) if deltas['confidence_delta'] is not None else '—'}"
            if deltas["confidence_delta"] is not None
            else "—"
        ),
        "subsidiary_rows": [
            {
                "subsidiary": r["subsidiary"],
                "total_reviewed": int(r["total_reviewed"]),
                "total_correct": int(r["total_correct"]),
                "match_rate": pct1(float(r["match_rate"])),
                "overrides_pct": pct1(float(r["overrides_pct"])),
                "avg_ai_confidence": f"{float(r['avg_ai_confidence']):.2f}",
            }
            for _, r in curr_table.iterrows()
        ],
        "subject_en": f"Monthly Review Summary — {month_en}",
        "subject_fr": f"Résumé Mensuel — {month_fr}",
        "attachment_csv": os.path.relpath(csv_path, ROOT),
        "attachment_prev_csv": os.path.relpath(prev_path, ROOT) if prev_path else None,
    }

    en_html = render_email("en", context_common)
    fr_html = render_email("fr", context_common)
    files = write_outputs(yyyymm, en_html, fr_html)

    log_jsonl(
        yyyymm,
        args.reviewer,
        files,
        meta={
            "inputs": {
                "current_csv": os.path.relpath(csv_path, ROOT),
                "previous_csv": os.path.relpath(prev_path, ROOT) if prev_path else None,
            },
            "kpi": asdict(curr_summary),
            "deltas": deltas,
            "assistive_only": True,
        },
    )

    print("[M9] Publication email drafts generated:")
    for k, v in files.items():
        print(f" - {k}: {os.path.relpath(v, ROOT)}")


if __name__ == "__main__":
    main()
