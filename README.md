# Agentic Excel Review Template

A modular agentic AI pipeline that reviews rows in an Excel workbook using RAG + local LLMs, with safe read-only behavior and full logging. This is a generic, open-source template demonstrating how to build an AI-assisted review process for any validated Excel-based workflow.

## Author

**Navid Broumandfar**  
*AI Systems & Cognitive Automation Architect | Applied AI Engineer | Data Science MSc*

This system demonstrates production-grade architecture for agentic AI workflows with local LLM integration, RAG, and compliance-focused design.

---

## 🎯 What This Project Is

This is a **modular agentic AI pipeline** designed for Excel-based review processes. It demonstrates:

- **Safe, read-only Excel ingestion** with automatic header detection
- **RAG (Retrieval-Augmented Generation)** over SOP-like documents  
- **Local LLM integration** via LM Studio (no cloud dependencies)
- **Agentic orchestration** with step-by-step logging
- **Compliance-focused design**: All AI outputs go to new `AI_*` columns, never modifying validated cells

### Use Cases

This template is ideal for:
- Monthly review processes (quality, compliance, audit)
- Excel workbooks with comment fields requiring interpretation
- Teams needing AI assistance without cloud data sharing
- Organizations with validated Excel workflows that need AI augmentation

---

## 🚀 Key Features

### ✅ Excel Reader (Module 1)
- Read-only access to Excel workbooks
- Automatic header detection and data profiling
- CSV preview export for downstream processing
- Zero modification of source files

### 🤖 AI Review Assistant (Module 2)
- RAG-based context retrieval from local document corpus
- LM Studio integration for local inference
- Structured output: suggested actions, confidence scores, rationale
- JSONL logging for full audit trail

### 📝 Safe Writer (Module 3)
- Writes AI suggestions to new columns prefixed with `AI_`
- Never overwrites validated cells
- Backup creation before any write operation

### 📊 Logging & Traceability (Module 4)
- Centralized JSONL log management
- Monthly metrics aggregation
- Tableau-ready CSV exports

### 🧠 Advanced Modules
- **Taxonomy Manager (M5)**: Standardized classification with fuzzy matching
- **SOP Indexer (M6)**: ChromaDB/FAISS vector search over documents
- **Model Card Generator (M7)**: Compliance documentation automation
- **Correction Tracker (M8)**: AI vs. human decision comparison
- **Publication Agent (M9)**: Automated report generation (HTML/email)
- **Orchestrator (M10)**: End-to-end pipeline execution

### 💬 Streamlit UI (Module 11)
- Interactive web interface for reviewing results
- Chat with your Excel data using local LLM
- KPI dashboard and visualization
- Zero-write mode for safety

---

## 📁 Architecture

```
src/
 ├── ai/
 │   ├── review_assistant.py       # RAG + LLM inference
 │   ├── correction_tracker.py     # AI vs human comparison
 │   ├── publication_agent.py      # Report generation
 │   └── orchestrator.py           # Pipeline orchestration
 ├── excel/
 │   ├── excel_reader.py           # Safe read-only Excel access
 │   └── excel_writer.py           # AI_ column writer
 ├── utils/
 │   ├── sop_indexer.py            # RAG document indexing
 │   ├── taxonomy_manager.py       # Classification management
 │   ├── config_loader.py          # Configuration
 │   └── lmstudio_smoketest.py     # LM Studio connectivity test
 ├── logging/
 │   └── log_manager.py            # Centralized JSONL logging
 ├── compliance/
 │   └── model_card_generator.py   # Model documentation
 └── ui/
     └── excel_review_app.py       # Streamlit UI
```

---

## 🛠️ Quick Start

### Prerequisites

