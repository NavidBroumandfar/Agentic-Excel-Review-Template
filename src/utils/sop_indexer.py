"""
SOP Indexer (RAG + Guidance Mapping) - Phase 6 (M6)

This module provides RAG (Retrieval-Augmented Generation) functionality for SOP documents,
including indexing, retrieval, and mapping of standardized correction reasons to relevant SOP clauses.

Key Features:
- Local vector index over SOP 029014 and attachments
- Semantic chunking with metadata preservation
- Reason-to-SOP clause mapping with similarity scores
- Support for both ChromaDB and FAISS vector stores
- Comprehensive logging and audit trails

Created by: Navid Broumandfar (Service Analytics, CHP, bioMérieux)
"""

import os
import re
import json
import hashlib
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
import logging

import pandas as pd
import yaml
import chromadb
from chromadb.config import Settings
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
from docx import Document
import jsonlines

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RawDoc:
    """Raw document structure"""

    filepath: str
    title: str
    content: str
    doc_type: str
    checksum: str
    rev: Optional[str] = None
    effective_date: Optional[str] = None


@dataclass
class Chunk:
    """Document chunk with metadata"""

    content: str
    section: str
    section_title: str
    page: int
    doc_id: str
    title: str
    filepath: str
    checksum: str
    source_type: str
    created_at: str
    model: str
    rev: Optional[str] = None
    effective_date: Optional[str] = None


@dataclass
class RetrievalResult:
    """Result from SOP retrieval"""

    section: str
    section_title: str
    sop_ref: str
    excerpt: str
    score: float
    doc_id: str
    page: int
    rev: Optional[str] = None


class VectorStoreHandle:
    """Abstract interface for vector store operations"""

    def __init__(self, store_type: str, model_name: str):
        self.store_type = store_type
        self.model_name = model_name
        self.embedder = SentenceTransformer(model_name)
        self.dimension = self.embedder.get_sentence_embedding_dimension()

    def add_chunks(self, chunks: List[Chunk]) -> None:
        """Add chunks to the vector store"""
        raise NotImplementedError

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search for similar chunks"""
        raise NotImplementedError

    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        raise NotImplementedError


class ChromaVectorStore(VectorStoreHandle):
    """ChromaDB implementation of vector store"""

    def __init__(self, embeddings_dir: str, model_name: str):
        super().__init__("chroma", model_name)
        self.embeddings_dir = embeddings_dir
        self.client = chromadb.PersistentClient(
            path=embeddings_dir, settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name="sop_index",
            metadata={"model": model_name, "created_at": datetime.now().isoformat()},
        )

    def add_chunks(self, chunks: List[Chunk]) -> None:
        """Add chunks to ChromaDB"""
        if not chunks:
            return

        # Check for existing chunks by checksum to avoid duplicates
        existing_checksums = set()
        try:
            existing = self.collection.get()
            existing_checksums = set(
                existing["metadatas"][i].get("checksum", "")
                for i in range(len(existing["metadatas"]))
            )
        except:
            pass

        # Filter out existing chunks
        new_chunks = [
            chunk for chunk in chunks if chunk.checksum not in existing_checksums
        ]

        if not new_chunks:
            logger.info("All chunks already exist in index, skipping")
            return

        # Prepare data for ChromaDB
        ids = [
            f"{chunk.doc_id}_{chunk.section}_{i}" for i, chunk in enumerate(new_chunks)
        ]
        documents = [chunk.content for chunk in new_chunks]

        # Clean metadata to avoid None values
        metadatas = []
        for chunk in new_chunks:
            metadata = asdict(chunk)
            # Replace None values with empty strings for ChromaDB compatibility
            cleaned_metadata = {}
            for key, value in metadata.items():
                if value is None:
                    cleaned_metadata[key] = ""
                else:
                    cleaned_metadata[key] = value
            metadatas.append(cleaned_metadata)

        # Generate embeddings
        embeddings = self.embedder.encode(documents).tolist()

        # Add to collection
        self.collection.add(
            ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings
        )

        logger.info(f"Added {len(new_chunks)} new chunks to ChromaDB index")

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search ChromaDB for similar chunks"""
        query_embedding = self.embedder.encode([query]).tolist()

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        # Convert to standard format
        search_results = []
        for i in range(len(results["documents"][0])):
            metadata = results["metadatas"][0][i]
            distance = results["distances"][0][i]
            similarity = 1 - distance  # Convert distance to similarity

            search_results.append(
                {
                    "content": results["documents"][0][i],
                    "metadata": metadata,
                    "similarity": similarity,
                    "distance": distance,
                }
            )

        return search_results

    def get_stats(self) -> Dict[str, Any]:
        """Get ChromaDB statistics"""
        try:
            count = self.collection.count()
            return {
                "store_type": "chroma",
                "total_chunks": count,
                "model": self.model_name,
                "dimension": self.dimension,
            }
        except:
            return {"store_type": "chroma", "total_chunks": 0}


