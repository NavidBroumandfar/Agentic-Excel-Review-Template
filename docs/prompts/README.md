# Prompt Log (MTCR Agentic Automation)

This folder stores:
- `module-XX.txt` — the exact prompt(s) used per module/phase.
- `log.jsonl` — machine-readable audit trail (timestamp + summary + module).

**Module Numbering System:**
- `module-01.txt` — M1: Excel Reader
- `module-02.txt` — M2: AI Review Assistant  
- `module-03.txt` — M3: Excel Writer (Safe AI_ Columns)
- `module-04.txt` — M4: Log Manager
- `module-05.txt` — M5: Taxonomy Manager
- `module-06.txt` — M6: SOP Indexer (RAG)
- `module-07.txt` — M7: Model Card Generator
- `module-08.txt` — M8: Correction Tracker Agent
- `module-09.txt` — M9: Publisher Agent

**Routine**
1) After each development step, paste the prompt(s) into `module-XX.txt`.
2) Append a short summary entry to `log.jsonl` (use `scripts/prompt_log.py`).
3) Update `src/context/ProjectVision.ts` (status + changelog).