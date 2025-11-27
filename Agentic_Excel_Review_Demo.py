#!/usr/bin/env python3
"""
Agentic Excel Review Demo - Python Script Version
Converted from Agentic_Excel_Review_Demo.ipynb

Author: Navid Broumandfar

This script runs the complete Excel review demo pipeline:
- Tests LM Studio connection
- Processes sample Excel review data with AI
- Generates visualizations and analysis
"""

import subprocess
import sys
from pathlib import Path
import pandas as pd
import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from IPython.display import Image, display
from io import BytesIO

# ============================================================================
# 0. PACKAGE INSTALLATION
# ============================================================================


def install_if_missing(package):
    """Install package if not already installed."""
    try:
        __import__(package)
        print(f"[OK] {package} already installed")
    except ImportError:
        print(f"[Installing] {package}...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package, "--quiet"]
        )
        print(f"[OK] {package} installed successfully")


# Install required packages
required_packages = ["pandas", "matplotlib", "networkx", "openpyxl", "requests"]

print("Checking and installing required packages...")
print("=" * 60)

for package in required_packages:
    install_if_missing(package)

print("=" * 60)
print("[OK] All required packages are ready!\n")


# ============================================================================
# 1. IMPORTS AND SETUP
# ============================================================================

from src.utils.config_loader import load_config
from src.utils.lmstudio_smoketest import test_lmstudio_connection
from src.ai.orchestrator import run_demo


def draw_flowchart(nodes, edges, title, layout_type="linear"):
    """
    Draw a professional flowchart with manual positioning.

    Args:
        nodes: list of (id, label) tuples
        edges: list of (source, target) tuples
        title: diagram title
        layout_type: 'linear' (left-to-right), 'tree' (hierarchical), or 'custom'
    """
    fig, ax = plt.subplots(figsize=(16, 10), dpi=120)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # Create position mapping based on layout type
    node_positions = {}

    if layout_type == "linear":
        # Horizontal linear flow (for roadmap)
        n = len(nodes)
        for i, (node_id, label) in enumerate(nodes):
            node_positions[node_id] = (1 + (i * 8 / (n - 1)) if n > 1 else 5, 5)

    elif layout_type == "tree":
        # Tree-style layout (for process/architecture)
        node_dict = {nid: label for nid, label in nodes}
        edge_dict = {}
        for src, dst in edges:
            if src not in edge_dict:
                edge_dict[src] = []
            edge_dict[src].append(dst)

        # Find root (nodes with no incoming edges)
        all_dests = set(dst for _, dst in edges)
        roots = [nid for nid, _ in nodes if nid not in all_dests]

        if roots:
            # Level-based positioning
            levels = {}

            def assign_levels(node, level=0):
                if node in levels:
                    return
                levels[node] = level
                if node in edge_dict:
                    for child in edge_dict[node]:
                        assign_levels(child, level + 1)

            for root in roots:
                assign_levels(root)

            # Group by level
            level_groups = {}
            for node, level in levels.items():
                if level not in level_groups:
                    level_groups[level] = []
                level_groups[level].append(node)

            # Position nodes
            max_level = max(levels.values()) if levels else 0
            for level, nodes_in_level in level_groups.items():
                y = 9 - (level * 8 / (max_level + 1)) if max_level > 0 else 5
                n_nodes = len(nodes_in_level)
                for i, node in enumerate(nodes_in_level):
                    x = 1 + (i * 8 / (n_nodes - 1)) if n_nodes > 1 else 5
                    node_positions[node] = (x, y)

    # Draw edges first (so they appear behind nodes)
    for src, dst in edges:
        if src in node_positions and dst in node_positions:
            x1, y1 = node_positions[src]
            x2, y2 = node_positions[dst]

            # Draw arrow
            ax.annotate(
                "",
                xy=(x2, y2),
                xytext=(x1, y1),
                arrowprops=dict(
                    arrowstyle="->",
                    lw=2.5,
                    color="#555555",
                    connectionstyle="arc3,rad=0.15",
                ),
            )

    # Draw nodes
    for node_id, label in nodes:
        if node_id in node_positions:
            x, y = node_positions[node_id]

            # Draw rounded rectangle
            box = mpatches.FancyBboxPatch(
                (x - 0.5, y - 0.3),
                1.0,
                0.6,
                boxstyle="round,pad=0.05",
                facecolor="#4A90E2",
                edgecolor="#2E5C8A",
                linewidth=3,
            )
            ax.add_patch(box)

            # Add text with wrapping
            wrapped_label = "\n".join(
                [label[i : i + 20] for i in range(0, len(label), 20)]
            )
            ax.text(
                x,
                y,
                wrapped_label,
                ha="center",
                va="center",
                fontsize=11,
                fontweight="bold",
                color="white",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="none", edgecolor="none"),
            )

    # Add title
    ax.text(5, 9.7, title, ha="center", fontsize=18, fontweight="bold")

    plt.tight_layout()

    # Save diagram
    output_file = (
        title.replace(" ", "_").replace(":", "").replace("(", "").replace(")", "")
        + ".png"
    )
    plt.savefig(
        output_file, format="png", bbox_inches="tight", dpi=150, facecolor="white"
    )
    print(f"📊 Diagram saved: {output_file}")
    plt.close()


