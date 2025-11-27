# 🚀 Quick Start Guide

## For First-Time Users Who Clone This Repo

### **Prerequisites:**
1. Python 3.11+ installed
2. LM Studio downloaded and running (optional for full demo)

---

## ⚡ **Quick Test (Without LM Studio)**

### **1. Clone the repo:**
```bash
git clone https://github.com/NavidBroumandfar/Agentic-Excel-Review-Template.git
cd Agentic-Excel-Review-Template
```

### **2. Install dependencies:**
```bash
pip install -r requirements.txt
```

### **3. Test Excel reader:**
```bash
python -c "from src.excel.excel_reader import read_review_sheet; from src.utils.config_loader import load_config; df, profile = read_review_sheet(load_config()); print(f'✅ Loaded {profile.row_count} rows from {profile.sheet_name}')"
```

**Expected output:**
```
✅ Loaded 5 rows from ReviewSheet
```

### **4. View sample data:**
```bash
python -c "import pandas as pd; df = pd.read_excel('data/Sample_Review_Workbook.xlsx'); print(df)"
```

---

## 🤖 **Full Demo (With LM Studio)**

### **1. Start LM Studio:**
- Download from https://lmstudio.ai
- Load a model (e.g., Llama 3, Mistral)
- Go to "Local Server" tab
- Click "Start Server"
- Verify running at: `http://127.0.0.1:1234/v1`

### **2. Test LM Studio connection:**
```bash
cd src/utils
python lmstudio_smoketest.py
cd ../..
```

**Expected:** "LM Studio is running and ready!" ✅

### **3. Run demo pipeline:**
```bash
python src/run_excel_review_demo.py --n 5
```

This will:
- Load 5 sample rows
- Call LM Studio for AI suggestions
- Generate `out/excel_review_demo.csv` with AI columns
- Create JSONL logs in `logs/`

---

## 📊 **What the Demo Does**

1. **Reads** sample Excel file (5 dummy rows)
2. **Retrieves** context from SOP documents (if available)
3. **Calls** local LLM via LM Studio
4. **Generates** AI suggestions with confidence scores
5. **Writes** to CSV with AI_ columns
6. **Logs** everything to JSONL for audit

---

## 🎨 **Run the Python Demo Script**

```bash
python Agentic_Excel_Review_Demo.py
```

This generates diagrams and visualizations showing the architecture.

---

## 📝 **Sample Data Structure**

The included `data/Sample_Review_Workbook.xlsx` contains:

| RecordID | ReviewComment | Status |
|----------|---------------|--------|
| 1 | User reported delay in delivery... | Open |
| 2 | Incorrect item delivered... | Open |
| 3 | Billing discrepancy resolved... | Closed |

**All dummy data - no real information.**

---

## 🔧 **Configuration**

Edit `config.json` to customize:
```json
{
  "input_file": "data/Sample_Review_Workbook.xlsx",
  "sheet_name": "ReviewSheet",
  "out_dir": "out",
  "lm_studio_url": "http://127.0.0.1:1234/v1"
}
```

---

## 🆘 **Troubleshooting**

### **Issue:** "No module named 'src'"
**Solution:** Run from repo root, not from subdirectory

### **Issue:** "Cannot connect to LM Studio"
**Solution:** 
1. Check LM Studio is running
2. Server started on port 1234
3. Try: `curl http://127.0.0.1:1234/v1/models`

### **Issue:** "File not found: Sample_Review_Workbook.xlsx"
**Solution:** Run from repo root:
```bash
python scripts/create_sample_workbook.py
```

---

## ✅ **Success Indicators**

You should see:
```
✅ Loaded 5 rows from ReviewSheet
✅ Config loaded successfully
✅ LM Studio connection: OK
```

---

## 📚 **Next Steps**

1. Read `README.md` for full documentation
2. Check `docs/Project_Structure.md` for architecture
3. Explore `src/` modules
4. Replace sample data with your own Excel file
5. Place your SOP documents in `data/docs/`

---

**Enjoy building agentic AI workflows!** 🚀

