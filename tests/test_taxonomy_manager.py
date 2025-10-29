import json
from pathlib import Path
import subprocess
import sys
import yaml
import pytest


def write_jsonl(p: Path, rows: list[dict]):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def run_cli(args, cwd: Path):
    cmd = [sys.executable, "-m", "src.utils.taxonomy_manager", *args]
    return subprocess.run(cmd, cwd=cwd, check=False, capture_output=True, text=True)


def test_taxonomy_end_to_end(tmp_path: Path):
    """Test complete end-to-end workflow with clustering and versioning."""
    # Arrange
    logs = tmp_path / "logs"
    write_jsonl(
        logs / "mtcr_review_assistant_202510.jsonl",
        [
            {"reason": "Wrong Error Code", "confidence": 0.72},
            {"reason": "Error code incorrect", "confidence": 0.8},
            {"reason": "Incorrect error-code", "confidence": 0.7},
            {"reason": "Wrong   error  code", "confidence": 0.75},
        ],
    )

    # Act
    args = [
        "--months",
        "202510",
        "--fuzzy_threshold",
        "87",
        "--output_yaml",
        "data/taxonomy/reasons.latest.yml",
        "--drift_csv",
        "logs/taxonomy_drift_202510.csv",
        "--changes_jsonl",
        "logs/taxonomy_changes.jsonl",
        "--append",
        "true",
        "--dry_run",
        "false",
        "--verbose",
        "false",
        "--logs_dir",
        str(logs),
    ]
    r = run_cli(args, tmp_path)
    assert r.returncode == 0, f"CLI failed: {r.stderr}"

    # Assert YAML exists and structure looks right
    latest = tmp_path / "data/taxonomy/reasons.latest.yml"
    assert latest.exists()
    data = yaml.safe_load(latest.read_text(encoding="utf-8"))
    items = data.get("items", [])
    assert len(items) == 1
    assert "canonical" in items[0]
    assert items[0]["aliases"]  # has some aliases
    assert "metrics" in items[0]
    assert items[0]["metrics"]["count"] == 4

    # Drift CSV
    drift = tmp_path / "logs/taxonomy_drift_202510.csv"
    assert drift.exists()
    txt = drift.read_text(encoding="utf-8")
    assert "alias,canonical_norm,count,share_pct,avg_conf" in txt
    assert "Wrong Error Code" in txt

    # Changes log appended
    changes = tmp_path / "logs/taxonomy_changes.jsonl"
    assert changes.exists()
    assert changes.read_text(encoding="utf-8").strip() != ""


def test_version_bump_on_new_variant(tmp_path: Path):
    """Test that adding a new variant creates a new version."""
    # Arrange - initial run
    logs = tmp_path / "logs"
    write_jsonl(
        logs / "mtcr_review_assistant_202510.jsonl",
        [
            {"reason": "Wrong Error Code", "confidence": 0.72},
            {"reason": "Error code incorrect", "confidence": 0.8},
        ],
    )

    args = [
        "--months",
        "202510",
        "--fuzzy_threshold",
        "87",
        "--output_yaml",
        "data/taxonomy/reasons.latest.yml",
        "--drift_csv",
        "logs/taxonomy_drift_202510.csv",
        "--changes_jsonl",
        "logs/taxonomy_changes.jsonl",
        "--append",
        "true",
        "--dry_run",
        "false",
        "--verbose",
        "false",
        "--logs_dir",
        str(logs),
    ]

    # First run
    r1 = run_cli(args, tmp_path)
    assert r1.returncode == 0

    # Add new variant
    with (logs / "mtcr_review_assistant_202510.jsonl").open("a", encoding="utf-8") as f:
        f.write(
            json.dumps({"reason": "Error code is wrong", "confidence": 0.77}) + "\n"
        )

    # Second run
    r2 = run_cli(args, tmp_path)
    assert r2.returncode == 0

    # Check that a new versioned file was created
    versions = sorted((tmp_path / "data/taxonomy").glob("reasons.v*.yml"))
    assert len(versions) >= 1


def test_dry_run_produces_no_files(tmp_path: Path):
    """Test that dry run mode doesn't create any output files."""
    logs = tmp_path / "logs"
    write_jsonl(
        logs / "mtcr_review_assistant_202510.jsonl",
        [
            {"reason": "Wrong Error Code", "confidence": 0.72},
        ],
    )

    args = [
        "--months",
        "202510",
        "--fuzzy_threshold",
        "87",
        "--output_yaml",
        "data/taxonomy/reasons.latest.yml",
        "--drift_csv",
        "logs/taxonomy_drift_202510.csv",
        "--changes_jsonl",
        "logs/taxonomy_changes.jsonl",
        "--append",
        "true",
        "--dry_run",
        "true",  # dry run mode
        "--verbose",
        "false",
        "--logs_dir",
        str(logs),
    ]

    r = run_cli(args, tmp_path)
    assert r.returncode == 0

    # No files should be created
    assert not (tmp_path / "data/taxonomy/reasons.latest.yml").exists()
    assert not (tmp_path / "logs/taxonomy_drift_202510.csv").exists()
    assert not (tmp_path / "logs/taxonomy_changes.jsonl").exists()


def test_fuzzy_threshold_splits_clusters(tmp_path: Path):
    """Test that higher fuzzy threshold causes separate clusters."""
    logs = tmp_path / "logs"
    write_jsonl(
        logs / "mtcr_review_assistant_202510.jsonl",
        [
            {"reason": "Wrong Error Code", "confidence": 0.72},
            {"reason": "Error code incorrect", "confidence": 0.8},
            {"reason": "Missing documentation", "confidence": 0.7},
            {"reason": "Documentation missing", "confidence": 0.75},
        ],
    )

    # Low threshold should cluster similar items together
    args_low = [
        "--months",
        "202510",
        "--fuzzy_threshold",
        "50",  # low threshold
        "--output_yaml",
        "data/taxonomy/reasons.latest.yml",
        "--drift_csv",
        "logs/taxonomy_drift_202510.csv",
        "--changes_jsonl",
        "logs/taxonomy_changes.jsonl",
        "--append",
        "true",
        "--dry_run",
        "false",
        "--verbose",
        "false",
        "--logs_dir",
        str(logs),
    ]

    r1 = run_cli(args_low, tmp_path)
    assert r1.returncode == 0

    data_low = yaml.safe_load(
        (tmp_path / "data/taxonomy/reasons.latest.yml").read_text()
    )
    items_low = data_low.get("items", [])

    # High threshold should keep them separate
    args_high = [
        "--months",
        "202510",
        "--fuzzy_threshold",
        "95",  # high threshold
        "--output_yaml",
        "data/taxonomy/reasons_high.yml",
        "--drift_csv",
        "logs/taxonomy_drift_high.csv",
        "--changes_jsonl",
        "logs/taxonomy_changes_high.jsonl",
        "--append",
        "true",
        "--dry_run",
        "false",
        "--verbose",
        "false",
        "--logs_dir",
        str(logs),
    ]

    r2 = run_cli(args_high, tmp_path)
    assert r2.returncode == 0

    data_high = yaml.safe_load(
        (tmp_path / "data/taxonomy/reasons_high.yml").read_text()
    )
    items_high = data_high.get("items", [])

    # High threshold should produce more clusters (or same if already different enough)
    assert len(items_high) >= len(items_low)


def test_checksum_traceability(tmp_path: Path):
    """Test that checksums are properly embedded in outputs."""
    logs = tmp_path / "logs"
    write_jsonl(
        logs / "mtcr_review_assistant_202510.jsonl",
        [
            {"reason": "Wrong Error Code", "confidence": 0.72},
        ],
    )

    args = [
        "--months",
        "202510",
        "--fuzzy_threshold",
        "87",
        "--output_yaml",
        "data/taxonomy/reasons.latest.yml",
        "--drift_csv",
        "logs/taxonomy_drift_202510.csv",
        "--changes_jsonl",
        "logs/taxonomy_changes.jsonl",
        "--append",
        "true",
        "--dry_run",
        "false",
        "--verbose",
        "false",
        "--logs_dir",
        str(logs),
    ]

    r = run_cli(args, tmp_path)
    assert r.returncode == 0

    # Check YAML has checksum header
    yaml_content = (tmp_path / "data/taxonomy/reasons.latest.yml").read_text()
    assert "# file_checksum_sha256:" in yaml_content

    # Check CSV has checksum metadata
    csv_content = (tmp_path / "logs/taxonomy_drift_202510.csv").read_text()
    assert "# input_checksums=" in csv_content

    # Check JSONL has checksum context
    jsonl_content = (tmp_path / "logs/taxonomy_changes.jsonl").read_text()
    changes_data = [
        json.loads(line) for line in jsonl_content.strip().split("\n") if line
    ]
    assert len(changes_data) > 0
    assert "input_checksums" in changes_data[0]
    assert "output_checksum" in changes_data[0]