print("[OK] Setup complete! Ready to run the demo.\n")


# ============================================================================
# 2. GENERATE DIAGRAMS
# ============================================================================

print("=" * 60)
print("GENERATING PROCESS DIAGRAMS")
print("=" * 60)

# Diagram 1: Current Excel Review Process
nodes = [
    ("SRC", "Source Data"),
    ("EXL", "Review Workbook.xlsx"),
    ("REV", "Manual Review"),
    ("KPIS", "KPIs / Dashboards"),
    ("REPORT", "Reports & Actions"),
]
edges = [
    ("SRC", "EXL"),
    ("EXL", "REV"),
    ("REV", "KPIS"),
    ("REV", "REPORT"),
]
draw_flowchart(nodes, edges, "Current Excel Review Process (Simplified)", layout_type="tree")

# Diagram 2: Agentic Automation Architecture
nodes = [
    ("SUB", "Sample Review Data"),
    ("RAG", "RAG Context (SOPs)"),
    ("LLM", "Local LLM"),
    ("AIW", "AI Review Engine"),
    ("CSV", "Demo CSV Output"),
    ("LOG", "JSONL Logs"),
]
edges = [
    ("SUB", "RAG"),
    ("SUB", "LLM"),
    ("RAG", "LLM"),
    ("LLM", "AIW"),
    ("AIW", "CSV"),
    ("AIW", "LOG"),
]
draw_flowchart(
    nodes,
    edges,
    "Excel Review Agentic Automation Architecture (Local Prototype)",
    layout_type="tree",
)

# Diagram 3: Roadmap
nodes = [
    ("M1", "M1 Excel Reader"),
    ("M2", "M2 AI Assistant"),
    ("M3", "M3 Safe Writer"),
    ("M4", "M4 Log Manager"),
    ("M5", "M5 Taxonomy Mgr"),
    ("M6", "M6 SOP Indexer"),
    ("M7", "M7 Model Card"),
    ("M8", "M8 Tracker"),
    ("M9", "M9 Publication"),
    ("M10", "M10 Orchestrator★"),
    ("M11", "M11 UI & Chat"),
    ("M12", "M12+ Future"),
]
edges = [
    ("M1", "M2"),
    ("M2", "M3"),
    ("M3", "M4"),
    ("M4", "M5"),
    ("M5", "M6"),
    ("M6", "M7"),
    ("M7", "M8"),
    ("M8", "M9"),
    ("M9", "M10"),
    ("M10", "M11"),
    ("M11", "M12"),
]
draw_flowchart(
    nodes, edges, "Excel Review Roadmap M1-M11 Completed", layout_type="linear"
)

print("\n✅ All diagrams generated!\n")


# ============================================================================
# 3. TEST LM STUDIO CONNECTION
# ============================================================================

print("=" * 60)
print("TESTING LM STUDIO CONNECTION")
print("=" * 60)

