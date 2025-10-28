import os, jsonlines, tempfile, shutil, pandas as pd
from src.logging.log_manager import (
    compose_monthly_summary,
    save_summary_csv,
    make_sparkline,
)


def _write_jsonl(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with jsonlines.open(path, "w") as w:
        for r in rows:
            w.write(r)


def test_compose_append_and_sparklen():
    cwd = os.getcwd()
    tmp = tempfile.mkdtemp()
    try:
        os.chdir(tmp)
        os.makedirs("logs", exist_ok=True)

        # Mock inference (3 confidence points) + writer logs
        _write_jsonl(
            "logs/mtcr_review_assistant_202510.jsonl",
            [
                {
                    "ts": "2025-10-01T10:00:00Z",
                    "model_version": "llama3-8b-ft-v0.1",
                    "confidence": 0.82,
                    "reason": "Wrong Error Code",
                    "run_id": "r1",
                    "row_id": 1,
                },
                {
                    "ts": "2025-10-02T10:00:00Z",
                    "model_version": "llama3-8b-ft-v0.1",
                    "confidence": 0.91,
                    "reason": "Catalog Profile mismatch",
                    "run_id": "r1",
                    "row_id": 2,
                },
                {
                    "ts": "2025-10-03T10:00:00Z",
                    "model_version": "llama3-8b-ft-v0.1",
                    "confidence": 0.77,
                    "reason": "Incomplete fields",
                    "run_id": "r2",
                    "row_id": 3,
                },
            ],
        )
        _write_jsonl(
            "logs/mtcr_writer.jsonl",
            [
                {
                    "ts": "2025-10-01T10:05:00Z",
                    "run_id": "r1",
                    "rows_written": 2,
                    "status": "OK",
                }
            ],
        )

        # Compose with sparklen=2 (forces downsample to 2 glyphs)
        s1 = compose_monthly_summary("202510", sparklen=2)
        spark = s1["metrics"]["confidence_sparkline"]
        assert isinstance(spark, str) and len(spark) == 2

        # Save CSV without append (overwrite)
        save_summary_csv(s1, "logs/monthly_metrics_summary.csv", append=False)
        assert os.path.exists("logs/monthly_metrics_summary.csv")

        # Update writer logs, recompute and append (should replace month row)
        _write_jsonl(
            "logs/mtcr_writer.jsonl",
            [
                {
                    "ts": "2025-10-01T10:05:00Z",
                    "run_id": "r1",
                    "rows_written": 2,
                    "status": "OK",
                },
                {
                    "ts": "2025-10-04T12:00:00Z",
                    "run_id": "r2",
                    "rows_written": 1,
                    "status": "OK",
                },
            ],
        )
        s2 = compose_monthly_summary("202510", sparklen=40)
        save_summary_csv(s2, "logs/monthly_metrics_summary.csv", append=True)

        df = pd.read_csv("logs/monthly_metrics_summary.csv")
        # Convert month to string for comparison since pandas might read it as int
        month_values = df["month"].astype(str).tolist()
        assert month_values.count("202510") == 1

        # Direct sparkline function test with many points
        long_vals = [i % 100 for i in range(100)]
        sl = make_sparkline(long_vals, max_len=10)
        assert isinstance(sl, str) and 1 <= len(sl) <= 10
    finally:
        os.chdir(cwd)
        shutil.rmtree(tmp, ignore_errors=True)
