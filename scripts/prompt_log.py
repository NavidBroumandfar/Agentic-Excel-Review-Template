#!/usr/bin/env python3
"""
Append an entry to docs/prompts/log.jsonl
Usage:
  python scripts/prompt_log.py --module M2 --title "Review Assistant skeleton" --summary "RAG+LLM scaffolding" --files src/ai/review_assistant.py ai/prompts/review_prompt.txt
"""
import argparse, json, os, sys, datetime

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--module", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--summary", required=True)
    p.add_argument("files", nargs="*")
    args = p.parse_args()

    entry = {
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "module": args.module,
        "title": args.title,
        "summary": args.summary,
        "files": args.files
    }
    log_path = os.path.join("docs", "prompts", "log.jsonl")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print("[OK] Logged:", entry)

if __name__ == "__main__":
    sys.exit(main())