class FAISSVectorStore(VectorStoreHandle):
    """FAISS implementation of vector store"""

    def __init__(self, embeddings_dir: str, model_name: str):
        super().__init__("faiss", model_name)
        self.embeddings_dir = embeddings_dir
        self.index_path = os.path.join(embeddings_dir, "faiss_index.bin")
        self.metadata_path = os.path.join(embeddings_dir, "metadata.json")

        # Initialize or load index
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.metadata_path, "r") as f:
                self.metadata = json.load(f)
        else:
            self.index = faiss.IndexFlatIP(
                self.dimension
            )  # Inner product for cosine similarity
            self.metadata = []

    def add_chunks(self, chunks: List[Chunk]) -> None:
        """Add chunks to FAISS index"""
        if not chunks:
            return

        # Check for existing chunks by checksum
        existing_checksums = {meta.get("checksum", "") for meta in self.metadata}
        new_chunks = [
            chunk for chunk in chunks if chunk.checksum not in existing_checksums
        ]

        if not new_chunks:
            logger.info("All chunks already exist in index, skipping")
            return

        # Generate embeddings
        embeddings = self.embedder.encode([chunk.content for chunk in new_chunks])

        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)

        # Add to index
        self.index.add(embeddings.astype("float32"))

        # Update metadata
        for chunk in new_chunks:
            metadata = asdict(chunk)
            # Replace None values with empty strings for consistency
            cleaned_metadata = {}
            for key, value in metadata.items():
                if value is None:
                    cleaned_metadata[key] = ""
                else:
                    cleaned_metadata[key] = value
            self.metadata.append(cleaned_metadata)

        # Save index and metadata
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, "w") as f:
            json.dump(self.metadata, f, indent=2)

        logger.info(f"Added {len(new_chunks)} new chunks to FAISS index")

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search FAISS index for similar chunks"""
        query_embedding = self.embedder.encode([query])
        faiss.normalize_L2(query_embedding)

        scores, indices = self.index.search(query_embedding.astype("float32"), top_k)

        search_results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.metadata):
                metadata = self.metadata[idx]
                search_results.append(
                    {
                        "content": metadata.get("content", ""),
                        "metadata": metadata,
                        "similarity": float(score),
                        "distance": 1 - float(score),
                    }
                )

        return search_results

    def get_stats(self) -> Dict[str, Any]:
        """Get FAISS statistics"""
        return {
            "store_type": "faiss",
            "total_chunks": len(self.metadata),
            "model": self.model_name,
            "dimension": self.dimension,
        }


class SOPIndexer:
    """Main SOP Indexer class"""

    def __init__(
        self,
        embeddings_dir: str,
        model_name: str = "all-MiniLM-L6-v2",
        use_faiss: bool = False,
    ):
        self.embeddings_dir = embeddings_dir
        self.model_name = model_name
        self.use_faiss = use_faiss

        # Initialize vector store
        if use_faiss:
            self.vector_store = FAISSVectorStore(embeddings_dir, model_name)
        else:
            self.vector_store = ChromaVectorStore(embeddings_dir, model_name)

    def compute_sha256(self, filepath: str) -> str:
        """Compute SHA256 checksum of a file"""
        hash_sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def load_docs(self, paths: List[str]) -> List[RawDoc]:
        """Load documents from file paths"""
        docs = []

        for path in paths:
            if not os.path.exists(path):
                logger.warning(f"File not found: {path}")
                continue

            try:
                checksum = self.compute_sha256(path)
                file_ext = Path(path).suffix.lower()

                if file_ext == ".pdf":
                    content = self._extract_pdf_content(path)
                    doc_type = "pdf"
                elif file_ext == ".docx":
                    content = self._extract_docx_content(path)
                    doc_type = "docx"
                else:
                    logger.warning(f"Unsupported file type: {file_ext}")
                    continue

                # Extract title from filename
                title = Path(path).stem

                # Try to extract revision and date from filename
                rev = self._extract_revision(title)
                effective_date = self._extract_effective_date(title)

                docs.append(
                    RawDoc(
                        filepath=path,
                        title=title,
                        content=content,
                        doc_type=doc_type,
                        checksum=checksum,
                        rev=rev,
                        effective_date=effective_date,
                    )
                )

                logger.info(f"Loaded {doc_type}: {title}")

            except Exception as e:
                logger.error(f"Error loading {path}: {e}")
                continue

        return docs

    def _extract_pdf_content(self, filepath: str) -> str:
        """Extract text content from PDF"""
        reader = PdfReader(filepath)
        content = ""
        for page in reader.pages:
            content += page.extract_text() + "\n"
        return content.strip()

    def _extract_docx_content(self, filepath: str) -> str:
        """Extract text content from DOCX"""
        doc = Document(filepath)
        content = ""
        for paragraph in doc.paragraphs:
            content += paragraph.text + "\n"
        return content.strip()

    def _extract_revision(self, title: str) -> Optional[str]:
        """Extract revision from title (e.g., '15.A')"""
        rev_match = re.search(r"rev\s*(\d+\.?\w*)", title, re.IGNORECASE)
        return rev_match.group(1) if rev_match else None

    def _extract_effective_date(self, title: str) -> Optional[str]:
        """Extract effective date from title"""
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", title)
        return date_match.group(1) if date_match else None

    def chunk_and_clean(self, docs: List[RawDoc]) -> List[Chunk]:
        """Chunk documents into semantically meaningful pieces"""
        chunks = []

        # Regex for identifying section headers
        section_pattern = re.compile(
            r"^(?:\d+(?:\.\d+)*\s+|Attachment\s+\d+\s+-\s+|Definitions|Scope|Responsibilities|Monthly Technical Complaints Review)",
            re.MULTILINE,
        )

        for doc in docs:
            # Find all section headers and their positions
            matches = list(section_pattern.finditer(doc.content))

            if not matches:
                # No sections found, treat entire document as one chunk
                section_chunks = self._split_long_content(doc.content, max_length=1600)
                for j, chunk_content in enumerate(section_chunks):
                    if not chunk_content.strip():
                        continue

                    chunks.append(
                        Chunk(
                            content=chunk_content.strip(),
                            section="Unknown",
                            section_title="Full Document",
                            page=1,
                            doc_id=self._extract_doc_id(doc.title),
                            title=doc.title,
                            filepath=doc.filepath,
                            checksum=doc.checksum,
                            source_type=doc.doc_type,
                            created_at=datetime.now().isoformat(),
                            model=self.model_name,
                            rev=doc.rev,
                            effective_date=doc.effective_date,
                        )
                    )
            else:
                # Process each section
                for i, match in enumerate(matches):
                    header = match.group(0)
                    start_pos = match.start()

                    # Find end position (start of next section or end of document)
                    if i + 1 < len(matches):
                        end_pos = matches[i + 1].start()
                    else:
                        end_pos = len(doc.content)

                    content = doc.content[start_pos:end_pos]

                    if not content.strip():
                        continue

                    # Extract section ID and title
                    section_id = self._extract_section_id(header)
                    section_title = self._clean_section_title(header)

                    # Split long sections into smaller chunks
                    section_chunks = self._split_long_content(content, max_length=1600)

                    for j, chunk_content in enumerate(section_chunks):
                        if not chunk_content.strip():
                            continue

                        chunks.append(
                            Chunk(
                                content=chunk_content.strip(),
                                section=section_id,
                                section_title=section_title,
                                page=1,  # TODO: Implement page tracking
                                doc_id=self._extract_doc_id(doc.title),
                                title=doc.title,
                                filepath=doc.filepath,
                                checksum=doc.checksum,
                                source_type=doc.doc_type,
                                created_at=datetime.now().isoformat(),
                                model=self.model_name,
                                rev=doc.rev,
                                effective_date=doc.effective_date,
                            )
                        )

        logger.info(f"Created {len(chunks)} chunks from {len(docs)} documents")
        return chunks

    def _extract_section_id(self, header: str) -> str:
        """Extract section ID from header"""
        # Check for attachment first
        attachment_match = re.search(r"Attachment\s+(\d+)", header, re.IGNORECASE)
        if attachment_match:
            return f"Attachment {attachment_match.group(1)}"

        # Look for patterns like "4.1.3"
        section_match = re.search(r"(\d+(?:\.\d+)*)", header)
        if section_match:
            return section_match.group(1)

        return "Unknown"

    def _clean_section_title(self, header: str) -> str:
        """Clean section title"""
        return header.strip()

    def _split_long_content(self, content: str, max_length: int = 1600) -> List[str]:
        """Split long content into smaller chunks"""
        if len(content) <= max_length:
            return [content]

        chunks = []
        sentences = content.split(". ")

        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk + sentence) <= max_length:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _extract_doc_id(self, title: str) -> str:
        """Extract document ID from title"""
        # Look for SOP number pattern
        sop_match = re.search(r"(\d{6})", title)
        if sop_match:
            return sop_match.group(1)
        return "Unknown"

    def embed_and_index(self, chunks: List[Chunk]) -> None:
        """Build vector index from chunks"""
        logger.info(f"Building vector index with {len(chunks)} chunks...")
        self.vector_store.add_chunks(chunks)
        stats = self.vector_store.get_stats()
        logger.info(f"Index built successfully: {stats}")

    def find_relevant_sop(
        self, reason_text: str, top_k: int = 3
    ) -> List[RetrievalResult]:
        """Find relevant SOP clauses for a given reason"""
        search_results = self.vector_store.search(reason_text, top_k)

        results = []
        for result in search_results:
            metadata = result["metadata"]

            # Format SOP reference
            sop_ref = self._format_sop_reference(metadata)

            results.append(
                RetrievalResult(
                    section=metadata.get("section", ""),
                    section_title=metadata.get("section_title", ""),
                    sop_ref=sop_ref,
                    excerpt=(
                        result["content"][:500] + "..."
                        if len(result["content"]) > 500
                        else result["content"]
                    ),
                    score=result["similarity"],
                    doc_id=metadata.get("doc_id", ""),
                    page=metadata.get("page", 1),
                    rev=metadata.get("rev"),
                )
            )

        return results

    def _format_sop_reference(self, metadata: Dict[str, Any]) -> str:
        """Format SOP reference string"""
        doc_id = metadata.get("doc_id", "")
        section = metadata.get("section", "")

        if doc_id and section and doc_id != "Unknown":
            return f"{doc_id} §{section}"
        elif section:
            return section
        else:
            return "Unknown"

    def generate_reason_mapping(
        self, taxonomy_yaml: str, output_path: str, log_path: str, top_k: int = 3
    ) -> None:
        """Generate mapping from reasons to SOP clauses"""

        # Load taxonomy
        with open(taxonomy_yaml, "r", encoding="utf-8") as f:
            taxonomy = yaml.safe_load(f)

        if not isinstance(taxonomy, list):
            logger.error("Taxonomy should be a list of reason objects")
            return

        mappings = []
        log_entries = []

        for reason_item in taxonomy:
            if not isinstance(reason_item, dict) or "label" not in reason_item:
                continue

            reason_label = reason_item["label"]
            reason_id = reason_item.get("id", "")
            synonyms = reason_item.get("synonyms", [])

            # Search for this reason and its synonyms
            search_queries = [reason_label] + synonyms
            all_results = []

            for query in search_queries:
                if query.strip():
                    results = self.find_relevant_sop(query, top_k)
                    all_results.extend(results)

            # Remove duplicates and sort by score
            unique_results = {}
            for result in all_results:
                key = f"{result.doc_id}_{result.section}"
                if (
                    key not in unique_results
                    or result.score > unique_results[key].score
                ):
                    unique_results[key] = result

            sorted_results = sorted(
                unique_results.values(), key=lambda x: x.score, reverse=True
            )

            # Take the best result
            if sorted_results:
                best_result = sorted_results[0]

                mapping = {
                    "reason": reason_label,
                    "reason_id": reason_id,
                    "sop_ref": best_result.sop_ref,
                    "excerpt": best_result.excerpt,
                    "similarity": best_result.score,
                    "metadata": {
                        "doc_id": best_result.doc_id,
                        "rev": best_result.rev,
                        "page": best_result.page,
                        "section": best_result.section,
                        "section_title": best_result.section_title,
                    },
                }
                mappings.append(mapping)

                # Log entry
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "reason": reason_label,
                    "reason_id": reason_id,
                    "topk": [
                        {
                            "sop_ref": r.sop_ref,
                            "similarity": r.score,
                            "section": r.section,
                        }
                        for r in sorted_results[:top_k]
                    ],
                    "chosen_idx": 0,
                    "model": self.model_name,
                    "thresholds": {"min_similarity": 0.0},
                    "checksums": [r.doc_id for r in sorted_results[:top_k]],
                }
                log_entries.append(log_entry)

                logger.info(
                    f"Mapped '{reason_label}' to {best_result.sop_ref} (similarity: {best_result.score:.3f})"
                )
            else:
                logger.warning(f"No relevant SOP found for reason: {reason_label}")

        # Save mappings
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(mappings, f, default_flow_style=False, allow_unicode=True)

        # Save logs
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with jsonlines.open(log_path, "w") as writer:
            for entry in log_entries:
                writer.write(entry)

        logger.info(f"Generated {len(mappings)} reason mappings")
        logger.info(f"Saved mappings to: {output_path}")
        logger.info(f"Saved logs to: {log_path}")


def cli():
    """Command line interface"""
    parser = argparse.ArgumentParser(description="SOP Indexer - RAG + Guidance Mapping")

    parser.add_argument(
        "--input_docs", nargs="+", required=True, help="Input document paths"
    )
    parser.add_argument(
        "--taxonomy_yaml", required=True, help="Path to taxonomy YAML file"
    )
    parser.add_argument(
        "--embeddings_dir", required=True, help="Directory for embeddings storage"
    )
    parser.add_argument(
        "--output_mapping", required=True, help="Output mapping YAML file"
    )
    parser.add_argument("--log_file", required=True, help="Log file path")
    parser.add_argument(
        "--embedding_model", default="all-MiniLM-L6-v2", help="Embedding model name"
    )
    parser.add_argument(
        "--top_k", type=int, default=3, help="Number of top results to return"
    )
    parser.add_argument(
        "--use_faiss", action="store_true", help="Use FAISS instead of ChromaDB"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create indexer
    indexer = SOPIndexer(
        embeddings_dir=args.embeddings_dir,
        model_name=args.embedding_model,
        use_faiss=args.use_faiss,
    )

    # Load and process documents
    logger.info("Loading documents...")
    docs = indexer.load_docs(args.input_docs)

    if not docs:
        logger.error("No documents loaded")
        return

    logger.info("Chunking documents...")
    chunks = indexer.chunk_and_clean(docs)

    if not chunks:
        logger.error("No chunks created")
        return

    logger.info("Building vector index...")
    indexer.embed_and_index(chunks)

    logger.info("Generating reason mappings...")
    indexer.generate_reason_mapping(
        taxonomy_yaml=args.taxonomy_yaml,
        output_path=args.output_mapping,
        log_path=args.log_file,
        top_k=args.top_k,
    )

    logger.info("SOP indexing completed successfully!")


if __name__ == "__main__":
    cli()
