# ⚠️ Compliance Notice:
# Assistive mode only. Do NOT overwrite validated cells/ranges in the source workbook.
# This module reads AI inference logs and writes ONLY new versioned outputs:
#   /data/taxonomy/reasons.vN.yml, reasons.latest.yml
#   /logs/taxonomy_drift_YYYYMM.csv
#   /logs/taxonomy_changes.jsonl
# Maintain traceability: input months, counts, timestamps, file checksums (SHA256).

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple, Iterable

import pandas as pd
from rapidfuzz import fuzz
import yaml

REASON_COL = "reason"  # from M2 schema
CONF_COL = "confidence"  # 0..1
MODEL_VER_COL = "model_version"  # optional in logs

NORMALIZE_RE = re.compile(r"[^\w\s]", flags=re.UNICODE)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_reason(s: str) -> str:
    s = s.strip().lower()
    s = NORMALIZE_RE.sub(" ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


@dataclass
class ReasonSample:
    raw: str
    norm: str
    conf: float
    month: str
    model_version: str | None = None


@dataclass
class Cluster:
    canonical: str = ""
    members: List[str] = field(default_factory=list)


def read_month_logs(months: List[str], logs_dir: Path) -> List[ReasonSample]:
    samples: List[ReasonSample] = []
    for m in months:
        fp = logs_dir / f"mtcr_review_assistant_{m}.jsonl"
        if not fp.exists():
            continue
        with fp.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                reason = (obj.get(REASON_COL) or "").strip()
                if not reason:
                    continue
                conf = float(obj.get(CONF_COL, 0.0))
                mv = obj.get(MODEL_VER_COL)
                samples.append(
                    ReasonSample(
                        raw=reason,
                        norm=normalize_reason(reason),
                        conf=conf,
                        month=m,
                        model_version=mv,
                    )
                )
    return samples


def cluster_reasons(
    samples: List[ReasonSample], threshold: int = 87
) -> Dict[str, List[str]]:
    """Return {canonical -> [aliases]} (aliases include canonical itself if variants exist)."""
    # Build buckets by normalized form first to avoid O(n^2) where obvious duplicates exist
    uniq_norms = {}
    for s in samples:
        uniq_norms.setdefault(s.norm, set()).add(s.raw)

    norms = list(uniq_norms.keys())
    parent = {i: i for i in range(len(norms))}

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[rj] = ri

    # Union by fuzzy similarity
    for i in range(len(norms)):
        for j in range(i + 1, len(norms)):
            score = fuzz.token_sort_ratio(norms[i], norms[j])
            if score >= threshold:
                union(i, j)

    # Gather clusters by root
    clusters: Dict[int, List[str]] = {}
    for idx, norm in enumerate(norms):
        r = find(idx)
        clusters.setdefault(r, []).append(norm)

    # Choose canonical per cluster using frequency -> avg confidence -> shortest length
    freq: Dict[str, int] = {}
    conf_sum: Dict[str, float] = {}
    for s in samples:
        freq[s.norm] = freq.get(s.norm, 0) + 1
        conf_sum[s.norm] = conf_sum.get(s.norm, 0.0) + float(s.conf or 0.0)

    result: Dict[str, List[str]] = {}
    for _, norm_list in clusters.items():

        def key_fn(n):
            return (
                freq.get(n, 0),
                conf_sum.get(n, 0.0) / max(freq.get(n, 1), 1),
                -len(n),
            )

        canon_norm = sorted(norm_list, key=key_fn, reverse=True)[0]
        # collect all raw variants under the norms in this cluster
        alias_raws = []
        for n in norm_list:
            alias_raws.extend(sorted(uniq_norms[n]))
        # ensure stable order & uniqueness
        seen = set()
        ordered_aliases = [a for a in alias_raws if (a not in seen and not seen.add(a))]
        result[canon_norm] = ordered_aliases
    return result


def build_yaml_payload(
    canon_to_aliases: Dict[str, List[str]], samples: List[ReasonSample]
) -> dict:
    # compute metrics
    df = pd.DataFrame(
        [
            {"norm": s.norm, "raw": s.raw, "conf": s.conf, "month": s.month}
            for s in samples
        ]
    )
    items = []
    for canon_norm, aliases in canon_to_aliases.items():
        sub = df[df["norm"].isin([normalize_reason(a) for a in aliases])]
        items.append(
            {
                "canonical": (
                    aliases[0] if aliases else canon_norm
                ),  # present best raw for canon
                "canonical_norm": canon_norm,
                "aliases": sorted(set(aliases) - {aliases[0]}),
                "metrics": {
                    "count": int(len(sub)),
                    "avg_conf": float(sub["conf"].mean()) if len(sub) else 0.0,
                    "months": sorted(sub["month"].unique().tolist()),
                },
            }
        )
    # stable sort by descending count then canonical alpha
    items.sort(
        key=lambda x: (x["metrics"]["count"], x["canonical"].lower()), reverse=True
    )
    return {
        "schema": "mtcr.taxonomy.reasons/1-0-0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "items": items,
    }


def load_latest_yaml(path_latest: Path) -> dict | None:
    if not path_latest.exists():
        return None
    with path_latest.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def yaml_content_hash(payload: dict) -> str:
    # dump canonical with sorted keys for stable hash
    text = yaml.safe_dump(payload, sort_keys=True, allow_unicode=True)
    return sha256_text(text)


def write_versioned_yaml(payload: dict, out_latest: Path) -> Tuple[Path, str, int]:
    out_dir = out_latest.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    # detect next version
    existing = sorted(out_dir.glob("reasons.v*.yml"))
    next_v = 1
    if existing:
        max_v = max(int(p.stem.split("v")[-1]) for p in existing if "v" in p.stem)
        next_v = max_v + 1
    versioned = out_dir / f"reasons.v{next_v}.yml"
    # add header comment with checksum
    text = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
    checksum = sha256_text(text)
    header = f"# file_checksum_sha256: {checksum}\n"
    versioned.write_text(header + text, encoding="utf-8")
    out_latest.write_text(header + text, encoding="utf-8")
    return versioned, checksum, next_v


def diff_taxonomies(old: dict | None, new: dict) -> List[dict]:
    # naive diff at alias level per canonical_norm
    changes = []
    old_map = {}
    if old:
        for it in old.get("items", []):
            old_map[it["canonical_norm"]] = set(
                [it["canonical"], *it.get("aliases", [])]
            )
    for it in new.get("items", []):
        cn = it["canonical_norm"]
        new_set = set([it["canonical"], *it.get("aliases", [])])
        if cn not in old_map:
            changes.append({"action": "new_canonical", "canonical": it["canonical"]})
        else:
            added = sorted(new_set - old_map[cn])
            removed = sorted(old_map[cn] - new_set)
            for a in added:
                changes.append(
                    {"action": "added_alias", "canonical": it["canonical"], "alias": a}
                )
            for a in removed:
                changes.append(
                    {
                        "action": "removed_alias",
                        "canonical": it["canonical"],
                        "alias": a,
                    }
                )
    return changes


def write_drift_csv(
    month: str,
    canon_to_aliases: Dict[str, List[str]],
    samples: List[ReasonSample],
    out_csv: Path,
    input_checksums: Dict[str, str],
):
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(
        [
            {"alias": s.raw, "norm": s.norm, "conf": s.conf, "month": s.month}
            for s in samples
            if s.month == month
        ]
    )
    rows = []
    total = len(df)
    for canon_norm, aliases in canon_to_aliases.items():
        for alias in aliases:
            sub = df[df["alias"] == alias]
            if sub.empty:
                continue
            count = int(len(sub))
            share = round(100.0 * count / max(total, 1), 2)
            rows.append(
                {
                    "month": month,
                    "alias": alias,
                    "canonical_norm": canon_norm,
                    "count": count,
                    "share_pct": share,
                    "avg_conf": float(sub["conf"].mean()),
                }
            )
    meta = "# input_checksums=" + json.dumps(input_checksums)
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        f.write(meta + "\n")
        pd.DataFrame(rows).to_csv(f, index=False)


def append_changes_log(
    changes: List[dict], out_jsonl: Path, append: bool, context: dict
):
    if not append or not changes:
        return
    out_jsonl.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).isoformat()
    with out_jsonl.open("a", encoding="utf-8") as f:
        for ch in changes:
            rec = {"ts": ts, **context, **ch}
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="taxonomy_manager",
        description="Excel Review Action Taxonomy Manager",
    )
    p.add_argument("--months", nargs="+", required=True)
    p.add_argument("--fuzzy_threshold", type=int, default=87)
    p.add_argument(
        "--output_yaml", type=Path, default=Path("data/taxonomy/reasons.latest.yml")
    )
    p.add_argument("--drift_csv", type=Path, required=True)
    p.add_argument(
        "--changes_jsonl", type=Path, default=Path("logs/taxonomy_changes.jsonl")
    )
    p.add_argument("--append", type=lambda x: str(x).lower() != "false", default=True)
    p.add_argument("--dry_run", type=lambda x: str(x).lower() == "true", default=False)
    p.add_argument("--verbose", type=lambda x: str(x).lower() == "true", default=False)
    p.add_argument("--logs_dir", type=Path, default=Path("logs"))
    args = p.parse_args(argv)

    samples = read_month_logs(args.months, args.logs_dir)
    if not samples:
        print("No samples found for given months.", file=sys.stderr)
        return 1

    input_checksums = {}
    for m in args.months:
        fp = args.logs_dir / f"mtcr_review_assistant_{m}.jsonl"
        if fp.exists():
            input_checksums[m] = sha256_file(fp)

    clusters = cluster_reasons(samples, args.fuzzy_threshold)
    payload = build_yaml_payload(clusters, samples)

    old_latest = load_latest_yaml(args.output_yaml)
    changed = yaml_content_hash(old_latest or {}) != yaml_content_hash(payload)

    if args.verbose:
        print(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True))

    if not args.dry_run:
        if changed:
            versioned_path, out_checksum, vnum = write_versioned_yaml(
                payload, args.output_yaml
            )
        else:
            # mirror latest write to embed checksum header even if unchanged
            text = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
            out_checksum = sha256_text(text)
            header = f"# file_checksum_sha256: {out_checksum}\n"
            args.output_yaml.parent.mkdir(parents=True, exist_ok=True)
            args.output_yaml.write_text(header + text, encoding="utf-8")
            versioned_path, vnum = None, None

        # Drift per requested month (write one CSV per invocation param)
        write_drift_csv(
            args.months[-1], clusters, samples, args.drift_csv, input_checksums
        )

        # Changes log (append)
        diffs = diff_taxonomies(old_latest, payload)
        ctx = {
            "fuzzy_threshold": args.fuzzy_threshold,
            "input_checksums": input_checksums,
            "output_checksum": out_checksum,
            "months": args.months,
        }
        append_changes_log(diffs, args.changes_jsonl, args.append, ctx)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
