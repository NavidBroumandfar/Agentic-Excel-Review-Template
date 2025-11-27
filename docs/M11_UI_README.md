# Module 11 (M11) - Streamlit UI for MTCR Assistant

## Overview

Module M11 provides a professional web-based user interface for the MTCR Agentic Automation system. Built with Streamlit, it offers an intuitive chat interface and comprehensive KPI dashboard for interacting with the MTCR dataset.

**Author**: Navid Broumandfar (Service Analytics, CHP, bioMérieux)

## Features

### 1. 📊 KPI Dashboard (Vue d'ensemble)

The overview tab provides instant insights into the MTCR dataset:

- **Total Rows**: Complete count of records in the Quality Review sheet
- **Rows with Comments**: Number of entries containing review comments
- **Distinct Reviewers**: Count of unique reviewers in the dataset
- **AI Suggestions**: Number of rows with AI-generated reason suggestions

#### Advanced Visualizations

- **AI Column Detection**: Automatically identifies all AI-generated columns (prefixed with `AI_`)
- **Top 5 Reasons Chart**: Interactive bar chart showing the most common AI reason suggestions
- **Dataset Preview**: Scrollable table displaying the first 10 rows of the dataset

### 2. 💬 Interactive Chat Interface

The chat tab enables natural language interaction with the MTCR dataset:

#### Key Capabilities

- **Context-Aware Responses**: The LLM receives a summary of the current dataset, enabling accurate, data-driven answers
- **Multi-turn Conversations**: Full conversation history maintained throughout the session
- **Suggested Questions**: Quick-start buttons for common queries
- **Bilingual Support**: Handles both French and English queries naturally

#### Example Questions

```text
- "Quels sont les principaux types de corrections dans cet échantillon?"
- "Explique-moi le rôle de MTCR dans le process de plaintes techniques."
- "Combien de suggestions AI ont été générées avec une haute confidence?"
- "Montre-moi les tendances dans les commentaires de revue."
- "What is SOP 029014 and how does it relate to MTCR?"
```

### 3. ⚙️ Technical Configuration

The UI provides transparency into the system configuration:

- LM Studio endpoint URL
- Input file path and sheet name
- Current dataset statistics
- Configuration viewing in expandable panel

## Installation & Setup

### Prerequisites

1. **Python 3.9+** with all project dependencies
2. **LM Studio** with a loaded model and running server
3. **MTCR Data.xlsm** in the `data/` directory

### Installation Steps

1. **Install Dependencies**

```bash
pip install -r requirements.txt
```

This will install Streamlit and all other required packages.

2. **Verify LM Studio Configuration**

Ensure LM Studio is running at the configured endpoint (default: `http://127.0.0.1:1234/v1`).

You can test connectivity with:

```bash
python src/utils/lmstudio_smoketest.py
```

3. **Run Smoke Tests**

Verify the UI module is properly set up:

```bash
python tests/test_ui_smoketest.py
```

Expected output: `✅ All smoke tests passed!`

### Running the UI

#### Method 1: Launcher Scripts (Recommended)

**Windows**:
```bash
run_ui.bat
```
Or double-click `run_ui.bat` in File Explorer.

**Mac/Linux**:
```bash
bash run_ui.sh
```

#### Method 2: Direct Command

```bash
streamlit run src/ui/mtcr_app.py
```

#### Method 3: Python Module

```bash
python -m streamlit run src/ui/mtcr_app.py
```

The application will automatically open in your default web browser at `http://localhost:8501`.

## Architecture

### Core Components

```
src/ui/mtcr_app.py
├── Data Loading Layer
│   ├── load_quality_review_dataframe()  # Cached Excel loading
│   └── load_config_cached()             # Configuration management
│
├── Analytics Layer
│   ├── compute_basic_kpis()             # KPI computation
│   └── build_sheet_context()           # LLM context building
│
├── LLM Integration Layer
│   └── call_mtcr_assistant()            # LM Studio interaction
│
└── UI Layer (Streamlit)
    ├── KPI Dashboard (Tab 1)
    │   ├── Metric cards
    │   ├── AI columns display
    │   ├── Top reasons chart
    │   └── Dataset preview
    │
    └── Chat Interface (Tab 2)
        ├── Conversation history
        ├── Message input
        ├── Suggested questions
        └── Configuration viewer
```

### Data Flow

1. **Initialization**:
   - Load configuration from `config.json`
   - Read Excel file via `mtcr_reader.py` (cached)
   - Compute KPIs from dataset

2. **User Query**:
   - User enters question in chat interface
   - System builds dataset context summary
   - Context + question sent to LM Studio
   - Response displayed in chat history

3. **Session Management**:
   - Chat history stored in `st.session_state`
   - Persists across interactions within session
   - Can be cleared with "Effacer l'historique" button

## Configuration

### config.json Parameters

The UI uses the following configuration parameters:

```json
{
  "input_file": "data/MTCR Data.xlsm",
  "sheet_name": "Quality Review",
  "out_dir": "out",
  "preview_rows": 200,
  "lm_studio_url": "http://127.0.0.1:1234/v1"
}
```

| Parameter | Description | Default |
|-----------|-------------|---------|
| `input_file` | Path to MTCR Excel file | `data/MTCR Data.xlsm` |
| `sheet_name` | Target worksheet name | `Quality Review` |
| `out_dir` | Output directory for exports | `out` |
| `preview_rows` | Rows in CSV preview | `200` |
| `lm_studio_url` | LM Studio API endpoint | `http://127.0.0.1:1234/v1` |

