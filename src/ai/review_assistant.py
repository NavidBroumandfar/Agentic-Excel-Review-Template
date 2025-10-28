# ⚠️ Compliance Notice:
# Assistive mode only. Do NOT overwrite validated cells or macros in `MTCR Data.xlsm`.
# AI outputs must be written only to new columns prefixed with "AI_".
# All inferences are logged for traceability and QA review.

"""
AI Review Assistant for MTCR Quality Review comments.
Uses RAG (Retrieval-Augmented Generation) with LM Studio for local inference.
"""

import json
import logging
import requests
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from utils.sop_indexer import SOPIndexer

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ReviewAssistant:
    """AI Review Assistant using RAG + LM Studio for comment analysis."""

    def __init__(
        self,
        lm_studio_url: str = "http://127.0.0.1:1234/v1",
        sop_index_dir: str = "data/embeddings",
        log_file: str = "logs/mtcr_review_assistant.jsonl",
    ):
        """
        Initialize the Review Assistant.

        Args:
            lm_studio_url: LM Studio API endpoint
            sop_index_dir: Directory containing SOP embeddings
            log_file: Path to JSONL log file
        """
        self.lm_studio_url = lm_studio_url
        self.sop_index_dir = sop_index_dir
        self.log_file = log_file

        # Initialize SOP indexer
        self.sop_indexer = SOPIndexer(index_dir=sop_index_dir)

        # Load prompt template
        self.prompt_template = self._load_prompt_template()

        # Create logs directory
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Review Assistant initialized with LM Studio at {lm_studio_url}")

    def _load_prompt_template(self) -> str:
        """Load the review prompt template."""
        template_path = (
            Path(__file__).parent.parent.parent / "ai" / "prompts" / "review_prompt.txt"
        )
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"Prompt template not found at {template_path}")
            return self._get_default_prompt()

    def _get_default_prompt(self) -> str:
        """Fallback prompt template if file not found."""
        return """System:
You are an expert in Technical Complaint Reviews following SOP 029014 (Rev 15.A).

Instruction:
Given the comment below and relevant SOP context, return a JSON object:
{
 "reason": "Standardized reason for correction",
 "confidence": 0.85,
 "comment_standardized": "Cleaned version of the comment",
 "rationale_short": "Brief explanation",
 "model_version": "MTCR-Llama3-v0.1"
}

Comment: {comment}
Context: {context}"""

    def _test_lm_studio_connection(self) -> bool:
        """Test connection to LM Studio."""
        try:
            response = requests.get(f"{self.lm_studio_url}/models", timeout=5)
            if response.status_code == 200:
                logger.info("LM Studio connection successful")
                return True
            else:
                logger.error(f"LM Studio returned status {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Failed to connect to LM Studio: {e}")
            return False

    def _generate_prompt(self, comment: str, context: str) -> str:
        """Generate the full prompt with comment and context."""
        return self.prompt_template.format(comment=comment, context=context)

    def _call_lm_studio(self, prompt: str) -> Optional[str]:
        """Call LM Studio API for inference."""
        try:
            payload = {
                "model": "local-model",  # LM Studio uses this for local models
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "max_tokens": 500,
                "stream": False,
            }

            response = requests.post(
                f"{self.lm_studio_url}/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                logger.error(
                    f"LM Studio API error: {response.status_code} - {response.text}"
                )
                return None

        except Exception as e:
            logger.error(f"Error calling LM Studio: {e}")
            return None

    def _parse_json_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse JSON response from LLM, handling potential formatting issues."""
        try:
            # Try direct JSON parsing first
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            try:
                # Look for JSON between curly braces
                start = response.find("{")
                end = response.rfind("}") + 1
                if start != -1 and end > start:
                    json_str = response[start:end]
                    return json.loads(json_str)
            except json.JSONDecodeError:
                pass

            # Try to find JSON in code blocks
            try:
                if "```json" in response:
                    json_start = response.find("```json") + 7
                    json_end = response.find("```", json_start)
                    if json_end > json_start:
                        json_str = response[json_start:json_end].strip()
                        return json.loads(json_str)
            except json.JSONDecodeError:
                pass

            logger.error(f"Failed to parse JSON from response: {response}")
            return None

    def _validate_response(self, response: Dict[str, Any]) -> bool:
        """Validate the LLM response structure."""
        required_fields = [
            "reason",
            "confidence",
            "comment_standardized",
            "rationale_short",
            "model_version",
        ]

        for field in required_fields:
            if field not in response:
                logger.error(f"Missing required field: {field}")
                return False

        # Validate confidence is a number between 0 and 1
        try:
            confidence = float(response["confidence"])
            if not 0.0 <= confidence <= 1.0:
                logger.error(
                    f"Confidence must be between 0.0 and 1.0, got: {confidence}"
                )
                return False
        except (ValueError, TypeError):
            logger.error(f"Confidence must be a number, got: {response['confidence']}")
            return False

        return True

    def _log_inference(
        self,
        row_data: Dict[str, Any],
        context: List[Dict],
        response: Optional[Dict],
        error: Optional[str] = None,
    ):
        """Log the inference result to JSONL file."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "row_id": row_data.get("index", "unknown"),
            "original_comment": row_data.get("Comment", ""),
            "context_chunks": len(context),
            "response": response,
            "error": error,
            "model_version": (
                response.get("model_version", "unknown") if response else None
            ),
        }

        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Failed to write log entry: {e}")

    def infer_reason(self, row: pd.Series) -> Dict[str, Any]:
        """
        Infer reason for correction for a single row.

        Args:
            row: Pandas Series containing the row data

        Returns:
            Dictionary with AI inference results
        """
        comment = str(row.get("Comment", "")).strip()

        if not comment or comment.lower() in ["nan", "none", ""]:
            logger.warning(f"Empty comment for row {row.name}")
            return {
                "AI_reason": "No comment provided",
                "AI_confidence": 0.0,
                "AI_comment_standardized": "",
                "AI_rationale_short": "No comment to analyze",
                "AI_model_version": "MTCR-Llama3-v0.1",
            }

        try:
            # Retrieve relevant context
            context_chunks = self.sop_indexer.retrieve_context(comment, k=4)
            context_text = "\n\n".join([chunk["text"] for chunk in context_chunks])

            # Generate prompt
            prompt = self._generate_prompt(comment, context_text)

            # Call LM Studio
            llm_response = self._call_lm_studio(prompt)

            if llm_response is None:
                error_msg = "Failed to get response from LM Studio"
                logger.error(error_msg)
                self._log_inference(row.to_dict(), context_chunks, None, error_msg)
                return {
                    "AI_reason": "Error: No LLM response",
                    "AI_confidence": 0.0,
                    "AI_comment_standardized": comment,
                    "AI_rationale_short": error_msg,
                    "AI_model_version": "MTCR-Llama3-v0.1",
                }

            # Parse and validate response
            parsed_response = self._parse_json_response(llm_response)

            if parsed_response is None or not self._validate_response(parsed_response):
                error_msg = "Invalid JSON response from LLM"
                logger.error(f"{error_msg}: {llm_response}")
                self._log_inference(row.to_dict(), context_chunks, None, error_msg)
                return {
                    "AI_reason": "Error: Invalid LLM response",
                    "AI_confidence": 0.0,
                    "AI_comment_standardized": comment,
                    "AI_rationale_short": error_msg,
                    "AI_model_version": "MTCR-Llama3-v0.1",
                }

            # Log successful inference
            self._log_inference(row.to_dict(), context_chunks, parsed_response)

            # Return formatted result
            return {
                "AI_reason": parsed_response["reason"],
                "AI_confidence": parsed_response["confidence"],
                "AI_comment_standardized": parsed_response["comment_standardized"],
                "AI_rationale_short": parsed_response["rationale_short"],
                "AI_model_version": parsed_response["model_version"],
            }

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            self._log_inference(row.to_dict(), [], None, error_msg)
            return {
                "AI_reason": f"Error: {str(e)}",
                "AI_confidence": 0.0,
                "AI_comment_standardized": comment,
                "AI_rationale_short": error_msg,
                "AI_model_version": "MTCR-Llama3-v0.1",
            }

    def process_all(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process all rows in the DataFrame.

        Args:
            df: DataFrame containing Quality Review data

        Returns:
            DataFrame with AI columns added
        """
        logger.info(f"Processing {len(df)} rows")

        # Test LM Studio connection
        if not self._test_lm_studio_connection():
            logger.error("Cannot connect to LM Studio. Please ensure it's running.")
            return df

        # Process each row
        ai_results = []
        for idx, row in df.iterrows():
            logger.info(f"Processing row {idx + 1}/{len(df)}")
            result = self.infer_reason(row)
            ai_results.append(result)

        # Add AI columns to DataFrame
        ai_df = pd.DataFrame(ai_results, index=df.index)
        result_df = pd.concat([df, ai_df], axis=1)

        logger.info(f"Processing complete. Added {len(ai_df.columns)} AI columns.")
        return result_df


def main():
    """Main function for testing the Review Assistant."""
    import argparse

    parser = argparse.ArgumentParser(description="AI Review Assistant for MTCR")
    parser.add_argument("--test", action="store_true", help="Run test with mock data")
    parser.add_argument("--input", type=str, help="Input CSV file path")
    parser.add_argument("--output", type=str, help="Output CSV file path")

    args = parser.parse_args()

    if args.test:
        # Create test data
        test_data = {
            "Comment": [
                "Missing calibration certificate for temperature sensor",
                "Documentation incomplete - missing batch number",
                "Equipment not properly maintained according to SOP",
            ],
            "Site": ["Site A", "Site B", "Site C"],
            "Date": ["2024-01-15", "2024-01-16", "2024-01-17"],
        }
        df = pd.DataFrame(test_data)

        print("Running test with mock data...")
        print("Test data:")
        print(df)
        print("\n" + "=" * 50 + "\n")

        # Initialize assistant
        assistant = ReviewAssistant()

        # Process test data
        result_df = assistant.process_all(df)

        print("Results:")
        print(
            result_df[["Comment", "AI_reason", "AI_confidence", "AI_rationale_short"]]
        )

    elif args.input and args.output:
        # Process real data
        df = pd.read_csv(args.input)
        assistant = ReviewAssistant()
        result_df = assistant.process_all(df)
        result_df.to_csv(args.output, index=False)
        print(f"Results saved to {args.output}")

    else:
        print("Use --test for mock data or --input/--output for real data")


if __name__ == "__main__":
    main()
