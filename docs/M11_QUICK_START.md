# M11 Quick Start Guide - MTCR Streamlit UI

## 🚀 Get Started in 3 Steps

### 1️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Start LM Studio

- Open LM Studio
- Load a model (e.g., Mistral 7B, Llama 3)
- Go to "Local Server" tab
- Click "Start Server"
- Verify it's running at `http://127.0.0.1:1234/v1`

### 3️⃣ Launch the UI

**Windows**:
```bash
run_ui.bat
```

**Mac/Linux**:
```bash
bash run_ui.sh
```

**Or directly**:
```bash
streamlit run src/ui/mtcr_app.py
```

The app will open automatically in your browser at `http://localhost:8501` 🎉

---

## 📊 What You'll See

### Tab 1: Vue d'ensemble (Overview)
- **KPI Cards**: Total rows, comments, reviewers, AI suggestions
- **AI Columns**: Detected AI-generated columns
- **Top Reasons Chart**: Most common AI suggestions
- **Dataset Preview**: First 10 rows of data

### Tab 2: Chat avec l'assistant MTCR (Chat)
- **Chat Interface**: Ask questions about the MTCR data
- **Conversation History**: Full chat log
- **Suggested Questions**: Quick-start buttons
- **Config Panel**: View current settings

---

## 💡 Try These Questions

French:
- "Quels sont les principaux types de corrections dans cet échantillon?"
- "Explique-moi le rôle de MTCR dans le process de plaintes techniques."
- "Combien de suggestions AI ont été générées?"

English:
- "What are the main correction types in this sample?"
- "Explain the role of MTCR in the technical complaints process."
- "How many AI suggestions were generated?"

---

## ⚠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| Cannot connect to LM Studio | Verify LM Studio server is running |
| Failed to load data | Check that `MTCR Data.xlsm` exists in `data/` |
| UI is slow | Clear Streamlit cache or reduce preview_rows |
| Module not found | Run `pip install -r requirements.txt` |

---

## 🧪 Verify Setup

Run the smoke test to ensure everything is configured correctly:

```bash
python tests/test_ui_smoketest.py
```

Expected output: `✅ All smoke tests passed!`

---

## 📚 Full Documentation

For detailed information, see [M11_UI_README.md](M11_UI_README.md)

---

## ⚠️ Compliance Reminder

- **Read-Only Mode**: No modifications to `MTCR Data.xlsm`
- **Assistive Only**: All AI outputs are suggestions requiring validation
- **Local Only**: No data sent to external servers

---

**Need Help?** Check the [troubleshooting section](M11_UI_README.md#troubleshooting) in the full documentation.

