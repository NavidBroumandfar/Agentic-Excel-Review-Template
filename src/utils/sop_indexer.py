# ⚠️ Compliance Notice:
# Assistive mode only. Do NOT overwrite validated cells or macros in `MTCR Data.xlsm`.
# AI outputs must be written only to new columns prefixed with "AI_".
# All inferences are logged for traceability and QA review.

"""
SOP Indexer for RAG-based retrieval of SOP documents and attachments.
Builds ChromaDB index from PDF and DOCX files for context retrieval.
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import pypdf
from docx import Document
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SOPIndexer:
    """Builds and manages ChromaDB index for SOP document retrieval."""

    def __init__(
        self,
        src_dir: str = "data/raw",
        index_dir: str = "data/embeddings",
        model_name: str = "all-MiniLM-L6-v2",
    ):
        """
        Initialize SOP indexer.

        Args:
            src_dir: Directory containing SOP documents (PDF, DOCX)
            index_dir: Directory to store ChromaDB index
            model_name: Sentence transformer model for embeddings
        """
        self.src_dir = Path(src_dir)
        self.index_dir = Path(index_dir)
        self.model_name = model_name
        self.embedding_model = None
        self.chroma_client = None
        self.collection = None

        # Create directories if they don't exist
        self.src_dir.mkdir(parents=True, exist_ok=True)
        self.index_dir.mkdir(parents=True, exist_ok=True)

    def _load_embedding_model(self):
        """Load the sentence transformer model."""
        if self.embedding_model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.embedding_model = SentenceTransformer(self.model_name)

    def _init_chroma_client(self):
        """Initialize ChromaDB client and collection."""
        if self.chroma_client is None:
            logger.info("Initializing ChromaDB client")
            self.chroma_client = chromadb.PersistentClient(
                path=str(self.index_dir), settings=Settings(anonymized_telemetry=False)
            )

        if self.collection is None:
            try:
                self.collection = self.chroma_client.get_collection("sop_documents")
                logger.info("Loaded existing SOP collection")
            except ValueError:
                self.collection = self.chroma_client.create_collection(
                    name="sop_documents",
                    metadata={
                        "description": "SOP documents and attachments for MTCR review"
                    },
                )
                logger.info("Created new SOP collection")

    def _extract_text_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file."""
        try:
            text = ""
            with open(file_path, "rb") as file:
                pdf_reader = pypdf.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {e}")
            return ""

    def _extract_text_from_docx(self, file_path: Path) -> str:
        """Extract text from DOCX file."""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from DOCX {file_path}: {e}")
            return ""

    def _extract_text_from_file(self, file_path: Path) -> str:
        """Extract text from file based on extension."""
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            return self._extract_text_from_pdf(file_path)
        elif suffix == ".docx":
            return self._extract_text_from_docx(file_path)
        else:
            logger.warning(f"Unsupported file type: {suffix}")
            return ""

    def _chunk_text(
        self, text: str, chunk_size: int = 1000, overlap: int = 200
    ) -> List[str]:
        """Split text into overlapping chunks for better retrieval."""
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]

            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind(".")
                last_newline = chunk.rfind("\n")
                break_point = max(last_period, last_newline)
                if break_point > start + chunk_size // 2:  # Don't make chunks too small
                    chunk = chunk[: break_point + 1]
                    end = start + break_point + 1

            chunks.append(chunk.strip())
            start = end - overlap

        return chunks

    def _get_file_hash(self, file_path: Path) -> str:
        """Get MD5 hash of file for change detection."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def build_index(self) -> Dict[str, Any]:
        """
        Build ChromaDB index from SOP documents.

        Returns:
            Dictionary with build statistics
        """
        logger.info(f"Building SOP index from {self.src_dir}")

        # Initialize components
        self._load_embedding_model()
        self._init_chroma_client()

        # Find all supported files
        supported_extensions = {".pdf", ".docx"}
        files = []
        for ext in supported_extensions:
            files.extend(self.src_dir.glob(f"**/*{ext}"))

        if not files:
            logger.warning(f"No supported files found in {self.src_dir}")
            return {"status": "no_files", "files_processed": 0}

        logger.info(f"Found {len(files)} files to process")

        # Load existing metadata if available
        metadata_file = self.index_dir / "file_metadata.json"
        existing_metadata = {}
        if metadata_file.exists():
            with open(metadata_file, "r") as f:
                existing_metadata = json.load(f)

        processed_files = 0
        total_chunks = 0
        new_files = []

        for file_path in files:
            try:
                # Check if file has changed
                current_hash = self._get_file_hash(file_path)
                if (
                    str(file_path) in existing_metadata
                    and existing_metadata[str(file_path)] == current_hash
                ):
                    logger.info(f"Skipping unchanged file: {file_path.name}")
                    continue

                logger.info(f"Processing: {file_path.name}")

                # Extract text
                text = self._extract_text_from_file(file_path)
                if not text:
                    logger.warning(f"No text extracted from {file_path.name}")
                    continue

                # Chunk text
                chunks = self._chunk_text(text)
                logger.info(f"Created {len(chunks)} chunks from {file_path.name}")

                # Generate embeddings and add to collection
                embeddings = self.embedding_model.encode(chunks).tolist()

                # Prepare metadata
                chunk_metadata = []
                chunk_ids = []
                for i, chunk in enumerate(chunks):
                    chunk_id = f"{file_path.stem}_{i}"
                    metadata = {
                        "file_path": str(file_path),
                        "file_name": file_path.name,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "file_type": file_path.suffix.lower(),
                    }
                    chunk_metadata.append(metadata)
                    chunk_ids.append(chunk_id)

                # Add to collection
                self.collection.add(
                    embeddings=embeddings,
                    documents=chunks,
                    metadatas=chunk_metadata,
                    ids=chunk_ids,
                )

                # Update metadata
                existing_metadata[str(file_path)] = current_hash
                processed_files += 1
                total_chunks += len(chunks)
                new_files.append(file_path.name)

            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                continue

        # Save updated metadata
        with open(metadata_file, "w") as f:
            json.dump(existing_metadata, f, indent=2)

        result = {
            "status": "success",
            "files_processed": processed_files,
            "total_chunks": total_chunks,
            "new_files": new_files,
            "index_path": str(self.index_dir),
        }

        logger.info(f"Index build complete: {result}")
        return result

    def retrieve_context(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context chunks for a query.

        Args:
            query: Search query
            k: Number of chunks to retrieve

        Returns:
            List of relevant chunks with metadata
        """
        if self.collection is None:
            self._init_chroma_client()

        if self.embedding_model is None:
            self._load_embedding_model()

        # Generate query embedding
        query_embedding = self.embedding_model.encode([query]).tolist()[0]

        # Search collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents", "metadatas", "distances"],
        )

        # Format results
        context_chunks = []
        for i in range(len(results["documents"][0])):
            chunk = {
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
            }
            context_chunks.append(chunk)

        return context_chunks


def build_index(
    src_dir: str = "data/raw", index_dir: str = "data/embeddings"
) -> Dict[str, Any]:
    """
    Convenience function to build SOP index.

    Args:
        src_dir: Source directory containing SOP documents
        index_dir: Directory to store the index

    Returns:
        Build statistics dictionary
    """
    indexer = SOPIndexer(src_dir, index_dir)
    return indexer.build_index()


if __name__ == "__main__":
    # Example usage
    result = build_index()
    print(json.dumps(result, indent=2))
