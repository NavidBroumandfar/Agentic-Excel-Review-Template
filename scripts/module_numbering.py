#!/usr/bin/env python3
"""
Module Numbering System Helper
Maintains consistent numbering between ProjectVision.ts phases and docs/prompts/module-XX.txt files.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Module mapping: M1 -> module-01, M2 -> module-02, etc.
MODULE_MAPPING = {
    "M1": "module-01",
    "M2": "module-02",
    "M3": "module-03",
    "M4": "module-04",
    "M5": "module-05",
    "M6": "module-06",
    "M7": "module-07",
    "M8": "module-08",
    "M9": "module-09",
}


def get_phase_info_from_vision() -> Dict[str, Dict]:
    """Extract phase information from ProjectVision.ts"""
    vision_path = Path("src/context/ProjectVision.ts")
    if not vision_path.exists():
        return {}

    with open(vision_path, "r", encoding="utf-8") as f:
        content = f.read()

    phases = {}
    # Extract phase information using regex
    phase_pattern = r'{\s*id:\s*"(M\d+)",\s*title:\s*"([^"]+)",[^}]*status:\s*"([^"]+)"'
    matches = re.findall(phase_pattern, content, re.DOTALL)

    for match in matches:
        phase_id, title, status = match
        phases[phase_id] = {"title": title, "status": status}

    return phases


def check_module_files() -> List[Tuple[str, str, bool]]:
    """Check which module files exist and their status"""
    prompts_dir = Path("docs/prompts")
    results = []

    for phase_id, module_file in MODULE_MAPPING.items():
        file_path = prompts_dir / f"{module_file}.txt"
        exists = file_path.exists()
        results.append((phase_id, module_file, exists))

    return results


def validate_numbering_consistency() -> Dict[str, any]:
    """Validate that module numbering is consistent"""
    phases = get_phase_info_from_vision()
    module_files = check_module_files()

    issues = []
    recommendations = []

    for phase_id, module_file, exists in module_files:
        if phase_id in phases:
            phase_info = phases[phase_id]
            if exists:
                # Check if file content matches phase
                file_path = Path(f"docs/prompts/{module_file}.txt")
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Check if phase ID is mentioned in file
                    if phase_id not in content:
                        issues.append(
                            f"{module_file}.txt exists but doesn't mention {phase_id}"
                        )

                    # Check if status matches
                    if f"Status: {phase_info['status']}" not in content:
                        issues.append(
                            f"{module_file}.txt status doesn't match ProjectVision.ts"
                        )

                except Exception as e:
                    issues.append(f"Error reading {module_file}.txt: {e}")
            else:
                if phase_info["status"] in ["completed", "active"]:
                    recommendations.append(
                        f"Create {module_file}.txt for {phase_id} ({phase_info['title']})"
                    )
        else:
            if exists:
                issues.append(
                    f"{module_file}.txt exists but {phase_id} not found in ProjectVision.ts"
                )

    return {
        "issues": issues,
        "recommendations": recommendations,
        "phases": phases,
        "module_files": module_files,
    }


def print_status():
    """Print current module numbering status"""
    print("🔍 Module Numbering System Status")
    print("=" * 50)

    validation = validate_numbering_consistency()

    print("\n📋 Phases from ProjectVision.ts:")
    for phase_id, info in validation["phases"].items():
        status_emoji = (
            "✅"
            if info["status"] == "completed"
            else "🔄" if info["status"] == "active" else "📋"
        )
        print(f"  {status_emoji} {phase_id}: {info['title']} ({info['status']})")

    print("\n📁 Module Files Status:")
    for phase_id, module_file, exists in validation["module_files"]:
        status_emoji = "✅" if exists else "❌"
        print(f"  {status_emoji} {module_file}.txt")

    if validation["issues"]:
        print("\n⚠️  Issues Found:")
        for issue in validation["issues"]:
            print(f"  - {issue}")

    if validation["recommendations"]:
        print("\n💡 Recommendations:")
        for rec in validation["recommendations"]:
            print(f"  - {rec}")

    if not validation["issues"] and not validation["recommendations"]:
        print("\n✅ All module numbering is consistent!")


def create_module_template(phase_id: str) -> str:
    """Create a template for a new module file"""
    if phase_id not in MODULE_MAPPING:
        raise ValueError(f"Unknown phase ID: {phase_id}")

    module_file = MODULE_MAPPING[phase_id]

    template = f"""# Module {module_file.replace('module-', '').zfill(2)} — {phase_id}: [TITLE]
Summary: [Brief description of the module's purpose and functionality]

Phase: {phase_id}
Status: [planned/active/completed]
Objective: [Clear objective statement]

Key files to create:
- [List key files that will be created]

Development notes:
- Phase {phase_id} [status]
- [Development notes]
- [Next steps]

[Paste here the exact prompt used to generate {phase_id} with Cursor.]
"""
    return template


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Module Numbering System Helper")
    parser.add_argument(
        "--check", action="store_true", help="Check numbering consistency"
    )
    parser.add_argument(
        "--create", type=str, help="Create template for phase ID (e.g., M4)"
    )
    parser.add_argument("--status", action="store_true", help="Show current status")

    args = parser.parse_args()

    if args.check or args.status:
        print_status()
    elif args.create:
        try:
            template = create_module_template(args.create)
            print(f"Template for {args.create}:")
            print("-" * 40)
            print(template)
        except ValueError as e:
            print(f"Error: {e}")
    else:
        print("Use --help for available options")


if __name__ == "__main__":
    main()
