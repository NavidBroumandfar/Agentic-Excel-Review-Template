"""
Unit tests for Model Card Generator (M7)
"""

import json
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from compliance.model_card_generator import (
    sha256sum,
    get_git_commit_hash,
    collect_metadata,
    validate_metadata_schema,
    save_outputs,
    render_markdown,
)


class TestModelCardGenerator:
    """Test suite for model card generator functionality."""

    def test_sha256sum_existing_file(self):
        """Test SHA256 checksum calculation for existing file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            temp_path = f.name

        try:
            checksum = sha256sum(temp_path)
            assert checksum.startswith("sha256:")
            assert len(checksum) == 19  # "sha256:" + 12 chars
        finally:
            os.unlink(temp_path)

    def test_sha256sum_nonexistent_file(self):
        """Test SHA256 checksum for non-existent file."""
        checksum = sha256sum("nonexistent_file.txt")
        assert checksum == "sha256:FILE_NOT_FOUND"

    @patch("subprocess.getoutput")
    def test_get_git_commit_hash_success(self, mock_subprocess):
        """Test successful git commit hash retrieval."""
        mock_subprocess.return_value = "abc1234"
        result = get_git_commit_hash()
        assert result == "abc1234"
        mock_subprocess.assert_called_once_with("git rev-parse --short HEAD")

    @patch("subprocess.getoutput")
    def test_get_git_commit_hash_failure(self, mock_subprocess):
        """Test git commit hash retrieval failure."""
        mock_subprocess.side_effect = Exception("Git not available")
        result = get_git_commit_hash()
        assert result == "unknown"

    @patch("compliance.model_card_generator.sha256sum")
    @patch("compliance.model_card_generator.get_git_commit_hash")
    def test_collect_metadata(self, mock_git, mock_sha256):
        """Test metadata collection."""
        # Mock git and checksum functions
        mock_git.return_value = "abc123"
        mock_sha256.return_value = "sha256:test123"

        # Mock file existence and stats
        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.stat") as mock_stat:
                mock_stat.return_value.st_size = 1024
                mock_stat.return_value.st_mtime = 1699000000.0

                # Mock log file content
                with patch(
                    "builtins.open",
                    mock_open(read_data='{"confidence": 0.85}\n{"confidence": 0.90}\n'),
                ):
                    meta = collect_metadata()

                    assert meta["model_name"] == "Llama-3-8B-local"
                    assert meta["embedding_model"] == "all-MiniLM-L6-v2"
                    assert meta["taxonomy_version"] == "20251015"
                    assert meta["accuracy"] == 0.82
                    assert meta["avg_confidence"] == 0.875  # Average of 0.85 and 0.90
                    assert meta["created_at"] is not None
                    assert meta["commit_hash"] == "abc123"
                    assert meta["project_version"] == "v0.7.0"
                    assert meta["compliance_standard"] == "SOP 029014 Rev 15.A"
                    assert meta["assistive_mode"] is True
                    assert meta["human_validation_required"] is True
                    assert isinstance(meta["checksums"], list)

    def test_validate_metadata_schema_valid(self):
        """Test schema validation with valid metadata."""
        valid_meta = {
            "model_name": "test-model",
            "embedding_model": "test-embedding",
            "accuracy": 0.85,
            "avg_confidence": 0.90,
            "created_at": "2025-10-29T10:00:00Z",
            "commit_hash": "abc123",
            "project_version": "v1.0.0",
            "checksums": [],
        }

        assert validate_metadata_schema(valid_meta) is True

    def test_validate_metadata_schema_invalid(self):
        """Test schema validation with invalid metadata."""
        invalid_meta = {
            "model_name": "test-model",
            # Missing required fields
            "accuracy": 1.5,  # Invalid range
        }

        assert validate_metadata_schema(invalid_meta) is False

    def test_render_markdown(self):
        """Test markdown rendering."""
        meta = {
            "created_at": "2025-10-29T10:00:00Z",
            "project_version": "v0.7.0",
            "commit_hash": "abc123",
            "model_name": "test-model",
            "embedding_model": "test-embedding",
            "taxonomy_version": "20251015",
            "accuracy": 0.85,
            "avg_confidence": 0.90,
            "checksums": [
                {
                    "file": "test.py",
                    "checksum": "sha256:abc123",
                    "size_bytes": 1024,
                    "modified": "2025-10-29T10:00:00Z",
                }
            ],
            "compliance_standard": "SOP 029014 Rev 15.A",
            "assistive_mode": True,
            "data_privacy": "No PII",
            "human_validation_required": True,
        }

        markdown = render_markdown(meta)

        assert "MTCR AI Model Card" in markdown
        assert "test-model" in markdown
        assert "test-embedding" in markdown
        assert "0.85" in markdown
        assert "0.9" in markdown
        assert "SOP 029014 Rev 15.A" in markdown
        assert "Assistive-only" in markdown
        assert "Required" in markdown

    def test_save_outputs(self):
        """Test saving outputs to files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            meta = {
                "created_at": "2025-10-29T10:00:00Z",
                "commit_hash": "abc123",
                "accuracy": 0.85,
                "avg_confidence": 0.90,
                "checksums": [],
            }

            with patch("compliance.model_card_generator.Path") as mock_path:
                mock_path.return_value.parent.parent.parent = temp_path
                mock_path.return_value.__truediv__ = (
                    lambda self, other: temp_path / other
                )

                outputs = save_outputs(meta)

                # Check that files were created
                assert (temp_path / "compliance").exists()
                assert (temp_path / "data" / "metadata").exists()
                assert (temp_path / "logs").exists()

                # Check output paths
                assert "compliance" in outputs["markdown"]
                assert "metadata" in outputs["json"]
                assert "logs" in outputs["log"]

    @patch("compliance.model_card_generator.sha256sum")
    @patch("compliance.model_card_generator.get_git_commit_hash")
    def test_integration_model_card_generation(self, mock_git, mock_sha256):
        """Integration test for complete model card generation."""
        # Mock git and checksum functions
        mock_git.return_value = "abc123"
        mock_sha256.return_value = "sha256:test123"

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            with patch("compliance.model_card_generator.Path") as mock_path:
                mock_path.return_value.parent.parent.parent = temp_path
                mock_path.return_value.__truediv__ = (
                    lambda self, other: temp_path / other
                )

                # Mock file existence
                with patch("pathlib.Path.exists", return_value=True):
                    with patch("pathlib.Path.stat") as mock_stat:
                        mock_stat.return_value.st_size = 1024
                        mock_stat.return_value.st_mtime = 1699000000.0

                        # Mock log file content
                        with patch(
                            "builtins.open",
                            mock_open(read_data='{"confidence": 0.85}\n'),
                        ):
                            meta = collect_metadata()

                            # Validate schema
                            assert validate_metadata_schema(meta)

                            # Test markdown rendering (mock template file reading)
                            with patch(
                                "pathlib.Path.exists", return_value=False
                            ):  # Template file doesn't exist, use fallback
                                markdown = render_markdown(meta)
                                assert "MTCR AI Model Card" in markdown

                            # Test file saving
                            outputs = save_outputs(meta)
                            assert "compliance" in outputs["markdown"]
                            assert "metadata" in outputs["json"]
                            assert "logs" in outputs["log"]


if __name__ == "__main__":
    pytest.main([__file__])
