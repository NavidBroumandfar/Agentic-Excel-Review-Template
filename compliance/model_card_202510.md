# MTCR AI Model Card — 2025-10

**Project:** MTCR_Agentic_Automation  
**Version:** v0.7.0  
**Commit:** 872aaa8

---

## Model Overview
| Component | Model | Version | Provider |
|------------|--------|---------|-----------|
| AI Review Assistant | Llama-3-8B-local | local | Meta |
| Embedding Model | all-MiniLM-L6-v2 | 3.0 | SBERT |
| Taxonomy Version | 20251015 |  |  |

---

## Performance Summary
| Metric | Value |
|--------|--------|
| Accuracy (QA validated) | 0.82 |
| Confidence avg | 0.833 |

---

## File Integrity

- **src/utils/sop_indexer.py**: sha256:aac97cd3b6b7 (26867 bytes, modified: 2025-10-29)

- **src/utils/taxonomy_manager.py**: sha256:5328800b4da7 (13315 bytes, modified: 2025-10-29)

- **src/ai/review_assistant.py**: sha256:27e7c1041518 (14567 bytes, modified: 2025-10-28)

- **src/excel/mtcr_writer.py**: sha256:b244dbaf59e0 (7882 bytes, modified: 2025-10-28)

- **src/logging/log_manager.py**: sha256:bf39ac0dd224 (11775 bytes, modified: 2025-10-29)


---

## Compliance & Governance
- **Standard**: SOP 029014 Rev 15.A
- **Mode**: Assistive-only
- **Data Privacy**: No PII or customer data used for training
- **Human Validation**: Required

---

## Limitations / Ethical Notes
- Assistive mode only (no autonomous decisions)  
- Human QA validation required for each Reason for Correction  
- No PII or customer data used for training  
- Local models only (no external API calls)

---

## Change Log
- 2025-10-29 — Model Card Generator (M7) implemented
- 2025-10-29 — Integrated SOP RAG index (M6)  
- 2025-10-27 — Added Taxonomy standardization (M5)
- 2025-10-28 — Log Manager & QA Traceability (M4)
- 2025-10-28 — Excel Writer with AI_ columns (M3)
- 2025-10-28 — AI Review Assistant with RAG (M2)
- 2025-10-28 — Excel Reader foundation (M1)

---

## Technical Details
- **Generated**: 2025-10-29T10:45:52.371527+00:00
- **Git Commit**: 872aaa8
- **Files Verified**: 5
- **Compliance**: SOP 029014 Rev 15.A