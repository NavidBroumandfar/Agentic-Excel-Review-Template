# Agentic Excel Review Template - Project Structure

## Overview
This project implements a modular AI automation system for Excel-based review processes. The system operates in assistive mode only, ensuring no modification of validated Excel cells or macros.

## Directory Structure
```
Agentic_Excel_Review_Template/
├── src/
│   ├── excel/
│   │   └── excel_reader.py        # M1: Excel reader and sheet profiler
│   ├── ui/
│   │   └── excel_review_app.py    # M11: Streamlit UI for Excel Review
│   └── utils/
│       ├── config_loader.py        # Configuration management
│       └── lmstudio_chat.py       # LM Studio integration
├── docs/
│   └── Project_Structure.md        # This file
├── data/                           # Input data directory
│   └── Sample_Review_Workbook.xlsx # Sample workbook (read-only)
├── out/                           # Output directory for AI artifacts
├── config.json                    # Configuration file
├── requirements.txt               # Python dependencies
└── README.md                      # Project documentation
```

## Modules

### Module 1 (M1) - Excel Reader
- **Purpose**: Safe, read-only Excel reader for review workbooks
- **Key Components**:
  - `src/excel/excel_reader.py`: Main reader with header detection and data profiling
  - `src/utils/config_loader.py`: Configuration management with env overrides
- **Outputs**:
  - Structured sheet profile with metadata
  - CSV preview in `/out/review_sheet_preview.csv`
- **Compliance**: Read-only access, no modification of source workbook

### Module 11 (M11) - Streamlit UI for Excel Review
- **Purpose**: Professional web interface for Excel Review with KPI overview and chat functionality
- **Key Components**:
  - `src/ui/excel_review_app.py`: Main Streamlit application
  - Integration with existing Excel reader and LM Studio chat
- **Features**:
  - KPI dashboard (row counts, comments, AI suggestions)
  - Interactive chat interface with dataset context
  - Read-only mode with compliance guardrails
  - Clean, minimal UI
- **How to Run**:
  ```bash
  streamlit run src/ui/excel_review_app.py
  ```
- **Compliance**: Read-only access only, all AI outputs are suggestions, no writes to validated Excel file

## Future Modules (Planned)
- M2: AI Review Assistant (RAG + LLM integration)
- M3-M9: Additional processing and analysis modules

## Compliance Notes
- All modules operate in assistive mode only
- No overwriting of validated Excel cells or macros
- AI outputs written only to new columns prefixed with "AI_" or to new files in `/out/`
