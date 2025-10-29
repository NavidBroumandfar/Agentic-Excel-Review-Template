"""
Unit tests for SOP Indexer (RAG + Guidance Mapping) - Phase 6 (M6)

Tests cover:
- Index building with mock corpus
- Query functionality
- Mapping generation
- Audit logging
- Idempotency
"""

import os
import tempfile
import shutil
import pytest
import yaml
import json
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Import the modules to test
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.sop_indexer import (
    SOPIndexer,
    RawDoc,
    Chunk,
    RetrievalResult,
    ChromaVectorStore,
    FAISSVectorStore,
)


class TestSOPIndexer:
    """Test cases for SOPIndexer class"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_docs(self):
        """Create mock documents for testing"""
        return [
            RawDoc(
                filepath="/mock/sop_029014.pdf",
                title="029014 - Periodic Technical Complaints Review",
                content="""
                4.1.3 Monthly quality content review
                The review is limited to the evaluation of the following fields:
                - Error Code should be the most appropriate IMDRF code
                - Product information must be accurate and complete
                - Sampling plan must follow golden rules
                
                4.2.1 Error Code Validation
                Error codes must be validated against IMDRF taxonomy.
                Incorrect error codes lead to regulatory non-compliance.
                """,
                doc_type="pdf",
                checksum="mock_checksum_1",
                rev="15.A",
                effective_date="2024-10-01",
            ),
            RawDoc(
                filepath="/mock/attachment2.docx",
                title="Attachment 2 - Golden Rules for Determination of Sampling Plan",
                content="""
                Golden Rules for Sampling Plan
                
                1. Sampling must be statistically valid
                2. Sample size must meet regulatory requirements
                3. Sampling plan errors must be corrected immediately
                
                Sampling Plan Error Types:
                - Insufficient sample size
                - Non-representative sampling
                - Missing sampling justification
                """,
                doc_type="docx",
                checksum="mock_checksum_2",
                rev="2.0",
                effective_date="2024-09-15",
            ),
            RawDoc(
                filepath="/mock/attachment3.pdf",
                title="Attachment 3 - TC Self-Review Dashboard User Guide",
                content="""
                Dashboard Error Types and Fixes
                
                PRE Not Escalated:
                - Error: PRE cases not properly escalated
                - Fix: Ensure escalation criteria are met
                
                UDI-DI Missing:
                - Error: UDI-DI field is empty or invalid
                - Fix: Populate UDI-DI with correct device identifier
                
                Misleading Product Info:
                - Error: Product information is misleading
                - Fix: Update product description to be accurate
                """,
                doc_type="pdf",
                checksum="mock_checksum_3",
                rev="1.5",
                effective_date="2024-08-20",
            ),
        ]

    @pytest.fixture
    def mock_taxonomy(self, temp_dir):
        """Create mock taxonomy YAML file"""
        taxonomy = [
            {
                "id": "R_ERRCODE",
                "label": "Incorrect Error Code",
                "synonyms": [
                    "wrong IMDRF A-code",
                    "mis-coded error",
                    "invalid error code",
                ],
            },
            {
                "id": "R_SAMPLING",
                "label": "Sampling Plan Error",
                "synonyms": [
                    "insufficient sample",
                    "sampling error",
                    "sample size issue",
                ],
            },
            {
                "id": "R_PRE_NOT_ESCALATED",
                "label": "PRE Not Escalated",
                "synonyms": ["PRE escalation missing", "not escalated PRE"],
            },
        ]

        taxonomy_path = os.path.join(temp_dir, "reasons.latest.yml")
        with open(taxonomy_path, "w", encoding="utf-8") as f:
            yaml.dump(taxonomy, f, default_flow_style=False)

        return taxonomy_path

    def test_compute_sha256(self, temp_dir):
        """Test SHA256 computation"""
        indexer = SOPIndexer(temp_dir)

        # Create a test file
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test content")

        checksum = indexer.compute_sha256(test_file)
        assert len(checksum) == 64  # SHA256 produces 64-character hex string
        assert isinstance(checksum, str)

    def test_extract_revision(self, temp_dir):
        """Test revision extraction from titles"""
        indexer = SOPIndexer(temp_dir)

        test_cases = [
            ("029014 rev 15.A", "15.A"),
            ("Document rev 2.0", "2.0"),
            ("No revision here", None),
            ("rev 1.5 effective", "1.5"),
        ]

        for title, expected in test_cases:
            result = indexer._extract_revision(title)
            assert result == expected

    def test_extract_effective_date(self, temp_dir):
        """Test effective date extraction from titles"""
        indexer = SOPIndexer(temp_dir)

        test_cases = [
            ("029014 effective 2024-10-01", "2024-10-01"),
            ("Document 2024-09-15", "2024-09-15"),
            ("No date here", None),
            ("2024-08-20 effective", "2024-08-20"),
        ]

        for title, expected in test_cases:
            result = indexer._extract_effective_date(title)
            assert result == expected

    def test_extract_section_id(self, temp_dir):
        """Test section ID extraction"""
        indexer = SOPIndexer(temp_dir)

        test_cases = [
            ("4.1.3 Monthly quality content review", "4.1.3"),
            ("Attachment 3 - Dashboard Guide", "Attachment 3"),
            ("Definitions", "Unknown"),
            ("1.2.3.4 Section", "1.2.3.4"),
            ("Attachment 2 - Golden Rules", "Attachment 2"),
        ]

        for header, expected in test_cases:
            result = indexer._extract_section_id(header)
            assert result == expected

    def test_chunk_and_clean(self, temp_dir, mock_docs):
        """Test document chunking functionality"""
        indexer = SOPIndexer(temp_dir)
        chunks = indexer.chunk_and_clean(mock_docs)

        assert len(chunks) > 0
        assert all(isinstance(chunk, Chunk) for chunk in chunks)

        # Check that chunks have required metadata
        for chunk in chunks:
            assert chunk.content
            assert chunk.section
            assert chunk.doc_id
            assert chunk.checksum
            assert chunk.model == "all-MiniLM-L6-v2"

        # Check that we have chunks from different sections
        sections = {chunk.section for chunk in chunks}
        assert len(sections) > 1  # Should have multiple sections

    def test_split_long_content(self, temp_dir):
        """Test content splitting for long text"""
        indexer = SOPIndexer(temp_dir)

        # Test short content (should not split)
        short_content = "This is short content."
        chunks = indexer._split_long_content(short_content, max_length=100)
        assert len(chunks) == 1
        assert chunks[0] == short_content

        # Test long content (should split)
        long_content = ". ".join([f"Sentence {i}" for i in range(100)])
        chunks = indexer._split_long_content(long_content, max_length=200)
        assert len(chunks) > 1
        assert all(len(chunk) <= 200 for chunk in chunks)

    @patch("src.utils.sop_indexer.SentenceTransformer")
    def test_chroma_vector_store(self, mock_transformer, temp_dir):
        """Test ChromaDB vector store functionality"""
        # Mock the transformer
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_model.encode.return_value = [[0.1] * 384]  # Mock embedding
        mock_transformer.return_value = mock_model

        # Create vector store
        store = ChromaVectorStore(temp_dir, "all-MiniLM-L6-v2")

        # Create test chunks
        chunks = [
            Chunk(
                content="Test content 1",
                section="4.1.3",
                section_title="Test Section",
                page=1,
                doc_id="029014",
                title="Test Doc",
                filepath="/test/path",
                checksum="test_checksum_1",
                source_type="pdf",
                created_at="2024-01-01T00:00:00",
                model="test-model",
            ),
            Chunk(
                content="Test content 2",
                section="4.2.1",
                section_title="Another Section",
                page=2,
                doc_id="029014",
                title="Test Doc",
                filepath="/test/path",
                checksum="test_checksum_2",
                source_type="pdf",
                created_at="2024-01-01T00:00:00",
                model="test-model",
            ),
        ]

        # Test adding chunks
        store.add_chunks(chunks)

        # Test search
        results = store.search("test query", top_k=2)
        assert len(results) <= 2

        # Test stats
        stats = store.get_stats()
        assert stats["store_type"] == "chroma"
        assert "total_chunks" in stats

    @patch("src.utils.sop_indexer.SentenceTransformer")
    def test_faiss_vector_store(self, mock_transformer, temp_dir):
        """Test FAISS vector store functionality"""
        # Mock the transformer
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_model.encode.return_value = np.array([[0.1] * 384])  # Mock embedding
        mock_transformer.return_value = mock_model

        # Create vector store
        store = FAISSVectorStore(temp_dir, "all-MiniLM-L6-v2")

        # Create test chunks
        chunks = [
            Chunk(
                content="Test content 1",
                section="4.1.3",
                section_title="Test Section",
                page=1,
                doc_id="029014",
                title="Test Doc",
                filepath="/test/path",
                checksum="test_checksum_1",
                source_type="pdf",
                created_at="2024-01-01T00:00:00",
                model="test-model",
            )
        ]

        # Test adding chunks
        store.add_chunks(chunks)

        # Test search
        results = store.search("test query", top_k=1)
        assert len(results) <= 1

        # Test stats
        stats = store.get_stats()
        assert stats["store_type"] == "faiss"
        assert "total_chunks" in stats

    @patch("src.utils.sop_indexer.SentenceTransformer")
    def test_find_relevant_sop(self, mock_transformer, temp_dir, mock_docs):
        """Test SOP retrieval functionality"""
        # Mock the transformer
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_model.encode.return_value = np.array([[0.1] * 384])
        mock_transformer.return_value = mock_model

        # Create indexer and process documents
        indexer = SOPIndexer(temp_dir)
        chunks = indexer.chunk_and_clean(mock_docs)
        indexer.embed_and_index(chunks)

        # Test search
        results = indexer.find_relevant_sop("sampling plan error", top_k=3)

        assert isinstance(results, list)
        assert len(results) <= 3

        for result in results:
            assert isinstance(result, RetrievalResult)
            assert result.sop_ref
            assert result.excerpt
            assert 0 <= result.score <= 1
            assert result.doc_id

    @patch("src.utils.sop_indexer.SentenceTransformer")
    def test_generate_reason_mapping(
        self, mock_transformer, temp_dir, mock_docs, mock_taxonomy
    ):
        """Test reason mapping generation"""
        # Mock the transformer
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_model.encode.return_value = np.array([[0.1] * 384])
        mock_transformer.return_value = mock_model

        # Create indexer and process documents
        indexer = SOPIndexer(temp_dir)
        chunks = indexer.chunk_and_clean(mock_docs)
        indexer.embed_and_index(chunks)

        # Generate mappings
        output_path = os.path.join(temp_dir, "reason_to_sop.yml")
        log_path = os.path.join(temp_dir, "rag_mapping.jsonl")

        indexer.generate_reason_mapping(
            taxonomy_yaml=mock_taxonomy,
            output_path=output_path,
            log_path=log_path,
            top_k=3,
        )

        # Check output files exist
        assert os.path.exists(output_path)
        assert os.path.exists(log_path)

        # Check mapping YAML structure
        with open(output_path, "r", encoding="utf-8") as f:
            mappings = yaml.safe_load(f)

        assert isinstance(mappings, list)
        assert len(mappings) > 0

        for mapping in mappings:
            assert "reason" in mapping
            assert "sop_ref" in mapping
            assert "excerpt" in mapping
            assert "similarity" in mapping
            assert "metadata" in mapping
            assert 0 <= mapping["similarity"] <= 1

        # Check log file structure
        with open(log_path, "r") as f:
            log_entries = [json.loads(line) for line in f]

        assert len(log_entries) > 0

        for entry in log_entries:
            assert "timestamp" in entry
            assert "reason" in entry
            assert "topk" in entry
            assert "chosen_idx" in entry
            assert "model" in entry

    @patch("src.utils.sop_indexer.SentenceTransformer")
    def test_idempotency(self, mock_transformer, temp_dir, mock_docs):
        """Test that re-running with same inputs doesn't duplicate embeddings"""
        # Mock the transformer
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_model.encode.return_value = np.array([[0.1] * 384])
        mock_transformer.return_value = mock_model

        # Create indexer
        indexer = SOPIndexer(temp_dir)
        chunks = indexer.chunk_and_clean(mock_docs)

        # First run
        indexer.embed_and_index(chunks)
        stats1 = indexer.vector_store.get_stats()

        # Second run with same chunks
        indexer.embed_and_index(chunks)
        stats2 = indexer.vector_store.get_stats()

        # Should have same number of chunks (no duplicates)
        assert stats1["total_chunks"] == stats2["total_chunks"]

    def test_format_sop_reference(self, temp_dir):
        """Test SOP reference formatting"""
        indexer = SOPIndexer(temp_dir)

        test_cases = [
            ({"doc_id": "029014", "section": "4.1.3"}, "029014 §4.1.3"),
            ({"section": "Attachment 3"}, "Attachment 3"),
            ({}, "Unknown"),
            ({"doc_id": "Unknown", "section": "4.1.3"}, "4.1.3"),
            ({"doc_id": "029014", "section": ""}, "Unknown"),
        ]

        for metadata, expected in test_cases:
            result = indexer._format_sop_reference(metadata)
            assert result == expected

    def test_extract_doc_id(self, temp_dir):
        """Test document ID extraction"""
        indexer = SOPIndexer(temp_dir)

        test_cases = [
            ("029014 - Periodic Technical Complaints Review", "029014"),
            ("Document 123456", "123456"),
            ("No number here", "Unknown"),
            ("SOP 789012 effective", "789012"),
        ]

        for title, expected in test_cases:
            result = indexer._extract_doc_id(title)
            assert result == expected


