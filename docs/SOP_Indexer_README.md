# SOP Indexer (RAG + Guidance Mapping) - Phase 6 (M6)

## Overview

The SOP Indexer provides **Retrieval-Augmented Generation (RAG)** functionality for SOP documents, enabling semantic search and automated mapping of standardized correction reasons to relevant SOP clauses. This module is part of the MTCR Agentic Automation system and supports both ChromaDB and FAISS vector stores.

## Key Features

- **Local Vector Index**: Builds and maintains a local vector index over SOP 029014 and attachments
- **Semantic Search**: Find relevant SOP clauses using natural language queries
- **Reason Mapping**: Automatically map standardized correction reasons to best-matching SOP clauses
- **Dual Backend Support**: ChromaDB (default) and FAISS vector stores
- **Comprehensive Logging**: JSONL audit trails for all mapping decisions
- **Idempotent Operations**: Avoid duplicate embeddings using checksum-based detection
- **Metadata Preservation**: Maintains document revision, effective dates, and traceability

## Architecture

```
SOP Documents → Chunking → Embeddings → Vector Store → Search → Mapping
     ↓              ↓           ↓            ↓          ↓         ↓
  PDF/DOCX    Semantic    Sentence-    ChromaDB/   Similarity  YAML
  Parsing     Chunks    Transformers    FAISS      Scoring   Output
```

## Installation

### Dependencies

The SOP Indexer requires the following Python packages:

```bash
pip install -r requirements.txt
```

Key dependencies:
- `chromadb==0.5.*` - Vector database (default)
- `faiss-cpu==1.8.*` - Alternative vector database
- `sentence-transformers==3.*` - Embedding model
- `pypdf>=4.2` - PDF parsing
- `python-docx>=1.1` - DOCX parsing
- `numpy>=1.24.0` - Numerical operations
- `pyyaml>=6.0` - YAML processing

### Model Download

The system uses `all-MiniLM-L6-v2` by default, which will be automatically downloaded on first use (~80MB).

## Usage

### Command Line Interface

```bash
python -m src.utils.sop_indexer \
  --input_docs "/path/to/sop_029014.pdf" \
               "/path/to/attachment3.pdf" \
               "/path/to/attachment2.docx" \
  --taxonomy_yaml data/taxonomy/reasons.latest.yml \
  --embeddings_dir data/embeddings/sop_index/ \
  --output_mapping data/mappings/reason_to_sop.yml \
  --log_file logs/rag_mapping_202510.jsonl \
  --embedding_model all-MiniLM-L6-v2 \
  --top_k 3 \
  --use_faiss false \
  --verbose true
```

### Python API

```python
from src.utils.sop_indexer import SOPIndexer

# Create indexer
indexer = SOPIndexer(
    embeddings_dir="data/embeddings/sop_index/",
    model_name="all-MiniLM-L6-v2",
    use_faiss=False  # Use ChromaDB
)

# Load and index documents
docs = indexer.load_docs(["/path/to/sop.pdf"])
chunks = indexer.chunk_and_clean(docs)
indexer.embed_and_index(chunks)

# Search for relevant SOP clauses
results = indexer.find_relevant_sop("sampling plan error", top_k=3)
for result in results:
    print(f"{result.sop_ref}: {result.excerpt} (score: {result.score:.3f})")

# Generate reason mappings
indexer.generate_reason_mapping(
    taxonomy_yaml="data/taxonomy/reasons.latest.yml",
    output_path="data/mappings/reason_to_sop.yml",
    log_path="logs/rag_mapping.jsonl"
)
```

## Document Processing

### Supported Formats

- **PDF**: Extracted using `pypdf`
- **DOCX**: Extracted using `python-docx`
- **Metadata**: Automatically extracted from filenames (revision, effective date)

### Chunking Strategy

Documents are split into semantically meaningful chunks using:

- **Section Headers**: Regex pattern `^(?:\d+(?:\.\d+)*\s+|Attachment\s+\d+\s+-\s+|Definitions|Scope|Responsibilities|Monthly Technical Complaints Review)`
- **Max Chunk Size**: 1,200-1,600 characters
- **Metadata Preservation**: Section IDs, page numbers, document revision

### Chunk Metadata

Each chunk includes comprehensive metadata:

```json
{
  "doc_id": "029014",
  "title": "Periodic Technical Complaints Review",
  "section": "4.1.3",
  "section_title": "Monthly quality content review",
  "page": 6,
  "filepath": "/path/to/document.pdf",
  "checksum_sha256": "abc123...",
  "rev": "15.A",
  "effective_date": "2024-10-01T01:00:00",
  "source_type": "pdf",
  "created_at": "2024-10-29T01:15:00.000000Z",
  "model": "all-MiniLM-L6-v2"
}
```

## Vector Stores

### ChromaDB (Default)

- **Pros**: Easy to use, persistent storage, metadata filtering
- **Cons**: Larger memory footprint
- **Use Case**: Development and small to medium datasets

### FAISS

- **Pros**: Fast, memory efficient, optimized for similarity search
- **Cons**: More complex setup, requires manual metadata management
- **Use Case**: Production environments with large datasets

## Search and Retrieval

### Similarity Scoring

- **Method**: Cosine similarity on normalized embeddings
- **Range**: 0.0 (no similarity) to 1.0 (perfect match)
- **Threshold**: Configurable minimum similarity threshold