1. **Python 3.11+**
2. **LM Studio** (for local LLM inference)
   - Download from [lmstudio.ai](https://lmstudio.ai)
   - Load a model (e.g., Llama 3 or Mistral)
   - Start the local server (default: `http://127.0.0.1:1234/v1`)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/agentic-excel-review-template.git
   cd agentic-excel-review-template
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare your data**
   - Place your Excel workbook in `./data/` (e.g., `Sample_Review_Workbook.xlsx`)
   - Place any SOP documents in `./data/docs/` for RAG indexing
   - Update `config.json` with your file paths

4. **Start LM Studio**
   - Open LM Studio
   - Load a model
   - Go to 'Local Server' tab and click 'Start Server'
   - Verify it's running at `http://127.0.0.1:1234/v1`

### Run the Demo

**Option A: Python Script**
```bash
python Agentic_Excel_Review_Demo.py
```

**Option B: Jupyter Notebook**
```bash
jupyter notebook Agentic_Excel_Review_Demo.ipynb
```

**Option C: Streamlit UI**
```bash
# Windows
run_ui.bat

# Mac/Linux
bash run_ui.sh
```

**Option D: Command Line**
```bash
python src/run_excel_review_demo.py --n 10
```

This will:
- Test LM Studio connection
- Load sample rows from your Excel file
- Retrieve relevant context from SOP documents
- Call the local LLM for analysis
- Generate AI suggestions with confidence scores
- Export results to `./out/excel_review_demo.csv`
- Log all inferences to `./logs/`

---

## ⚙️ Configuration

Edit `config.json`:

```json
{
  "input_file": "data/Sample_Review_Workbook.xlsx",
  "sheet_name": "ReviewSheet",
  "out_dir": "out",
  "preview_rows": 200,
  "lm_studio_url": "http://127.0.0.1:1234/v1"
}
```

You can also use environment variables:
- `EXCEL_REVIEW_INPUT_FILE`
- `EXCEL_REVIEW_SHEET_NAME`
- `EXCEL_REVIEW_OUT_DIR`
- `EXCEL_REVIEW_PREVIEW_ROWS`

---

## 📊 Example Output

After running the demo, you'll get:

- **CSV with AI suggestions**: `out/excel_review_demo.csv`
  - Original columns + `AI_SuggestedAction`, `AI_Confidence`, `AI_Rationale`
- **JSONL audit logs**: `logs/excel_review_assistant.jsonl`
  - Full trace of every LLM call with input/output/timestamps
- **Visualizations**: Charts of suggestion distribution and confidence

---

## 🔒 Compliance & Safety

This template is designed with validated workflows in mind:

1. **Read-Only by Default**: Excel reader never modifies source files
2. **AI_ Column Convention**: All AI outputs use the `AI_` prefix
3. **Backup Creation**: Writer module creates backups before any modification
4. **Full Audit Trail**: JSONL logs capture every inference
5. **Local Inference Only**: No data sent to cloud APIs
6. **Assistive Mode**: Human review required for all AI suggestions

### Compliance Header

All modules include a compliance notice:

```python
# ⚠️ Compliance Notice:
# This is a template for assistive AI on top of a validated Excel process.
# It must NOT overwrite original validated cells/ranges.
# All AI outputs must be written to new columns prefixed with "AI_".
```

---

## 🧪 Testing

Run the test suite:

```bash
# All tests
python -m pytest tests/

# Specific module
python -m pytest tests/test_review_assistant.py -v
```

---

## 📚 Documentation

- `docs/LM_STUDIO_SETUP.md` - Detailed LM Studio setup guide
- `docs/Project_Structure.md` - Architecture overview
- `docs/SOP_Indexer_README.md` - RAG indexing guide
- `docs/CHAT_GUIDE.md` - Using the Streamlit chat interface

---

## 🗺️ Roadmap

Modules marked with ✅ are complete:

- ✅ **M1**: Excel Reader
- ✅ **M2**: AI Review Assistant (RAG + LLM)
- ✅ **M3**: Excel Writer (Safe AI_ Columns)
- ✅ **M4**: Log Manager & QA Traceability
- ✅ **M5**: Taxonomy Manager
- ✅ **M6**: SOP Indexer (RAG)
- ✅ **M7**: Model Card Generator
- ✅ **M8**: Correction Tracker Agent
- ✅ **M9**: Publication Agent
- ✅ **M10**: LLM Integration + Demo Orchestrator
- ✅ **M11**: Streamlit UI

**Future Enhancements:**
- **M12**: QA Dashboards with Tableau integration
- **M13**: Data Lake integration for historical analysis
- **M14**: Multi-model comparison and A/B testing

---

## 🙋 Who Is This For?

This template is designed for:

- **Data Scientists** building agentic AI pipelines
- **AI Engineers** integrating local LLMs into existing workflows
- **Analytics Teams** working with Excel-based processes
- **Compliance Teams** needing audit trails and read-only AI assistance
- **Organizations** exploring AI without cloud dependencies

---

## 🛡️ License

This project is open-source and available under the MIT License. Feel free to use, modify, and distribute as needed.

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request with clear description

---

## 📧 Contact

For questions, suggestions, or collaboration opportunities, please open an issue on GitHub.

---

## 🙏 Acknowledgments

Built with:
- **LM Studio** for local LLM inference
- **ChromaDB** for vector storage
- **Streamlit** for the web interface
- **pandas**, **openpyxl** for Excel handling

---

**Note**: This is a template repository. Replace sample data with your own Excel workbooks and documents. Ensure you comply with your organization's data governance policies before deploying in production.
