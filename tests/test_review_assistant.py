# ⚠️ Compliance Notice:
# Assistive mode only. Do NOT overwrite validated cells or macros in `MTCR Data.xlsm`.
# AI outputs must be written only to new columns prefixed with "AI_".
# All inferences are logged for traceability and QA review.

"""
Test suite for AI Review Assistant.
Tests RAG retrieval, LM Studio integration, and JSON response parsing.
"""

import unittest
import pandas as pd
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from ai.review_assistant import ReviewAssistant
from utils.sop_indexer import SOPIndexer


class TestReviewAssistant(unittest.TestCase):
    """Test cases for ReviewAssistant class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_index_dir = os.path.join(self.temp_dir, "test_embeddings")
        self.test_log_file = os.path.join(self.temp_dir, "test_log.jsonl")

        # Create test data
        self.test_data = {
            "Comment": [
                "Missing calibration certificate for temperature sensor",
                "Documentation incomplete - missing batch number",
                "Equipment not properly maintained according to SOP",
                "",  # Empty comment
                "Invalid comment with no clear issue",
            ],
            "Site": ["Site A", "Site B", "Site C", "Site D", "Site E"],
            "Date": [
                "2024-01-15",
                "2024-01-16",
                "2024-01-17",
                "2024-01-18",
                "2024-01-19",
            ],
        }
        self.test_df = pd.DataFrame(self.test_data)

        # Mock LM Studio response
        self.mock_llm_response = {
            "reason": "Calibration documentation missing",
            "confidence": 0.85,
            "comment_standardized": "Missing calibration certificate for temperature sensor",
            "rationale_short": "Standard calibration documentation issue",
            "model_version": "MTCR-Llama3-v0.1",
        }

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("requests.get")
    def test_lm_studio_connection_success(self, mock_get):
        """Test successful LM Studio connection."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"data": []}

        assistant = ReviewAssistant(
            sop_index_dir=self.test_index_dir, log_file=self.test_log_file
        )

        result = assistant._test_lm_studio_connection()
        self.assertTrue(result)

    @patch("requests.get")
    def test_lm_studio_connection_failure(self, mock_get):
        """Test failed LM Studio connection."""
        mock_get.side_effect = Exception("Connection failed")

        assistant = ReviewAssistant(
            sop_index_dir=self.test_index_dir, log_file=self.test_log_file
        )

        result = assistant._test_lm_studio_connection()
        self.assertFalse(result)

    def test_generate_prompt(self):
        """Test prompt generation."""
        assistant = ReviewAssistant(
            sop_index_dir=self.test_index_dir, log_file=self.test_log_file
        )

        comment = "Test comment"
        context = "Test context"

        prompt = assistant._generate_prompt(comment, context)

        self.assertIn(comment, prompt)
        self.assertIn(context, prompt)
        self.assertIn("System:", prompt)
        self.assertIn("Instruction:", prompt)

    def test_parse_json_response_valid(self):
        """Test parsing valid JSON response."""
        assistant = ReviewAssistant(
            sop_index_dir=self.test_index_dir, log_file=self.test_log_file
        )

        valid_json = json.dumps(self.mock_llm_response)
        result = assistant._parse_json_response(valid_json)

        self.assertEqual(result, self.mock_llm_response)

    def test_parse_json_response_with_code_block(self):
        """Test parsing JSON response wrapped in code block."""
        assistant = ReviewAssistant(
            sop_index_dir=self.test_index_dir, log_file=self.test_log_file
        )

        wrapped_json = f"```json\n{json.dumps(self.mock_llm_response)}\n```"
        result = assistant._parse_json_response(wrapped_json)

        self.assertEqual(result, self.mock_llm_response)

    def test_parse_json_response_invalid(self):
        """Test parsing invalid JSON response."""
        assistant = ReviewAssistant(
            sop_index_dir=self.test_index_dir, log_file=self.test_log_file
        )

        invalid_json = "This is not valid JSON"
        result = assistant._parse_json_response(invalid_json)

        self.assertIsNone(result)

    def test_validate_response_valid(self):
        """Test validation of valid response."""
        assistant = ReviewAssistant(
            sop_index_dir=self.test_index_dir, log_file=self.test_log_file
        )

        result = assistant._validate_response(self.mock_llm_response)
        self.assertTrue(result)

    def test_validate_response_missing_field(self):
        """Test validation of response with missing field."""
        assistant = ReviewAssistant(
            sop_index_dir=self.test_index_dir, log_file=self.test_log_file
        )

        invalid_response = {"reason": "test", "confidence": 0.5}
        result = assistant._validate_response(invalid_response)
        self.assertFalse(result)

    def test_validate_response_invalid_confidence(self):
        """Test validation of response with invalid confidence."""
        assistant = ReviewAssistant(
            sop_index_dir=self.test_index_dir, log_file=self.test_log_file
        )

        invalid_response = self.mock_llm_response.copy()
        invalid_response["confidence"] = 1.5  # Invalid confidence
        result = assistant._validate_response(invalid_response)
        self.assertFalse(result)

    @patch("requests.post")
    def test_call_lm_studio_success(self, mock_post):
        """Test successful LM Studio API call."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": json.dumps(self.mock_llm_response)}}]
        }
        mock_post.return_value = mock_response

        assistant = ReviewAssistant(
            sop_index_dir=self.test_index_dir, log_file=self.test_log_file
        )

        result = assistant._call_lm_studio("Test prompt")
        self.assertEqual(result, json.dumps(self.mock_llm_response))

    @patch("requests.post")
    def test_call_lm_studio_failure(self, mock_post):
        """Test failed LM Studio API call."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        assistant = ReviewAssistant(
            sop_index_dir=self.test_index_dir, log_file=self.test_log_file
        )

        result = assistant._call_lm_studio("Test prompt")
        self.assertIsNone(result)

    @patch("ai.review_assistant.SOPIndexer")
    @patch("requests.post")
    @patch("requests.get")
    def test_infer_reason_success(self, mock_get, mock_post, mock_indexer_class):
        """Test successful reason inference."""
        # Mock LM Studio connection
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"data": []}

        # Mock LM Studio response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": json.dumps(self.mock_llm_response)}}]
        }
        mock_post.return_value = mock_response

        # Mock SOP indexer
        mock_indexer = Mock()
        mock_indexer.retrieve_context.return_value = [
            {"text": "Test context chunk 1"},
            {"text": "Test context chunk 2"},
        ]
        mock_indexer_class.return_value = mock_indexer

        assistant = ReviewAssistant(
            sop_index_dir=self.test_index_dir, log_file=self.test_log_file
        )

        # Test with valid comment
        test_row = pd.Series(
            {"Comment": "Missing calibration certificate", "Site": "Site A"}, name=0
        )

        result = assistant.infer_reason(test_row)

        self.assertEqual(result["AI_reason"], self.mock_llm_response["reason"])
        self.assertEqual(result["AI_confidence"], self.mock_llm_response["confidence"])
        self.assertEqual(
            result["AI_comment_standardized"],
            self.mock_llm_response["comment_standardized"],
        )
        self.assertEqual(
            result["AI_rationale_short"], self.mock_llm_response["rationale_short"]
        )
        self.assertEqual(
            result["AI_model_version"], self.mock_llm_response["model_version"]
        )

    @patch("ai.review_assistant.SOPIndexer")
    def test_infer_reason_empty_comment(self, mock_indexer_class):
        """Test inference with empty comment."""
        mock_indexer = Mock()
        mock_indexer_class.return_value = mock_indexer

        assistant = ReviewAssistant(
            sop_index_dir=self.test_index_dir, log_file=self.test_log_file
        )

        test_row = pd.Series({"Comment": "", "Site": "Site A"}, name=0)

        result = assistant.infer_reason(test_row)

        self.assertEqual(result["AI_reason"], "No comment provided")
        self.assertEqual(result["AI_confidence"], 0.0)
        self.assertEqual(result["AI_rationale_short"], "No comment to analyze")

    @patch("ai.review_assistant.SOPIndexer")
    @patch("requests.post")
    @patch("requests.get")
    def test_infer_reason_llm_failure(self, mock_get, mock_post, mock_indexer_class):
        """Test inference when LLM call fails."""
        # Mock LM Studio connection
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"data": []}

        # Mock failed LM Studio response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        # Mock SOP indexer
        mock_indexer = Mock()
        mock_indexer.retrieve_context.return_value = [{"text": "Test context chunk"}]
        mock_indexer_class.return_value = mock_indexer

        assistant = ReviewAssistant(
            sop_index_dir=self.test_index_dir, log_file=self.test_log_file
        )

        test_row = pd.Series({"Comment": "Test comment", "Site": "Site A"}, name=0)

        result = assistant.infer_reason(test_row)

        self.assertIn("Error:", result["AI_reason"])
        self.assertEqual(result["AI_confidence"], 0.0)
        self.assertIn("No LLM response", result["AI_rationale_short"])

    @patch("ai.review_assistant.SOPIndexer")
    @patch("requests.post")
    @patch("requests.get")
    def test_process_all(self, mock_get, mock_post, mock_indexer_class):
        """Test processing all rows in DataFrame."""
        # Mock LM Studio connection
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"data": []}

        # Mock LM Studio response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": json.dumps(self.mock_llm_response)}}]
        }
        mock_post.return_value = mock_response

        # Mock SOP indexer
        mock_indexer = Mock()
        mock_indexer.retrieve_context.return_value = [{"text": "Test context chunk"}]
        mock_indexer_class.return_value = mock_indexer

        assistant = ReviewAssistant(
            sop_index_dir=self.test_index_dir, log_file=self.test_log_file
        )

        result_df = assistant.process_all(self.test_df)

        # Check that AI columns were added
        ai_columns = [col for col in result_df.columns if col.startswith("AI_")]
        self.assertEqual(len(ai_columns), 5)

        # Check that all rows were processed
        self.assertEqual(len(result_df), len(self.test_df))

        # Check that empty comment was handled
        empty_comment_row = result_df[result_df["Comment"] == ""].iloc[0]
        self.assertEqual(empty_comment_row["AI_reason"], "No comment provided")