def test_empty_input_handling(tmp_path: Path):
    """Test handling of empty or missing input files."""
    logs = tmp_path / "logs"
    logs.mkdir(parents=True, exist_ok=True)

    # Test with non-existent file
    args = [
        "--months",
        "202510",
        "--fuzzy_threshold",
        "87",
        "--output_yaml",
        "data/taxonomy/reasons.latest.yml",
        "--drift_csv",
        "logs/taxonomy_drift_202510.csv",
        "--changes_jsonl",
        "logs/taxonomy_changes.jsonl",
        "--append",
        "true",
        "--dry_run",
        "false",
        "--verbose",
        "false",
        "--logs_dir",
        str(logs),
    ]

    r = run_cli(args, tmp_path)
    assert r.returncode == 1  # Should fail with no samples
    assert "No samples found" in r.stderr


def test_multiple_months(tmp_path: Path):
    """Test processing multiple months of data."""
    logs = tmp_path / "logs"
    write_jsonl(
        logs / "mtcr_review_assistant_202510.jsonl",
        [
            {"reason": "Wrong Error Code", "confidence": 0.72},
        ],
    )
    write_jsonl(
        logs / "mtcr_review_assistant_202511.jsonl",
        [
            {"reason": "Error code incorrect", "confidence": 0.8},
        ],
    )

    args = [
        "--months",
        "202510",
        "202511",
        "--fuzzy_threshold",
        "87",
        "--output_yaml",
        "data/taxonomy/reasons.latest.yml",
        "--drift_csv",
        "logs/taxonomy_drift_202511.csv",  # drift for last month
        "--changes_jsonl",
        "logs/taxonomy_changes.jsonl",
        "--append",
        "true",
        "--dry_run",
        "false",
        "--verbose",
        "false",
        "--logs_dir",
        str(logs),
    ]

    r = run_cli(args, tmp_path)
    assert r.returncode == 0

    # Should have processed both months
    data = yaml.safe_load((tmp_path / "data/taxonomy/reasons.latest.yml").read_text())
    items = data.get("items", [])
    assert len(items) == 1  # Should cluster together
    assert "202510" in items[0]["metrics"]["months"]
    assert "202511" in items[0]["metrics"]["months"]


def test_confidence_and_frequency_ranking(tmp_path: Path):
    """Test that canonical selection prioritizes frequency, then confidence, then length."""
    logs = tmp_path / "logs"
    write_jsonl(
        logs / "mtcr_review_assistant_202510.jsonl",
        [
            {
                "reason": "Error code wrong",
                "confidence": 0.9,
            },  # High confidence but low frequency
            {
                "reason": "Wrong error code",
                "confidence": 0.7,
            },  # Lower confidence but higher frequency
            {"reason": "Wrong error code", "confidence": 0.7},  # Same as above
            {
                "reason": "Very long error code description that is wrong",
                "confidence": 0.8,
            },  # High confidence, medium frequency, but long
        ],
    )

    args = [
        "--months",
        "202510",
        "--fuzzy_threshold",
        "50",  # Low threshold to cluster them
        "--output_yaml",
        "data/taxonomy/reasons.latest.yml",
        "--drift_csv",
        "logs/taxonomy_drift_202510.csv",
        "--changes_jsonl",
        "logs/taxonomy_changes.jsonl",
        "--append",
        "true",
        "--dry_run",
        "false",
        "--verbose",
        "false",
        "--logs_dir",
        str(logs),
    ]

    r = run_cli(args, tmp_path)
    assert r.returncode == 0

    data = yaml.safe_load((tmp_path / "data/taxonomy/reasons.latest.yml").read_text())
    items = data.get("items", [])
    assert len(items) == 1

    # Should choose "Wrong error code" as canonical (highest frequency)
    canonical = items[0]["canonical"]
    assert "Wrong error code" in canonical or "wrong error code" in canonical.lower()
