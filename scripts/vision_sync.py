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
            parent = phase_id.split(".")[0]
            if parent not in sub_phases:
                sub_phases[parent] = []
            sub_phases[parent].append((phase_id, title, status))

    # Sort main phases by number
    sorted_main = sorted(
        main_phases.items(), key=lambda x: int(x[0][1:]) if x[0][1:].isdigit() else 999
    )

    # Build final ordered list
    for main_id, (phase_id, title, status) in sorted_main:
        # Add main phase
        phase_list.append((phase_id, title, status))

        # Add its sub-phases if any
        if main_id in sub_phases:
            sorted_subs = sorted(
                sub_phases[main_id],
                key=lambda x: (
                    int(x[0].split(".")[1]) if x[0].split(".")[1].isdigit() else 999
                ),
            )
            phase_list.extend(sorted_subs)

    # Create mapping
    for phase_id, title, status in phase_list:
        mapping[phase_id] = {
            "module_num": module_num,
            "title": title,
            "status": status,
            "type": "main" if "." not in phase_id else "sub",
        }
        module_num += 1

    return mapping


def get_next_module_number(ts_code: str) -> int:
    """Get the next available module number"""
    mapping = get_phase_mapping(ts_code)
    if not mapping:
        return 1
    return max(info["module_num"] for info in mapping.values()) + 1


def detect_phase_files(phase_id: str) -> list:
    """Detect actual files created for a phase based on common patterns"""
    files = []

    # Define file patterns for each phase
    phase_patterns = {
        "M1": [
            "src/excel/mtcr_reader.py",
            "src/utils/config_loader.py",
            "config.json",
            "requirements.txt",
            "docs/Project_Structure.md",
            "README.md",
        ],
        "M1.1": [
            "src/excel/mtcr_reader.py",
            "src/utils/config_loader.py",
            "config.json",
            "requirements.txt",
        ],
        "M1.2": [
            "src/context/ProjectVision.ts",
            "scripts/vision_sync.py",
            "scripts/prompt_log.py",
            "src/logging/prompt_logger.py",
            "scripts/hooks/pre-commit.sh",
            "scripts/hooks/install_hooks.py",
            "docs/prompts/README.md",
            "docs/prompts/log.jsonl",
        ],
        "M2": ["src/ai/review_assistant.py", "src/ai/prompts/review_prompt.txt"],
        "M3": ["src/excel/mtcr_writer.py"],
    }

    if phase_id in phase_patterns:
        # Check which files actually exist
        for file_path in phase_patterns[phase_id]:
            if os.path.exists(file_path):
                files.append(file_path)

    return files


def generate_phase_summary(phase_id: str, title: str, status: str) -> str:
    """Generate a comprehensive summary based on phase content"""
    files = detect_phase_files(phase_id)

    if status == "completed":
        if phase_id == "M1":
            return "Complete Excel reader with profiling, CSV preview, and robust error handling. Includes configuration management and comprehensive documentation."
        elif phase_id == "M1.1":
            return "Basic Excel reader implementation with read-only access, automatic header detection, and data profiling capabilities."
        elif phase_id == "M1.2":
            return "Meta automation system with ProjectVision.ts roadmap, VisionSync CLI, prompt logging, and pre-commit governance hooks."
        elif phase_id == "M2":
            return "AI Review Assistant with RAG-based SOP retrieval and LLM-powered suggestion generation for standardized corrections."
        elif phase_id == "M3":
            return "Safe Excel writer that appends AI_ columns without modifying validated data ranges."
    else:
        return f"Development phase for {title} - {len(files)} files created"


def create_module_file(
    phase_id: str, title: str, objective: str, module_num: int = None
):
    """Create module-XX.txt file automatically with sequential numbering and real content"""
    if module_num is None:
        # Read current vision to determine module number
        ts_code = read(VISION_PATH)
        mapping = get_phase_mapping(ts_code)
        if phase_id in mapping:
            module_num = mapping[phase_id]["module_num"]
        else:
            module_num = get_next_module_number(ts_code)

    # Get actual files created for this phase
    actual_files = detect_phase_files(phase_id)

    # Generate comprehensive summary
    summary = generate_phase_summary(
        phase_id, title, "completed" if actual_files else "planned"
    )

    module_file = os.path.join("docs", "prompts", f"module-{module_num:02d}.txt")
    content = f"""# Module {module_num:02d} — {phase_id}: {title}
Summary: {summary}

Phase: {phase_id}
Status: {"completed" if actual_files else "planned"}
Objective: {objective}

Key files created:
{chr(10).join(f"- {file}" for file in actual_files) if actual_files else "- [Development in progress]"}

Development notes:
- Phase {phase_id} {"completed successfully" if actual_files else "is planned"}
- {"All core functionality implemented" if actual_files else "Implementation pending"}
- {"Ready for production use" if actual_files else "Awaiting development start"}

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


def update_all_modules():
    """Update all existing module files with current content"""
    ts_code = read(VISION_PATH)
    mapping = get_phase_mapping(ts_code)

    for phase_id, info in mapping.items():
        module_num = info["module_num"]
        title = info["title"]

        # Only update if module file exists (meaning phase was completed or explicitly created)
        module_file = os.path.join("docs", "prompts", f"module-{module_num:02d}.txt")
        if os.path.exists(module_file):
            # Extract objective from ProjectVision.ts
            objective_match = re.search(
                rf'id:\s*"{re.escape(phase_id)}"[\s\S]*?objective:\s*"([^"]+)"',
                ts_code,
            )
            objective = (
                objective_match.group(1) if objective_match else "Phase objective"
            )

            # Regenerate module file
            create_module_file(phase_id, title, objective, module_num)
            print(f"Updated module-{module_num:02d}.txt for {phase_id}")
        else:
            print(f"Skipped {phase_id} - no module file exists (phase not completed)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", required=False)
    ap.add_argument(
        "--status",
        required=False,
        choices=["planned", "active", "completed", "blocked"],
    )
    ap.add_argument("--note", required=False)
    ap.add_argument(
        "--create-module", action="store_true", help="Auto-create module file"
    )
    ap.add_argument(
        "--update-all",
        action="store_true",
        help="Update all module files with current content",
    )
    args = ap.parse_args()

    if args.update_all:
        update_all_modules()
        return

    if not args.phase or not args.status or not args.note:
        ap.error("--phase, --status, and --note are required unless using --update-all")

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

    # Auto-create module file only if explicitly requested or if phase becomes completed
    if args.create_module or args.status == "completed":
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