class TestSOPIndexer(unittest.TestCase):
    """Test cases for SOPIndexer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_src_dir = os.path.join(self.temp_dir, "test_src")
        self.test_index_dir = os.path.join(self.temp_dir, "test_index")

        # Create test source directory
        Path(self.test_src_dir).mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init(self):
        """Test SOPIndexer initialization."""
        indexer = SOPIndexer(src_dir=self.test_src_dir, index_dir=self.test_index_dir)

        self.assertEqual(indexer.src_dir, Path(self.test_src_dir))
        self.assertEqual(indexer.index_dir, Path(self.test_index_dir))
        self.assertEqual(indexer.model_name, "all-MiniLM-L6-v2")

    def test_chunk_text_small(self):
        """Test text chunking with small text."""
        indexer = SOPIndexer(src_dir=self.test_src_dir, index_dir=self.test_index_dir)

        text = "This is a short text."
        chunks = indexer._chunk_text(text, chunk_size=1000)

        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], text)

    def test_chunk_text_large(self):
        """Test text chunking with large text."""
        indexer = SOPIndexer(src_dir=self.test_src_dir, index_dir=self.test_index_dir)

        text = "This is a sentence. " * 100  # Create long text
        chunks = indexer._chunk_text(text, chunk_size=100, overlap=20)

        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(chunk) <= 100 for chunk in chunks))


def run_mock_test():
    """Run a mock test without requiring actual LM Studio or SOP files."""
    print("Running mock test for Review Assistant...")

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

    print("Test data:")
    print(df)
    print("\n" + "=" * 50 + "\n")

    # Mock the assistant behavior
    print("Mock AI responses:")
    mock_responses = [
        {
            "AI_reason": "Calibration documentation missing",
            "AI_confidence": 0.85,
            "AI_comment_standardized": "Missing calibration certificate for temperature sensor",
            "AI_rationale_short": "Standard calibration documentation issue",
            "AI_model_version": "MTCR-Llama3-v0.1",
        },
        {
            "AI_reason": "Documentation incomplete",
            "AI_confidence": 0.90,
            "AI_comment_standardized": "Documentation incomplete - missing batch number",
            "AI_rationale_short": "Missing required batch documentation",
            "AI_model_version": "MTCR-Llama3-v0.1",
        },
        {
            "AI_reason": "Equipment maintenance issue",
            "AI_confidence": 0.75,
            "AI_comment_standardized": "Equipment not properly maintained according to SOP",
            "AI_rationale_short": "Maintenance not following standard procedures",
            "AI_model_version": "MTCR-Llama3-v0.1",
        },
    ]

    for i, response in enumerate(mock_responses):
        print(f"Row {i+1}:")
        print(f"  Original: {df.iloc[i]['Comment']}")
        print(f"  AI Reason: {response['AI_reason']}")
        print(f"  Confidence: {response['AI_confidence']}")
        print(f"  Rationale: {response['AI_rationale_short']}")
        print()

    print("Mock test completed successfully!")
    print(
        "Note: This test simulates the behavior without requiring LM Studio or SOP files."
    )


if __name__ == "__main__":
    # Run unit tests
    unittest.main(argv=[""], exit=False, verbosity=2)

    # Run mock test
    print("\n" + "=" * 60 + "\n")
    run_mock_test()
