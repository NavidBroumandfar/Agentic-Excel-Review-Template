# MTCR Agentic Automation Demo

## 📂 Two Versions Available

This demo is available in two formats:

### 1. **`MTCR_Demo.ipynb`** - Interactive Notebook
- **Best for:** Presentations, exploration, step-by-step execution
- **Run in:** Jupyter Notebook, VS Code, JupyterLab
- **Features:**
  - Interactive visualizations
  - Cell-by-cell execution
  - Markdown explanations
  - Easy to modify and experiment

### 2. **`MTCR_Demo.py`** - Python Script
- **Best for:** Automation, batch processing, CI/CD pipelines
- **Run in:** Command line, terminal, automated scripts
- **Features:**
  - Standalone execution
  - No notebook environment needed
  - Saves all outputs to files
  - Can be scheduled or automated

---

## 🚀 Quick Start

### Option A: Run the Notebook

```bash
# Open in VS Code or Jupyter
jupyter notebook MTCR_Demo.ipynb

# Or in VS Code
code MTCR_Demo.ipynb
```

**Instructions:**
1. Run Cell 1 first (installs packages)
2. Then use "Run All" from the menu
3. View diagrams and results inline

---

### Option B: Run the Python Script

```bash
# Run the complete demo
python MTCR_Demo.py
```

**What it does:**
1. ✅ Checks and installs required packages
2. ✅ Generates 3 process diagrams (PNG files)
3. ✅ Tests LM Studio connection
4. ✅ Runs AI pipeline on sample data
5. ✅ Analyzes results and creates visualizations
6. ✅ Saves all outputs to files

**Output Files:**
- `out/mtcr_ai_demo.csv` - Demo results with AI columns
- `AI_Reason_Distribution.png` - Bar chart of AI suggestions
- `Current_MTCR_Process_Simplified.png` - Process diagram
- `MTCR_Agentic_Automation_Architecture_Local_Prototype.png` - Architecture diagram
- `MTCR_Roadmap_M1-M10_Done_M11-M13_Future.png` - Roadmap diagram
- `logs/mtcr_demo_orchestrator.jsonl` - Execution logs

---

## 📋 Prerequisites

**For Both Versions:**

1. **LM Studio** running with a model loaded
   ```
   http://127.0.0.1:1234/v1
   ```

2. **MTCR Data File**
   ```
   data/MTCR Data.xlsm
   ```

3. **Python 3.8+** installed

**Python Packages** (auto-installed by both versions):
- pandas
- matplotlib
- networkx
- openpyxl
- requests

---

## 📊 What the Demo Shows

### 1. Current MTCR Process (Before AI)
- Manual review workflow
- Excel-based orchestration
- Human interpretation of comments

### 2. Agentic Automation Architecture (With AI)
- RAG-enhanced AI assistant
- Local LLM integration (LM Studio)
- Automated reasoning with confidence scores
- JSONL logging for audit trails

### 3. Roadmap
- **M1-M10:** ✅ Completed (local prototype)
  - Excel reader
  - AI review assistant
  - Safe writer
  - Log manager
  - Taxonomy manager
  - SOP indexer (RAG)
  - Model card generator
  - Correction tracker
  - Publication agent
  - Orchestrator + Demo
- **M11-M13:** 🔮 Future phases
  - MCP/Tools integration
  - QA dashboards
  - Data lake + internal LLM APIs

---

## 🎯 Use Cases

### Use the **Notebook** when:
- 📊 Presenting to stakeholders
- 🔬 Exploring and experimenting
- 📚 Learning how the system works
- 🐛 Debugging specific steps

### Use the **Python Script** when:
- ⚙️ Running automated tests
- 📅 Scheduling regular runs
- 🔄 Batch processing multiple datasets
- 🚀 Deploying to production pipelines

---

## 🛠️ Troubleshooting

### Issue: LM Studio Connection Failed
**Solution:** Ensure LM Studio is running and a model is loaded
```bash
# Check if LM Studio is listening
curl http://127.0.0.1:1234/v1/models
```

### Issue: Excel File Not Found
**Solution:** Ensure `data/MTCR Data.xlsm` exists
```bash
# Check file exists
ls "data/MTCR Data.xlsm"
```

### Issue: Import Errors
**Solution:** Manually install packages
```bash
pip install pandas matplotlib networkx openpyxl requests
```

---

## 📝 Notes

- **Compliance:** All AI outputs are written to new columns prefixed with `AI_`
- **Safe Mode:** No modifications to validated Excel files or macros
- **Audit Trail:** All inferences logged to JSONL for traceability
- **Local Only:** Runs entirely on your laptop, no cloud services

---

## 👤 Author

**Navid Broumandfar**  
Service Analytics, CHP  
bioMérieux

---

## 📄 License

Internal prototype for demonstration purposes.  
For official deployment, governance and validation required.

