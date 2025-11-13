# ⚠️ Compliance Notice:
# Assistive mode only. No modifications to validated Excel ranges.
# All AI outputs must be written to new files or new columns prefixed with "AI_".
# This module is for local prototype demonstration only.

"""
MTCR Demo Orchestrator
Chains M1 → M2 → M3 → M4 steps with clear step logs.
"""

from __future__ import annotations
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

import pandas as pd

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import modules
from src.utils.config_loader import load_config, Config
from src.excel.mtcr_reader import read_quality_review
from src.ai.review_assistant import ReviewAssistant
from src.utils.sop_indexer import SOPIndexer


class MTCRDemoOrchestrator:
    """Orchestrator for MTCR demo pipeline."""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize orchestrator.
        
        Args:
            config: Config object (if None, loads from config.json)
        """
        self.config = config or load_config()
        self.out_dir = Path(self.config.out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        
        # Load LM Studio URL from config
        try:
            config_path = Path("config.json")
            if config_path.exists():
                cfg_dict = json.loads(config_path.read_text(encoding="utf-8"))
                self.lm_studio_url = cfg_dict.get("lm_studio_url", "http://127.0.0.1:1234/v1")
            else:
                self.lm_studio_url = "http://127.0.0.1:1234/v1"
        except Exception:
            self.lm_studio_url = "http://127.0.0.1:1234/v1"
        
        # Initialize review assistant
        self.review_assistant = ReviewAssistant(
            lm_studio_url=self.lm_studio_url,
            sop_index_dir="data/embeddings",
            log_file="logs/mtcr_review_assistant.jsonl",
        )
        
        self.step_logs = []
    
    def _log_step(self, step_num: int, step_name: str, message: str, data: Optional[Dict] = None):
        """Log a step with formatted output."""
        log_entry = {
            "step": step_num,
            "name": step_name,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "data": data or {},
        }
        self.step_logs.append(log_entry)
        print(f"[STEP {step_num}] {step_name}: {message}")
        if data:
            for key, value in data.items():
                print(f"  {key}: {value}")
    
    def _map_ai_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Map review_assistant column names to mtcr_writer expected names.
        
        review_assistant uses: AI_reason, AI_confidence, AI_comment_standardized, AI_rationale_short, AI_model_version
        mtcr_writer expects: AI_ReasonSuggestion, AI_Confidence, AI_CommentStandardized, AI_RationaleShort, AI_ModelVersion
        """
        column_mapping = {
            "AI_reason": "AI_ReasonSuggestion",
            "AI_confidence": "AI_Confidence",
            "AI_comment_standardized": "AI_CommentStandardized",
            "AI_rationale_short": "AI_RationaleShort",
            "AI_model_version": "AI_ModelVersion",
        }
        
        # Map columns and drop old ones to avoid duplicates
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                df[new_col] = df[old_col]
                # Drop old column to avoid duplicates
                df = df.drop(columns=[old_col])
        
        return df
    
    def run_demo(self, sample_size: int = 10) -> Dict[str, Any]:
        """
        Run the demo pipeline.
        
        Args:
            sample_size: Number of rows to process
        
        Returns:
            Dictionary with summary statistics
        """
        print("=" * 60)
        print("MTCR Demo Orchestrator - Starting Pipeline")
        print("=" * 60)
        
        # STEP 1: Load config
        self._log_step(1, "Load config", "Configuration loaded", {
            "input_file": self.config.input_file,
            "sheet_name": self.config.sheet_name,
            "out_dir": str(self.out_dir),
        })
        
        # STEP 2: Load sample from Quality Review
        try:
            df, profile = read_quality_review(self.config)
            self._log_step(2, "Load sample from Quality Review", f"Loaded {len(df)} rows", {
                "total_rows": profile.row_count,
                "columns": profile.col_count,
                "sheet": profile.sheet_name,
            })
            
            # Sample N rows
            if len(df) > sample_size:
                df_sample = df.head(sample_size).copy()
                self._log_step(2, "Load sample from Quality Review", f"Sampled {sample_size} rows for demo", {})
            else:
                df_sample = df.copy()
                self._log_step(2, "Load sample from Quality Review", f"Using all {len(df_sample)} rows (less than sample_size)", {})
        
        except Exception as e:
            self._log_step(2, "Load sample from Quality Review", f"ERROR: {str(e)}", {})
            raise
        
        # STEP 3: Build context (optional RAG)
        try:
            # Check if SOP indexer is available
            sop_indexer = SOPIndexer(embeddings_dir="data/embeddings")
            self._log_step(3, "Build context (RAG)", "SOP indexer initialized", {
                "embeddings_dir": "data/embeddings",
            })
        except Exception as e:
            self._log_step(3, "Build context (RAG)", f"WARNING: RAG context unavailable ({str(e)})", {
                "note": "Continuing without RAG context",
            })
        
        # STEP 4: Call LLM for reasoning
        try:
            self._log_step(4, "Call LLM for reasoning", f"Processing {len(df_sample)} rows", {})
            
            # Process each row
            ai_results = []
            for idx, row in df_sample.iterrows():
                result = self.review_assistant.infer_reason(row)
                ai_results.append(result)
                print(f"  Processed row {idx + 1}/{len(df_sample)}")
            
            # Add AI columns to DataFrame
            ai_df = pd.DataFrame(ai_results, index=df_sample.index)
            df_with_ai = pd.concat([df_sample, ai_df], axis=1)
            
            # Map column names for compatibility
            df_with_ai = self._map_ai_columns(df_with_ai)
            
            self._log_step(4, "Call LLM for reasoning", f"Completed inference for {len(df_sample)} rows", {
                "ai_columns_added": len(ai_df.columns),
            })
        
        except Exception as e:
            self._log_step(4, "Call LLM for reasoning", f"ERROR: {str(e)}", {})
            raise
        
        # STEP 5: Write AI_ columns to demo CSV
        try:
            output_csv = self.out_dir / "mtcr_ai_demo.csv"
            df_with_ai.to_csv(output_csv, index=False, encoding="utf-8")
            self._log_step(5, "Write AI_ columns to demo CSV", f"Saved to {output_csv}", {
                "rows": len(df_with_ai),
                "columns": len(df_with_ai.columns),
            })
        except Exception as e:
            self._log_step(5, "Write AI_ columns to demo CSV", f"ERROR: {str(e)}", {})
            raise
        
        # STEP 6: Log each inference
        try:
            log_file = Path("logs") / "mtcr_demo_orchestrator.jsonl"
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "module": "M10_Orchestrator",
                "sample_size": sample_size,
                "rows_processed": len(df_sample),
                "output_file": str(output_csv),
                "step_logs": self.step_logs,
            }
            
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            
            self._log_step(6, "Log each inference", f"Logs written to {log_file}", {})
        except Exception as e:
            self._log_step(6, "Log each inference", f"WARNING: Logging failed ({str(e)})", {})
        
        # STEP 7: Summary
        try:
            # Calculate average confidence
            if "AI_Confidence" in df_with_ai.columns:
                avg_confidence = df_with_ai["AI_Confidence"].astype(float).mean()
            elif "AI_confidence" in df_with_ai.columns:
                avg_confidence = df_with_ai["AI_confidence"].astype(float).mean()
            else:
                avg_confidence = 0.0
            
            summary = {
                "rows_processed": len(df_sample),
                "avg_confidence": round(avg_confidence, 3),
                "output_file": str(output_csv),
                "log_file": str(log_file) if 'log_file' in locals() else None,
            }
            
            print("=" * 60)
            print("[DONE] Summary:")
            print(f"  Rows processed: {summary['rows_processed']}")
            print(f"  Average confidence: {summary['avg_confidence']}")
            print(f"  Output file: {summary['output_file']}")
            if summary['log_file']:
                print(f"  Log file: {summary['log_file']}")
            print("=" * 60)
            
            return summary
        
        except Exception as e:
            print(f"[DONE] Summary generation failed: {str(e)}")
            return {
                "rows_processed": len(df_sample),
                "avg_confidence": 0.0,
                "output_file": str(output_csv) if 'output_csv' in locals() else None,
                "error": str(e),
            }


def main():
    """Main entry point for orchestrator."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MTCR Demo Orchestrator")
    parser.add_argument("--n", type=int, default=10, help="Number of sample rows to process")
    args = parser.parse_args()
    
    orchestrator = MTCRDemoOrchestrator()
    result = orchestrator.run_demo(sample_size=args.n)
    
    if "error" in result:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()

