#!/usr/bin/env python3
"""
VisionSync — Update ProjectVision.ts and write a snapshot.
Usage:
  python scripts/vision_sync.py --phase M2 --status active --note "Kick off AI Review Assistant"
"""
import argparse, datetime, re, os, sys

VISION_PATH = os.path.join("src", "context", "ProjectVision.ts")
SNAPSHOT_MD = os.path.join("docs", "Project_Vision_Snapshot.md")


def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write(path, txt):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(txt)


def set_last_updated(ts_code: str) -> str:
    iso = datetime.datetime.utcnow().isoformat() + "Z"
    return re.sub(
        r'(lastUpdatedISO:\s*)(new Date\(\)\.toISOString\(\)|".*?")',
        r'\1"' + iso + r'"',
        ts_code,
        count=1,
    )


def update_phase_status(ts_code: str, phase_id: str, new_status: str) -> str:
    pattern = rf'(\{{\s*id:\s*"{re.escape(phase_id)}"[\s\S]*?status:\s*")(\w+)(")'
    return re.sub(pattern, rf"\1{new_status}\3", ts_code, count=1)


def append_changelog(ts_code: str, note: str) -> str:
    iso = datetime.datetime.utcnow().isoformat() + "Z"
    escaped_note = note.replace('"', '\\"')
    return re.sub(
        r"(changelog:\s*\[\s*)",
        rf'\1{{ dateISO: "{iso}", note: "{escaped_note}" }}, ',
        ts_code,
        count=1,
    )


def extract_snapshot(ts_code: str) -> str:
    name = re.search(r'name:\s*"([^"]+)"', ts_code)
    phases = re.findall(
        r'\{[^{}]*id:\s*"([^"]+)"[^{}]*title:\s*"([^"]+)"[^{}]*status:\s*"([^"]+)"[^{}]*\}',
        ts_code,
    )
    lines = [
        f"# Project Vision Snapshot — {name.group(1) if name else 'MTCR_Agentic_Automation'}",
        "",
    ]
    lines += ["| Phase | Title | Status |", "|------|-------|--------|"]
    for pid, title, status in phases:
        lines.append(f"| {pid} | {title} | {status} |")

    # Add sub-phases
    subphases = re.findall(
        r'id:\s*"([^"]+)"[\s\S]*?title:\s*"([^"]+)"[\s\S]*?status:\s*"([^"]+)"',
        ts_code,
    )
    if subphases:
        lines.append("")
        lines.append("### Sub-Phases")
        lines.append("| Phase | Title | Status |")
        lines.append("|------|-------|--------|")
        for pid, title, status in subphases:
            if "." in pid:  # Only show sub-phases
                lines.append(f"| {pid} | {title} | {status} |")

    return "\n".join(lines) + "\n"


def get_phase_mapping(ts_code: str) -> dict:
    """Extract all phases and sub-phases, return mapping to sequential module numbers"""
    mapping = {}
    module_num = 1
    
    # Extract all phases (main and sub) in order
    all_phases = re.findall(
        r'id:\s*"([^"]+)"[\s\S]*?title:\s*"([^"]+)"[\s\S]*?status:\s*"([^"]+)"',
        ts_code,
    )
    
    # Create a flat list with proper ordering: M1, M1.1, M1.2, M2, M2.1, etc.
    phase_list = []
    
    # Group phases by main phase
    main_phases = {}
    sub_phases = {}
    
    for phase_id, title, status in all_phases:
        if "." not in phase_id:  # Main phase
            main_phases[phase_id] = (phase_id, title, status)
        else:  # Sub-phase
            parent = phase_id.split('.')[0]
            if parent not in sub_phases:
                sub_phases[parent] = []
            sub_phases[parent].append((phase_id, title, status))
    
    # Sort main phases by number
    sorted_main = sorted(main_phases.items(), key=lambda x: int(x[0][1:]) if x[0][1:].isdigit() else 999)
    
    # Build final ordered list
    for main_id, (phase_id, title, status) in sorted_main:
        # Add main phase
        phase_list.append((phase_id, title, status))
        
        # Add its sub-phases if any
        if main_id in sub_phases:
            sorted_subs = sorted(sub_phases[main_id], key=lambda x: int(x[0].split('.')[1]) if x[0].split('.')[1].isdigit() else 999)
            phase_list.extend(sorted_subs)
    
    # Create mapping
    for phase_id, title, status in phase_list:
        mapping[phase_id] = {
            "module_num": module_num,
            "title": title,
            "status": status,
            "type": "main" if "." not in phase_id else "sub"
        }
        module_num += 1
    
    return mapping

def get_next_module_number(ts_code: str) -> int:
    """Get the next available module number"""
    mapping = get_phase_mapping(ts_code)
    if not mapping:
        return 1
    return max(info["module_num"] for info in mapping.values()) + 1

def create_module_file(phase_id: str, title: str, objective: str, module_num: int = None):
    """Create module-XX.txt file automatically with sequential numbering"""
    if module_num is None:
        # Read current vision to determine module number
        ts_code = read(VISION_PATH)
        mapping = get_phase_mapping(ts_code)
        if phase_id in mapping:
            module_num = mapping[phase_id]["module_num"]
        else:
            module_num = get_next_module_number(ts_code)
    
    module_file = os.path.join("docs", "prompts", f"module-{module_num:02d}.txt")
    content = f"""# Module {module_num:02d} — {phase_id}: {title}
Summary: {objective}

Phase: {phase_id}
Status: [To be updated via VisionSync]

Key files:
- [To be filled during development]

[Paste here the exact prompt used to generate {phase_id} with Cursor.]
"""
    write(module_file, content)
    print(f"[VisionSync] Created module file: {module_file} (Phase: {phase_id})")
    return module_file


def update_subphase_status(
    ts_code: str, phase_id: str, subphase_id: str, new_status: str
) -> str:
    """Update sub-phase status"""
    pattern = rf'(\{{\s*id:\s*"{re.escape(subphase_id)}"[\s\S]*?status:\s*")(\w+)(")'
    return re.sub(pattern, rf"\1{new_status}\3", ts_code, count=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", required=True)
    ap.add_argument(
        "--status", required=True, choices=["planned", "active", "completed", "blocked"]
    )
    ap.add_argument("--note", required=True)
    ap.add_argument(
        "--create-module", action="store_true", help="Auto-create module file"
    )
    args = ap.parse_args()

    ts = read(VISION_PATH)

    # Handle sub-phases (e.g., M1.1, M1.2)
    if "." in args.phase:
        ts = update_subphase_status(
            ts, args.phase.split(".")[0], args.phase, args.status
        )
    else:
        ts = update_phase_status(ts, args.phase, args.status)

    ts = set_last_updated(ts)
    ts = append_changelog(ts, args.note)
    write(VISION_PATH, ts)
    write(SNAPSHOT_MD, extract_snapshot(ts))

    # Auto-create module file if requested or if phase becomes active
    if args.create_module or args.status == "active":
        # Extract title and objective from the phase
        phase_match = re.search(
            rf'id:\s*"{re.escape(args.phase)}"[\s\S]*?title:\s*"([^"]+)"[\s\S]*?objective:\s*"([^"]+)"',
            ts,
        )
        if phase_match:
            title = phase_match.group(1)
            objective = phase_match.group(2)
            create_module_file(args.phase, title, objective)

    print("[VisionSync] Updated:", args.phase, "→", args.status)


if __name__ == "__main__":
    sys.exit(main())
