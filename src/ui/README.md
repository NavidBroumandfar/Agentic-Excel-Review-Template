# UI Module - Streamlit Interface

This module provides a professional web-based interface for the Excel Review Agentic Automation system.

## Features

### 📊 Overview Tab
- **KPI Dashboard**: Real-time metrics including total rows, comments, reviewers, and AI suggestions
- **Data Preview**: Interactive table showing the first rows of your dataset
- **AI Analysis**: On-demand AI analysis of selected rows with confidence scores
- **Top Reasons Chart**: Visualization of the most common AI suggestions
- **Export Functionality**: Export analyzed data with AI columns to CSV

### 💬 Chat Tab
- **Interactive Q&A**: Ask questions about your data in natural language
- **Context-Aware**: The assistant has access to your dataset and AI analysis results
- **Suggested Questions**: Quick-start buttons for common queries
- **Chat History**: Full conversation history with clear/reset capability
- **LM Studio Integration**: Powered by local LLM models for privacy

### 📖 Presentation Tab
- **Bilingual Support**: Toggle between French and English
- **System Overview**: Visual presentation of the automation objectives
- **Architecture Details**: Complete system architecture and design principles
- **Roadmap**: Project phases and future development plans
- **Technical Stack**: Technologies and tools used

## Running the UI

### Method 1: Using Shell Scripts (Recommended)

**Windows:**
```batch
run_ui.bat
```

**Linux/Mac:**
```bash
./run_ui.sh
```

### Method 2: Direct Streamlit Command

```bash
streamlit run src/ui/excel_review_app.py
```

### Method 3: From Python

```python
import subprocess
subprocess.run(["streamlit", "run", "src/ui/excel_review_app.py"])
```

## Prerequisites

1. **Configuration**: Ensure `config.json` is properly configured with:
   - `input_file`: Path to your Excel workbook
   - `sheet_name`: Name of the sheet to analyze
   - `out_dir`: Output directory for exports

2. **LM Studio**: For chat and AI analysis features:
   - Install and start LM Studio
   - Load a compatible model
   - Default URL: `http://localhost:1234/v1/chat/completions`

3. **Dependencies**: Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The UI automatically loads configuration from `config.json`. Example:

```json
{
  "input_file": "data/Sample_Review_Workbook.xlsx",
  "sheet_name": "Review",
  "out_dir": "out",
  "lm_studio_url": "http://localhost:1234/v1/chat/completions"
}
```

## Usage Guide

### Step 1: Launch the UI
Run the UI using one of the methods above. Your browser will open automatically to `http://localhost:8501`.

### Step 2: Explore the Overview
- View KPIs and dataset statistics
- Preview your data in the interactive table
- Optionally run AI analysis on selected rows

### Step 3: AI Analysis (Optional)
1. Select the number of rows to analyze (5-50)
2. Click "🚀 Lancer l'analyse IA"
3. Wait for the analysis to complete
4. View results with confidence scores
5. Export to CSV if needed

### Step 4: Chat with the Assistant
1. Go to the "💬 Chat" tab
2. Type your question or use suggested questions
3. The assistant will respond based on your data context
4. Continue the conversation as needed

### Step 5: Learn About the System
Visit the "📖 Présentation" tab to:
- Understand the system objectives
- Learn about the architecture
- View the project roadmap
- Switch between French and English

## Features in Detail

### KPI Computation
The UI automatically computes:
- **Total Rows**: Complete dataset size
- **Rows with Comments**: Non-empty review comments
- **Distinct Reviewers**: Unique reviewer count
- **AI Suggestions**: Rows with AI analysis

### AI Analysis
When you run AI analysis:
1. Each row is processed individually
2. AI generates standardized reason suggestions
3. Confidence scores are calculated (0.0 to 1.0)
4. Results are added as `AI_*` columns
5. Original data remains unchanged (read-only mode)

### Chat Context
The chat assistant has access to:
- Dataset structure and column names
- Sample comments and data
- AI analysis results (if available)
- System architecture information
- Full project roadmap

## Customization

### Changing the Model
Edit `config.json` to point to a different LM Studio instance:
```json
{
  "lm_studio_url": "http://your-server:port/v1/chat/completions"
}
```

### Adjusting Analysis Limits
Modify line 822 in `excel_review_app.py`:
```python
max_value=min(50, len(df)),  # Change 50 to your desired max
```

### Custom Branding
Update the header in `excel_review_app.py` (lines 693-704) to customize:
- Title
- Subtitle
- Author information

## Troubleshooting

### UI Won't Start
- **Error**: `ModuleNotFoundError: No module named 'streamlit'`
- **Solution**: Run `pip install streamlit`

### Data Won't Load
- **Error**: `Failed to load review data`
- **Solution**: Verify `config.json` paths and Excel file existence

### AI Analysis Fails
- **Error**: `Unable to contact LM Studio model`
- **Solution**: 
  1. Ensure LM Studio is running
  2. Verify a model is loaded
  3. Check the LM Studio URL in config

### Chat Doesn't Respond
- **Symptom**: Empty or error responses
- **Solution**:
  1. Check LM Studio connection
  2. Verify the model supports chat completions
  3. Check console for error messages

## Architecture

The UI follows the M11 (Module 11) design:

```
src/ui/
├── __init__.py           # Package initialization
├── excel_review_app.py   # Main Streamlit application
└── README.md             # This file
```

### Key Components

1. **Data Loading** (`@st.cache_data`):
   - Cached loading of Excel data
   - Configuration management

2. **KPI Computation**:
   - Dynamic metric calculation
   - Column detection (flexible naming)

3. **LLM Integration**:
   - Context building for chat
   - Single-turn and multi-turn conversations
   - RAG integration (optional)

4. **UI Tabs**:
   - Tab 1: Overview + AI Analysis
   - Tab 2: Chat Interface
   - Tab 3: Presentation

## Design Principles

- **Read-Only Mode**: No modifications to source data
- **Assistive Mode**: All AI outputs are suggestions only
- **Local First**: Data stays on your machine
- **Traceable**: All actions can be logged
- **Bilingual**: French and English support

## Security & Compliance

- ⚠️ **Read-Only**: The UI never modifies the source Excel file
- 🔒 **Local Processing**: Data is processed locally via LM Studio
- 📝 **Audit Trail**: All AI interactions can be logged
- ✅ **Compliance**: Follows governance standards

## Support

**Created by:** Navid Broumandfar  
**Role:** Author, AI Agent & Cognitive Systems Architect  
**Department:** Service Analytics, CHP, bioMérieux

For issues or questions, refer to the main project documentation.

## License

This is a prototype system developed for demonstration purposes. For production deployment, proper governance and validation are required.