config = load_config()
print("Loaded config:")
print(f"  Input file: {config.input_file}")
print(f"  Sheet name: {config.sheet_name}")
print(f"  Output dir: {config.out_dir}")

try:
    ok = test_lmstudio_connection()
    print("\nLM Studio connection:", "OK ✅" if ok else "FAILED ❌")
except Exception as e:
    print("LM Studio connection test failed ❌")
    print(type(e).__name__, "-", e)

print()


# ============================================================================
# 4. RUN DEMO PIPELINE
# ============================================================================

print("=" * 60)
print("RUNNING EXCEL REVIEW DEMO PIPELINE")
print("=" * 60)

demo_rows = 5  # Number of rows to process

result = run_demo(sample_size=demo_rows)

print("\nDemo completed.")
print("Rows processed:", result.get("rows_processed"))
print("Average confidence:", result.get("avg_confidence"))
print("Output CSV:", result.get("output_path"))
print("Log file:", result.get("log_path"))

print()


# ============================================================================
# 5. ANALYZE RESULTS
# ============================================================================

print("=" * 60)
print("ANALYZING DEMO RESULTS")
print("=" * 60)

output_path = Path(result.get("output_path", "out/mtcr_ai_demo.csv"))

if not output_path.exists():
    print(f"❌ Error: Output file not found at {output_path}")
    sys.exit(1)

df_demo = pd.read_csv(output_path)

print(f"\n📊 Demo dataset loaded from: {output_path}")
print(f"📊 Shape: {df_demo.shape[0]} rows x {df_demo.shape[1]} columns")

# Find reason column
candidate_cols = [
    c for c in df_demo.columns if "AI_Reason" in c or "AI_ReasonSuggestion" in c
]

if candidate_cols:
    reason_col = candidate_cols[0]
    print(f"📊 Reason column: {reason_col}")

    # Show distribution
    reason_counts = df_demo[reason_col].value_counts().head(10)
    print("\n📊 Top AI Reason Suggestions:")
    print(reason_counts)

    # Create visualization
    fig, ax = plt.subplots(figsize=(12, 6), dpi=100)
    reason_counts.plot(
        kind="bar", ax=ax, color="#4A90E2", edgecolor="#2E5C8A", linewidth=1.5
    )
    ax.set_title("Top AI Reason Suggestions", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Reason", fontsize=12, fontweight="bold")
    ax.set_ylabel("Count", fontsize=12, fontweight="bold")
    plt.xticks(rotation=45, ha="right")
    plt.grid(axis="y", alpha=0.3, linestyle="--")
    plt.tight_layout()
    plt.savefig("AI_Reason_Distribution.png", bbox_inches="tight", dpi=150)
    print("\n📊 Chart saved: AI_Reason_Distribution.png")
    plt.close()

    # Check for errors or low confidence
    error_rows = df_demo[
        (df_demo[reason_col].str.contains("Error:", na=False))
        | (df_demo["AI_Confidence"] < 0.5)
    ]

    if len(error_rows) > 0:
        print(f"\n⚠️  Found {len(error_rows)} rows with errors or low confidence (<0.5)")
        for idx, row in error_rows.iterrows():
            print(
                f"  Row {idx}: {row[reason_col]} (Confidence: {row.get('AI_Confidence', 'N/A')})"
            )
    else:
        print("\n✅ No errors or low-confidence predictions!")

else:
    print("❌ Could not find AI reason column in output")

print()


# ============================================================================
# 6. SUMMARY
# ============================================================================

print("=" * 60)
print("DEMO COMPLETE")
print("=" * 60)
print("\n📊 Generated Files:")
print(f"  - {output_path}")
print(f"  - AI_Reason_Distribution.png")
print(f"  - Current_Excel_Review_Process_Simplified.png")
print(f"  - Excel_Review_Agentic_Automation_Architecture_Local_Prototype.png")
print(f"  - Excel_Review_Roadmap_M1-M11_Completed.png")
print(f"  - {result.get('log_path', 'N/A')}")
print("\n✅ Agentic Excel Review Demo completed successfully!")
print("=" * 60)
