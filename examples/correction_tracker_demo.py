#!/usr/bin/env python3
"""
Demo script for Correction Tracker Agent (M8).
Shows how to use the correction tracker to compare AI vs human corrections.
"""

import os
import sys
import json
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from ai.correction_tracker import CorrectionTracker


def create_demo_data():
    """Create demo AI log data for testing."""
    demo_log_file = "logs/mtcr_review_assistant_202510.jsonl"
    
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(demo_log_file), exist_ok=True)
    
    # Demo AI log entries
    demo_entries = [
        {
            "timestamp": "2025-10-01T10:00:00Z",
            "row_id": "case_001",
            "response": {
                "reason": "Missing calibration certificate",
                "confidence": 0.85,
                "model_version": "MTCR-Llama3-v0.1"
            },
            "original_comment": "No calibration cert found for temperature sensor"
        },
        {
            "timestamp": "2025-10-01T10:01:00Z",
            "row_id": "case_002",
            "response": {
                "reason": "Documentation incomplete",
                "confidence": 0.92,
                "model_version": "MTCR-Llama3-v0.1"
            },
            "original_comment": "Missing batch number in documentation"
        },
        {
            "timestamp": "2025-10-01T10:02:00Z",
            "row_id": "case_003",
            "response": {
                "reason": "Equipment not properly maintained",
                "confidence": 0.78,
                "model_version": "MTCR-Llama3-v0.1"
            },
            "original_comment": "Equipment maintenance overdue"
        },
        {
            "timestamp": "2025-10-01T10:03:00Z",
            "row_id": "case_004",
            "response": {
                "reason": "Training records missing",
                "confidence": 0.88,
                "model_version": "MTCR-Llama3-v0.1"
            },
            "original_comment": "No training records for operator"
        },
        {
            "timestamp": "2025-10-01T10:04:00Z",
            "row_id": "case_005",
            "response": {
                "reason": "Sampling plan not followed",
                "confidence": 0.95,
                "model_version": "MTCR-Llama3-v0.1"
            },
            "original_comment": "Sampling frequency not according to SOP"
        }
    ]
    
    # Write demo log file
    with open(demo_log_file, "w", encoding="utf-8") as f:
        for entry in demo_entries:
            f.write(json.dumps(entry) + "\n")
    
    print(f"Created demo AI log file: {demo_log_file}")
    return demo_log_file


def main():
    """Run the correction tracker demo."""
    print("MTCR Correction Tracker Agent Demo")
    print("=" * 50)
    
    # Create demo data
    print("\n1. Creating demo AI log data...")
    demo_log_file = create_demo_data()
    
    # Initialize correction tracker
    print("\n2. Initializing Correction Tracker...")
    tracker = CorrectionTracker()
    
    # Run analysis
    print("\n3. Running correction analysis...")
    results = tracker.run_analysis(month="202510")
    
    if "error" in results:
        print(f"Error: {results['error']}")
        return 1
    
    # Display results
    print("\n4. Analysis Results:")
    print("-" * 30)
    
    kpi = results['kpi_summary']
    print(f"Total Cases Analyzed: {kpi['total_cases']}")
    print(f"Match Rate: {kpi['match_rate_pct']}%")
    print(f"Override Rate: {kpi['override_rate_pct']}%")
    print(f"Average AI Confidence: {kpi['avg_confidence']}")
    print(f"Confidence Correlation: {kpi['confidence_correlation']}")
    
    # Show detailed results
    print("\n5. Detailed Comparison Results:")
    print("-" * 40)
    comparison_df = results['comparison_df']
    
    for _, row in comparison_df.iterrows():
        status_symbol = {
            "Matched": "[MATCH]",
            "Partial": "[PARTIAL]",
            "Overridden": "[OVERRIDE]"
        }.get(row['match_status'], "[UNKNOWN]")
        
        print(f"\n{status_symbol} Case {row['case_id']}:")
        print(f"   AI Reason: {row['ai_reason']}")
        print(f"   Human Reason: {row['human_reason']}")
        print(f"   Status: {row['match_status']}")
        print(f"   Similarity: {row['similarity_score']:.2f}")
        print(f"   AI Confidence: {row['ai_confidence']:.2f}")
    
    # Show output files
    print("\n6. Output Files Generated:")
    print("-" * 30)
    print(f"CSV Report: {results['csv_path']}")
    print(f"Excel Report: {results['xlsx_path']}")
    print(f"Log File: {results['log_file']}")
    
    # Show file sizes
    if os.path.exists(results['csv_path']):
        csv_size = os.path.getsize(results['csv_path'])
        print(f"   CSV Size: {csv_size} bytes")
    
    if os.path.exists(results['xlsx_path']):
        xlsx_size = os.path.getsize(results['xlsx_path'])
        print(f"   Excel Size: {xlsx_size} bytes")
    
    print("\nDemo completed successfully!")
    print("\nYou can now:")
    print("- Open the Excel file to view detailed reports")
    print("- Import the CSV into Tableau for visualization")
    print("- Check the JSONL log for audit trail")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