class TestMockCorpus:
    """Test with mock corpus as specified in requirements"""

    @pytest.fixture
    def mock_corpus(self):
        """Create mock corpus with 3 faux sections"""
        return [
            RawDoc(
                filepath="/mock/sop.pdf",
                title="029014 - Periodic Technical Complaints Review",
                content="""
                4.1.3 Error Code Validation
                Error Code should be the most appropriate IMDRF code.
                Incorrect error codes must be corrected immediately.
                
                4.2.1 Sampling Plan Rules
                Sampling must follow golden rules for determination.
                Sample size must be statistically valid.
                
                Attachment 2 - Golden Rules
                Golden rules for sampling plan determination.
                """,
                doc_type="pdf",
                checksum="mock_checksum",
                rev="15.A",
            )
        ]

    @patch("src.utils.sop_indexer.SentenceTransformer")
    def test_mock_corpus_indexing(self, mock_transformer, mock_corpus, temp_dir):
        """Test index building with mock corpus"""
        # Mock the transformer
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_model.encode.return_value = np.array([[0.1] * 384])
        mock_transformer.return_value = mock_model

        # Create indexer
        indexer = SOPIndexer(temp_dir)
        chunks = indexer.chunk_and_clean(mock_corpus)
        indexer.embed_and_index(chunks)

        # Verify index has documents
        stats = indexer.vector_store.get_stats()
        assert stats["total_chunks"] > 0

        # Verify metadata keys are present
        results = indexer.find_relevant_sop("error code", top_k=1)
        if results:
            result = results[0]
            assert hasattr(result, "section")
            assert hasattr(result, "sop_ref")
            assert hasattr(result, "excerpt")
            assert hasattr(result, "score")

    @patch("src.utils.sop_indexer.SentenceTransformer")
    def test_sampling_plan_query(self, mock_transformer, mock_corpus, temp_dir):
        """Test that sampling plan query returns Attachment 2 reference"""
        # Mock the transformer
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_model.encode.return_value = np.array([[0.1] * 384])
        mock_transformer.return_value = mock_model

        # Create indexer
        indexer = SOPIndexer(temp_dir)
        chunks = indexer.chunk_and_clean(mock_corpus)
        indexer.embed_and_index(chunks)

        # Search for sampling plan
        results = indexer.find_relevant_sop("sampling plan error", top_k=3)

        # Should find references to sampling rules
        assert len(results) > 0
        # At least one result should mention sampling or golden rules
        sampling_mentioned = any(
            "sampling" in result.excerpt.lower() or "golden" in result.excerpt.lower()
            for result in results
        )
        assert sampling_mentioned


if __name__ == "__main__":
    pytest.main([__file__])
