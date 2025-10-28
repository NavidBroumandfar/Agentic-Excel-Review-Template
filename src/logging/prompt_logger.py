"""
Helper for writing dev events to docs/prompts/log.jsonl
"""
from __future__ import annotations
import os, json, datetime
from typing import Iterable

LOG_PATH = os.path.join("docs", "prompts", "log.jsonl")

def append_event(module: str, title: str, summary: str, files: Iterable[str] = ()):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    entry = {
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "module": module,
        "title": title,
        "summary": summary,
        "files": list(files)
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry