# MTCR_Agentic_Automation

A modular AI automation system for the Monthly Technical Complaints Review (MTCR) process at bioMérieux. This system operates in assistive mode only, ensuring no modification of validated Excel cells or macros.

## Module 1 — Excel Reader

### Purpose
This module establishes a safe, read-only Excel reader for the validated workbook `MTCR Data.xlsm` and outputs a structured sheet profile with CSV preview for downstream AI processing.

### Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Prepare Data**
   - Place `MTCR Data.xlsm` in the `data/` directory
   - Ensure the workbook contains a "Quality Review" sheet

3. **Run Module 1**
   ```bash
   python -m src.excel.mtcr_reader
   ```

### Expected Outputs
- Console message: `Loaded Quality Review with X rows, Y columns.`
- CSV preview: `/out/quality_review_preview.csv` (first 200 rows by default)

### Configuration
Edit `config.json` to customize:
- `input_file`: Path to the Excel workbook
- `sheet_name`: Target sheet name (default: "Quality Review")
- `out_dir`: Output directory for artifacts
- `preview_rows`: Number of rows in CSV preview

Environment variables can override config values:
- `MTCR_INPUT_FILE`
- `MTCR_SHEET_NAME`
- `MTCR_OUT_DIR`
- `MTCR_PREVIEW_ROWS`

### Acceptance Criteria
- ✅ Read-only access to Excel workbook
- ✅ Automatic header detection
- ✅ Data cleaning and profiling
- ✅ CSV preview export
- ✅ Graceful error handling
- ✅ No modification of source data

### Compliance
- All operations are read-only
- No overwriting of validated Excel cells or macros
- AI outputs written only to new columns prefixed with "AI_" or to new files in `/out/`

## Project Vision & Prompt Logging

- Living roadmap: `src/context/ProjectVision.ts`  
  - Update **after each phase**: set status, add a changelog note.
- Prompt audit trail:
  - Paste exact prompts to `docs/prompts/module-XX.txt`
  - Append a JSONL entry:
    ```
    python scripts/prompt_log.py --module M1 --title "Excel Reader created" --summary "Read-only ingestion + CSV preview" src/excel/mtcr_reader.py src/utils/config_loader.py
    ```

## VisionSync & Hook

- Sync roadmap:
```bash
python scripts/vision_sync.py --phase M2 --status active --note "Start AI Review Assistant dev"
```
- Install pre-commit guard (run once):
```bash
python scripts/hooks/install_hooks.py
```
- The guard blocks commits if `/src/**` changed but you didn't:
- update `ProjectVision.ts` **or**
- log to `docs/prompts/log.jsonl` **and** `docs/prompts/module-XX.txt`.