### Environment Variables

Configuration can also be set via environment variables (takes precedence over config.json):

- `MTCR_INPUT_FILE`
- `MTCR_SHEET_NAME`
- `MTCR_OUT_DIR`
- `MTCR_PREVIEW_ROWS`

## Compliance & Security

### ⚠️ Compliance Notice

**This UI operates in assistive mode only.**

#### Read-Only Guarantees

1. **No Excel Modifications**: The UI never writes to `MTCR Data.xlsm`
2. **No Cell Overwrites**: Validated cells and ranges are never modified
3. **No Macro Changes**: VBA macros remain untouched
4. **No Structural Changes**: No columns, rows, or sheets are added/removed

#### Data Handling

- All data loading uses read-only mode
- Excel file is cached after first load (no repeated reads)
- Any exports (future feature) will write to `out/` directory only
- No temporary files created in `data/` directory

#### AI Output Handling

- All AI responses are suggestions only
- Require manual validation before use
- Not automatically written back to Excel
- Clearly marked as AI-generated in the UI

### Security Considerations

1. **Local-Only Operation**: No data sent to external servers
2. **LM Studio Integration**: Uses local LLM model only
3. **No Network Dependencies**: Works completely offline
4. **No Telemetry**: No usage data collected or transmitted

## Troubleshooting

### Common Issues

#### Issue: "Cannot connect to LM Studio"

**Symptoms**: Chat returns connection error message

**Solutions**:
1. Verify LM Studio is running
2. Check that a model is loaded in LM Studio
3. Confirm the server is started (Local Server tab)
4. Verify endpoint in `config.json` matches LM Studio URL
5. Test connection: `python src/utils/lmstudio_smoketest.py`

#### Issue: "Failed to load Quality Review data"

**Symptoms**: Error message on app startup

**Solutions**:
1. Verify `MTCR Data.xlsm` exists in `data/` directory
2. Check that file is not open in Excel (file lock issue)
3. Confirm `sheet_name` in `config.json` matches actual sheet name
4. Check file permissions (read access required)

#### Issue: UI is slow or unresponsive

**Symptoms**: Long loading times, lag in interactions

**Solutions**:
1. Check Excel file size (large files take longer to load)
2. Clear Streamlit cache: Click "Clear cache" in Streamlit settings menu
3. Reduce `preview_rows` in `config.json`
4. Close other resource-intensive applications
5. Restart the Streamlit server

#### Issue: Chat responses are slow

**Symptoms**: Long wait time after submitting questions

**Solutions**:
1. Check LM Studio model size (larger models are slower)
2. Verify LM Studio is using GPU acceleration if available
3. Reduce dataset context size (modify `max_rows` parameter)
4. Consider using a smaller, faster model in LM Studio

#### Issue: Streamlit import error

**Symptoms**: `ModuleNotFoundError: No module named 'streamlit'`

**Solutions**:
```bash
pip install streamlit>=1.28.0
# Or reinstall all dependencies
pip install -r requirements.txt
```

### Debug Mode

To run Streamlit in debug mode with detailed logging:

```bash
streamlit run src/ui/mtcr_app.py --logger.level=debug
```

### Log Files

Streamlit logs are stored in:
- Windows: `%APPDATA%\streamlit\logs\`
- Mac/Linux: `~/.streamlit/logs/`

## Testing

### Smoke Tests

Run the comprehensive smoke test suite:

```bash
python tests/test_ui_smoketest.py
```

The suite tests:
- Streamlit installation
- Module imports
- KPI computation logic
- Context building functionality
- Edge case handling

### Manual Testing Checklist

- [ ] UI loads without errors
- [ ] KPI dashboard displays correct counts
- [ ] AI columns are detected (if present)
- [ ] Top reasons chart displays (if AI suggestions exist)
- [ ] Dataset preview shows data correctly
- [ ] Chat input accepts text
- [ ] Submit button sends questions
- [ ] LLM responds to queries
- [ ] Chat history persists during session
- [ ] Clear history button works
- [ ] Suggested questions function correctly
- [ ] Configuration panel shows correct settings

## Future Enhancements

Potential additions for future versions:

1. **Multi-turn Context**: Maintain dataset context across conversation turns
2. **RAG Integration**: Connect to SOP indexer for document-aware responses
3. **Export Functionality**: Export chat history or analysis results
4. **Advanced Filtering**: Filter dataset before analysis
5. **Visualization Tools**: Interactive charts and plots
6. **Batch Questions**: Ask multiple questions at once
7. **Response Streaming**: Stream LLM responses token-by-token
8. **Custom Prompts**: User-defined system prompts
9. **Session Persistence**: Save and resume conversations
10. **Multi-language UI**: Full bilingual interface

## Related Documentation

- [Project Structure](Project_Structure.md) - Overall project architecture
- [LM Studio Setup](LM_STUDIO_SETUP.md) - LM Studio configuration guide
- [Chat Guide](CHAT_GUIDE.md) - Interactive chat usage guide
- [Main README](../README.md) - Project overview and quick start

## Support

For issues or questions:
1. Check this documentation
2. Review troubleshooting section
3. Run smoke tests to diagnose issues
4. Contact: Navid Broumandfar (Service Analytics, CHP, bioMérieux)

---

**Version**: 1.0.0  
**Last Updated**: November 2025  
**Status**: Production-ready prototype  
**License**: Internal use only (bioMérieux)

