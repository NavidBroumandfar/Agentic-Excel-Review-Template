# ⚠️ Compliance Notice:
# Assistive mode only. No modifications to validated Excel ranges.
# All AI outputs must be written to new files or new columns prefixed with "AI_".
# This module is for local prototype demonstration only.

"""
Excel Review Demo Pipeline Runner
CLI runner for end-to-end demonstration of Excel Review Agentic Automation.
"""

from __future__ import annotations
import argparse
import sys
import os
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ai.orchestrator import ExcelReviewOrchestrator
from src.utils.config_loader import load_config


def main():
    """Main entry point for demo pipeline."""
    parser = argparse.ArgumentParser(
        description="Excel Review Demo Pipeline - Process N sample rows from Review sheet",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/run_excel_review_demo.py --n 10
  python src/run_excel_review_demo.py --n 5
        """
    )
    parser.add_argument(
        "--n",
        type=int,
        default=10,
        help="Number of sample rows to process (default: 10)",
    )
    
    args = parser.parse_args()
    
    print("Excel Review Agentic Automation - Demo Pipeline")
    print(f"Processing {args.n} sample rows...")
    print()
    
    try:
        # Load config
        config = load_config()
        
        # Initialize orchestrator
        orchestrator = ExcelReviewOrchestrator(config=config)
        
        # Run demo
        result = orchestrator.run_demo(sample_size=args.n)
        
        # Print final summary
        print()
        print("[SUCCESS] Demo completed successfully!")
        print(f"   Total processed rows: {result.get('rows_processed', 0)}")
        print(f"   Average confidence: {result.get('avg_confidence', 0.0)}")
        print(f"   Output file: {result.get('output_file', 'N/A')}")
        if result.get('log_file'):
            print(f"   Log file: {result['log_file']}")
        
        sys.exit(0)
    
    except KeyboardInterrupt:
        print("\n[WARNING] Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Demo failed: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

