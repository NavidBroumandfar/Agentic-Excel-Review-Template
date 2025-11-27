# ⚠️ Compliance Notice:
# This test module verifies the UI components without modifying validated data.

"""
Smoke test for MTCR Streamlit UI (M11)

Verifies that:
1. All UI functions are importable
2. Data loading functions work correctly
3. KPI computation handles edge cases
4. Context building produces valid output
"""

from __future__ import annotations
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pandas as pd


def test_imports():
    """Test that all UI module components can be imported."""
    print("Testing imports...")
    try:
        from src.ui.mtcr_app import (
            load_quality_review_dataframe,
            load_config_cached,
            compute_basic_kpis,
            build_sheet_context,
            call_mtcr_assistant,
        )

        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_kpi_computation():
    """Test KPI computation with sample data."""
    print("\nTesting KPI computation...")
    try:
        from src.ui.mtcr_app import compute_basic_kpis

        # Create sample DataFrame
        sample_data = pd.DataFrame(
            {
                "Comment": ["Test 1", "Test 2", None, "Test 4"],
                "Reviewer": ["Alice", "Bob", "Alice", "Charlie"],
                "AI_ReasonSuggestion": ["Reason A", "Reason B", None, "Reason A"],
                "AI_Confidence": [0.9, 0.8, None, 0.95],
            }
        )

        kpis = compute_basic_kpis(sample_data)

        # Verify expected KPIs
        assert kpis["total_rows"] == 4, f"Expected 4 rows, got {kpis['total_rows']}"
        assert (
            kpis["rows_with_comment"] == 3
        ), f"Expected 3 comments, got {kpis['rows_with_comment']}"
        assert (
            kpis["distinct_reviewers"] == 3
        ), f"Expected 3 reviewers, got {kpis['distinct_reviewers']}"
        assert (
            kpis["rows_with_ai_reason"] == 3
        ), f"Expected 3 AI reasons, got {kpis['rows_with_ai_reason']}"
        assert (
            kpis["ai_columns_count"] == 2
        ), f"Expected 2 AI columns, got {kpis['ai_columns_count']}"

        print(f"✓ KPI computation passed all checks")
        print(f"  - Total rows: {kpis['total_rows']}")
        print(f"  - Comments: {kpis['rows_with_comment']}")
        print(f"  - Reviewers: {kpis['distinct_reviewers']}")
        print(f"  - AI suggestions: {kpis['rows_with_ai_reason']}")
        print(f"  - AI columns: {kpis['ai_columns_count']}")
        return True
    except Exception as e:
        print(f"✗ KPI computation failed: {e}")
        return False


def test_context_building():
    """Test context building for LLM prompts."""
    print("\nTesting context building...")
    try:
        from src.ui.mtcr_app import build_sheet_context

        # Create sample DataFrame
        sample_data = pd.DataFrame(
            {
                "Comment": ["First comment", "Second comment", "Third comment"],
                "Reviewer": ["Alice", "Bob", "Alice"],
                "AI_ReasonSuggestion": ["Reason A", "Reason B", "Reason A"],
            }
        )

        context = build_sheet_context(sample_data, max_rows=2)

        # Verify context contains expected elements
        assert "Total rows: 3" in context, "Context missing total rows"
        assert "Rows with comments: 3" in context, "Context missing comment count"
        assert "=== MTCR Dataset Context ===" in context, "Context missing header"

        print("✓ Context building passed all checks")
        print(f"  - Context length: {len(context)} characters")
        print(f"  - Contains row counts: Yes")
        print(f"  - Contains example data: Yes")
        return True
    except Exception as e:
        print(f"✗ Context building failed: {e}")
        return False


def test_edge_cases():
    """Test edge cases like empty DataFrames."""
    print("\nTesting edge cases...")
    try:
        from src.ui.mtcr_app import compute_basic_kpis, build_sheet_context

        # Test with empty DataFrame
        empty_df = pd.DataFrame()
        kpis_empty = compute_basic_kpis(empty_df)
        assert kpis_empty["total_rows"] == 0, "Expected 0 rows for empty DataFrame"

        # Test with DataFrame without expected columns
        minimal_df = pd.DataFrame({"Data": [1, 2, 3]})
        kpis_minimal = compute_basic_kpis(minimal_df)
        context_minimal = build_sheet_context(minimal_df)

        assert kpis_minimal["total_rows"] == 3, "Expected 3 rows"
        assert (
            kpis_minimal["rows_with_comment"] == 0
        ), "Expected 0 comments (no comment column)"
        assert len(context_minimal) > 0, "Context should not be empty"

        print("✓ Edge cases handled correctly")
        print(f"  - Empty DataFrame: OK")
        print(f"  - Minimal columns: OK")
        return True
    except Exception as e:
        print(f"✗ Edge case handling failed: {e}")
        return False


def test_streamlit_available():
    """Test that Streamlit is installed."""
    print("\nTesting Streamlit installation...")
    try:
        import streamlit as st

        print(f"✓ Streamlit installed (version: {st.__version__})")
        return True
    except ImportError:
        print("✗ Streamlit not installed. Run: pip install streamlit")
        return False


def main():
    """Run all smoke tests."""
    print("=" * 60)
    print("MTCR Streamlit UI - Smoke Test Suite")
    print("=" * 60)

    tests = [
        test_streamlit_available,
        test_imports,
        test_kpi_computation,
        test_context_building,
        test_edge_cases,
    ]

    results = []
    for test in tests:
        results.append(test())

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("\n✅ All smoke tests passed!")
        print("\nYou can now run the UI with:")
        print("  streamlit run src/ui/mtcr_app.py")
        print("or use the launcher scripts:")
        print("  Windows: run_ui.bat")
        print("  Mac/Linux: bash run_ui.sh")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        print("\nPlease fix the issues before running the UI.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
