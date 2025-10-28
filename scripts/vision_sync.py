#!/usr/bin/env python3
"""
VisionSync — Update ProjectVision.ts and write a snapshot.
Usage:
  python scripts/vision_sync.py --phase M2 --status active --note "Kick off AI Review Assistant"
"""
import argparse, datetime, re, os, sys

VISION_PATH = os.path.join("src","context","ProjectVision.ts")
SNAPSHOT_MD = os.path.join("docs","Project_Vision_Snapshot.md")

def read(path):
    with open(path,"r",encoding="utf-8") as f: return f.read()

def write(path, txt):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path,"w",encoding="utf-8") as f: f.write(txt)

def set_last_updated(ts_code: str) -> str:
    iso = datetime.datetime.utcnow().isoformat()+"Z"
    return re.sub(r'(lastUpdatedISO:\s*)(new Date\(\)\.toISOString\(\)|".*?")',
                  r'\1"'+iso+r'"', ts_code, count=1)

def update_phase_status(ts_code: str, phase_id: str, new_status: str) -> str:
    pattern = rf'(\{{\s*id:\s*"{re.escape(phase_id)}"[\s\S]*?status:\s*")(\w+)(")'
    return re.sub(pattern, rf'\1{new_status}\3', ts_code, count=1)

def append_changelog(ts_code: str, note: str) -> str:
    iso = datetime.datetime.utcnow().isoformat()+"Z"
    escaped_note = note.replace('"', '\\"')
    return re.sub(
        r'(changelog:\s*\[\s*)',
        rf'\1{{ dateISO: "{iso}", note: "{escaped_note}" }}, ',
        ts_code, count=1)

def extract_snapshot(ts_code: str) -> str:
    name = re.search(r'name:\s*"([^"]+)"', ts_code)
    phases = re.findall(r'\{[^{}]*id:\s*"([^"]+)"[^{}]*title:\s*"([^"]+)"[^{}]*status:\s*"([^"]+)"[^{}]*\}', ts_code)
    lines = [f"# Project Vision Snapshot — {name.group(1) if name else 'MTCR_Agentic_Automation'}", ""]
    lines += ["| Phase | Title | Status |", "|------|-------|--------|"]
    for pid, title, status in phases:
        lines.append(f"| {pid} | {title} | {status} |")
    return "\n".join(lines) + "\n"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", required=True)
    ap.add_argument("--status", required=True, choices=["planned","active","completed","blocked"])
    ap.add_argument("--note", required=True)
    args = ap.parse_args()

    ts = read(VISION_PATH)
    ts = update_phase_status(ts, args.phase, args.status)
    ts = set_last_updated(ts)
    ts = append_changelog(ts, args.note)
    write(VISION_PATH, ts)
    write(SNAPSHOT_MD, extract_snapshot(ts))
    print("[VisionSync] Updated:", args.phase, "→", args.status)

if __name__ == "__main__":
    sys.exit(main())
