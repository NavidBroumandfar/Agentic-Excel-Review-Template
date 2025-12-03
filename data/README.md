# Data Directory

This directory should contain your Excel workbook and SOP documents for the agentic review pipeline.

## Required Files

### 1. Excel Workbook

Place your review workbook here:
- **File name**: `Sample_Review_Workbook.xlsx` (or configure in `config.json`)
- **Sheet name**: Should contain a sheet named `ReviewSheet` (or configure in `config.json`)
- **Structure**: The sheet should have:
  - Header row with column names
  - Review records (rows)
  - Comment or description fields for AI analysis

**Example structure**:
```
| ID | Date       | Category | ReviewComment             | Status |
|----|------------|----------|---------------------------|--------|
| 1  | 2025-01-15 | TypeA    | Needs clarification...    | Open   |
| 2  | 2025-01-16 | TypeB    | Review completed...       | Closed |
```

### 2. SOP Documents (Optional)

Place your SOP/policy documents in `data/docs/`:
- Supported formats: PDF, DOCX, TXT
- These documents will be indexed by the RAG system
- They provide context for AI suggestions

Example structure:
```
data/
├── Sample_Review_Workbook.xlsx
└── docs/
    ├── SOP-EXAMPLE-001.pdf
    ├── SOP-EXAMPLE-002.pdf
    └── Guidelines.docx
```

## Embeddings

The `embeddings/` directory is automatically created when you run the SOP indexer.
It contains the vector database for RAG:
- ChromaDB or FAISS index files
- Automatically generated and managed

## Metadata

The `metadata/` directory contains:
- Model summaries (JSON)
- Configuration snapshots
- Automatically generated

## Outputs

The `outputs/` directory contains:
- Generated reports
- Publication drafts
- Correction summaries

---

**Note**: This template does not include real data. You must provide your own Excel workbook and SOP documents.

For a quick test, you can create a simple Excel file with dummy data matching the structure described above.