### SOP Reference Format

- **Main Document**: `"029014 §4.1.3"`
- **Attachments**: `"Attachment 3 - PRE Not Escalated"`
- **Unknown**: `"Unknown"`

## Reason Mapping

### Input Taxonomy

The system expects a YAML taxonomy file with standardized reasons:

```yaml
- id: R_ERRCODE
  label: Incorrect Error Code
  synonyms: ["wrong IMDRF A-code", "mis-coded error", "invalid error code"]

- id: R_SAMPLING
  label: Sampling Plan Error
  synonyms: ["insufficient sample", "sampling error", "sample size issue"]
```

### Output Mapping

Generated mappings include:

```yaml
- reason: Incorrect Error Code
  reason_id: R_ERRCODE
  sop_ref: "029014 §4.1.3"
  excerpt: "Error Code should be the most appropriate IMDRF code..."
  similarity: 0.91
  metadata:
    doc_id: "029014"
    rev: "15.A"
    page: 6
    section: "4.1.3"
    section_title: "Monthly quality content review"
```

## Logging and Audit

### JSONL Log Format

Each mapping decision is logged with:

```json
{
  "timestamp": "2024-10-29T01:15:00.000000Z",
  "reason": "Incorrect Error Code",
  "reason_id": "R_ERRCODE",
  "topk": [
    {
      "sop_ref": "029014 §4.1.3",
      "similarity": 0.91,
      "section": "4.1.3"
    }
  ],
  "chosen_idx": 0,
  "model": "all-MiniLM-L6-v2",
  "thresholds": {"min_similarity": 0.0},
  "checksums": ["029014", "Attachment 3"]
}
```

## Testing

### Unit Tests

Run the comprehensive test suite:

```bash
python -m pytest tests/test_sop_indexer.py -v
```

### Test Coverage

- **Index Building**: Mock corpus with 3 faux sections
- **Query Functionality**: Search for "sampling plan error"
- **Mapping Generation**: Mini taxonomy with "Incorrect Error Code"
- **Audit Logging**: JSONL log verification
- **Idempotency**: Duplicate prevention via checksums

### Demo Script

Run the interactive demo:

```bash
python examples/sop_indexer_demo.py
```

## Configuration

### Environment Variables

- `SOP_INDEXER_MODEL`: Default embedding model (default: `all-MiniLM-L6-v2`)
- `SOP_INDEXER_BACKEND`: Default vector store (default: `chroma`)
- `SOP_INDEXER_VERBOSE`: Enable verbose logging (default: `false`)

### CLI Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--input_docs` | Input document paths | Required |
| `--taxonomy_yaml` | Taxonomy YAML file | Required |
| `--embeddings_dir` | Embeddings storage directory | Required |
| `--output_mapping` | Output mapping YAML file | Required |
| `--log_file` | Log file path | Required |
| `--embedding_model` | Embedding model name | `all-MiniLM-L6-v2` |
| `--top_k` | Number of top results | `3` |
| `--use_faiss` | Use FAISS instead of ChromaDB | `false` |
| `--verbose` | Enable verbose logging | `false` |

## Performance

### Memory Usage

- **ChromaDB**: ~2-4GB for typical SOP corpus
- **FAISS**: ~1-2GB for typical SOP corpus
- **Embeddings**: ~384 dimensions × 4 bytes per float

### Speed

- **Indexing**: ~100-500 chunks per minute
- **Search**: ~10-50ms per query
- **Mapping**: ~1-5 seconds per reason

## Troubleshooting

### Common Issues

1. **Model Download Fails**
   - Check internet connection
   - Verify `sentence-transformers` installation
   - Try manual download: `python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"`

2. **ChromaDB Permission Errors**
   - Ensure write permissions to embeddings directory
   - Check disk space availability

3. **FAISS Index Corruption**
   - Delete `faiss_index.bin` and `metadata.json`
   - Rebuild index from scratch

4. **Low Similarity Scores**
   - Check if documents are properly chunked
   - Verify embedding model compatibility
   - Consider using different embedding model

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
python -m src.utils.sop_indexer --verbose true [other args]
```

## Compliance

### Data Handling

- **Read-Only**: Never modifies original SOP documents
- **Local Processing**: All operations performed locally
- **Checksum Verification**: Document integrity maintained
- **Audit Trails**: Complete logging of all operations

### Security

- **No External APIs**: All processing local
- **Encrypted Storage**: Vector stores can be encrypted
- **Access Control**: File system permissions apply

## Future Enhancements

### Planned Features

- **Multi-language Support**: French/English document processing
- **Advanced Chunking**: Semantic boundary detection
- **Hybrid Search**: Combine semantic and keyword search
- **Real-time Updates**: Incremental index updates
- **Performance Optimization**: GPU acceleration support

### Integration Points

- **M2 AI Review Assistant**: Direct integration for comment analysis
- **M5 Taxonomy Manager**: Automatic taxonomy updates
- **M7 Model Card Generator**: Model metadata tracking

## Support

For issues, questions, or contributions:

1. Check the test suite for usage examples
2. Review the demo script for common patterns
3. Examine the JSONL logs for debugging information
4. Consult the ProjectVision.ts for overall system context

---

**Phase 6 (M6) Status**: ✅ **Completed**  
**Last Updated**: 2025-10-29T01:15:00.000000Z  
**Version**: 1.0.0
