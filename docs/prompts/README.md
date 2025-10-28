# Prompt Log (MTCR Agentic Automation)

This folder stores:
- `module-XX.txt` — the exact prompt(s) used per module/phase.
- `log.jsonl` — machine-readable audit trail (timestamp + summary + module).

**Routine**
1) After each development step, paste the prompt(s) into `module-XX.txt`.
2) Append a short summary entry to `log.jsonl` (use `scripts/prompt_log.py`).
3) Update `src/context/ProjectVision.ts` (status + changelog).