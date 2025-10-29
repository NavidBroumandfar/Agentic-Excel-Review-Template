/**
 * ProjectVision.ts — Canonical roadmap & status (MTCR Agentic Automation)
 * Update after EACH module: set status, append changelog, bump timestamp.
 */
export type PhaseStatus = "planned" | "active" | "completed" | "blocked";

export interface Phase {
  id: string;
  title: string;
  folder: string;
  objective: string;
  outputs: string[];
  status: PhaseStatus;
  subPhases?: SubPhase[];
}

export interface SubPhase {
  id: string;
  title: string;
  objective: string;
  status: PhaseStatus;
}

export interface ProjectVision {
  name: string;
  owner: string;
  architect: string;
  compliance: string;
  coreTooling: string[];
  summary: string;
  phases: Phase[];
  lastUpdatedISO: string;
  changelog: { dateISO: string; note: string }[];
}

export const Project: ProjectVision = {
  name: "MTCR_Agentic_Automation",
  owner: "CHP Governance (GCS)",
  architect: "Navid",
  compliance:
    "SOP 029014; Excel/Tableau validated; AI assistive-only; write to AI_ columns; JSONL audit logs; local models only.",
  coreTooling: [
    "Python 3.11+",
    "pandas, openpyxl",
    "LM Studio (local inference)",
    "chromadb/faiss (RAG, later)"
  ],
  summary:
    "Local, assistive + agentic AI to interpret IU/Site Review comments within MTCR Data.xlsm. Start with safe Excel ingestion (M1), add RAG+LLM suggestions (M2), safe writer (M3), and logging/governance (M4+).",
  phases: [
    {
      id: "M1",
      title: "Excel Reader",
      folder: "/src/excel/",
      objective: "Read-only ingestion of 'Quality Review' sheet with profiling + CSV preview.",
      outputs: ["mtcr_reader.py", "quality_review_preview.csv", "sheet profile"],
      status: "completed",
      subPhases: [
        {
          id: "M1.1",
          title: "Basic Excel Reader",
          objective: "Create read-only Excel reader with basic sheet detection",
          status: "completed"
        },
        {
          id: "M1.2",
          title: "Meta Automation: VisionSync + Prompt Logs + Hook",
          objective: "Add automated governance with ProjectVision.ts, prompt logging, and pre-commit hooks",
          status: "completed"
        }
      ]
    },
    {
      id: "M2",
      title: "AI Review Assistant (RAG + LLM)",
      folder: "/src/ai/",
      objective:
        "Suggest standardized Reason-for-Correction with confidence + rationale, using SOP-based RAG.",
      outputs: ["review_assistant.py", "ai/prompts/review_prompt.txt", "sop_indexer.py", "test_review_assistant.py"],
      status: "completed",
      subPhases: [
        {
          id: "M2.1",
          title: "SOP Indexer (RAG)",
          objective: "Build ChromaDB index from SOP documents for context retrieval",
          status: "completed"
        },
        {
          id: "M2.2",
          title: "AI Review Assistant",
          objective: "Implement RAG + LM Studio integration for comment analysis",
          status: "completed"
        },
        {
          id: "M2.3",
          title: "Test Suite",
          objective: "Create comprehensive test suite with mock data",
          status: "completed"
        }
      ]
    },
    {
      id: "M3",
      title: "Excel Writer (Safe AI_ Columns)",
      folder: "/src/excel/",
      objective:
        "Append AI_ReasonSuggestion, AI_Confidence, etc., without touching validated ranges.",
      outputs: ["mtcr_writer.py", "test_mtcr_writer.py", "module-03.txt"],
      status: "completed"
    },
    {
      id: "M4",
      title: "Log Manager & QA Traceability",
      folder: "/src/logging/",
      objective: "Centralize JSONL ingestion (M2/M3 logs), produce monthly JSONL + Tableau-ready CSV with appender mode and confidence sparklines.",
      outputs: ["log_manager.py", "test_log_manager.py", "logs/monthly_metrics_summary.csv", "module-04.txt"],
      status: "completed"
    },
    {
      id: "M5",
      title: "Taxonomy Manager",
      folder: "/src/utils/",
      objective: "Dictionary + validation for Reason-for-Correction taxonomy.",
      outputs: ["taxonomy_manager.py"],
      status: "completed"
    },
    {
      id: "M6",
      title: "SOP Indexer (RAG + Guidance Mapping)",
      folder: "/src/utils/",
      objective: "Build local RAG index over SOP 029014 and attachments, then expose function that maps each standardized 'Reason for Correction' to best SOP clause(s) with similarity score, excerpt, and traceability.",
      outputs: ["sop_indexer.py", "data/embeddings/sop_index/", "data/mappings/reason_to_sop.yml", "logs/rag_mapping_YYYYMM.jsonl", "test_sop_indexer.py", "module-06.txt"],
      status: "completed"
    },
    {
      id: "M7",
      title: "Model Card Generator",
      folder: "/src/compliance/",
      objective: "Record model metadata, accuracy, and governance details.",
      outputs: ["model_card_generator.py", "templates/model_card.md.j2", "compliance/model_card_<YYYYMM>.md", "data/metadata/model_summary.json", "logs/modelcard_build_<YYYYMM>.jsonl", "test_model_card_generator.py", "module-07.txt"],
      status: "completed"
    },
    {
      id: "M8",
      title: "Correction Tracker Agent",
      folder: "/src/ai/",
      objective: "Summarize progress on corrections and draft reminders.",
      outputs: ["tracker_agent.py"],
      status: "planned"
    },
    {
      id: "M9",
      title: "Publisher Agent",
      folder: "/src/ai/",
      objective: "Assemble KPI email packs (FR/EN) from Dashboard & Quality Review.",
      outputs: ["publisher_agent.py"],
      status: "planned"
    }
  ],
  lastUpdatedISO: "2025-10-29T11:45:00.000000Z",
  changelog: [
    { dateISO: "2025-10-29T11:45:00.000000Z", note: "M7 Model Card Generator completed — compliance-grade documentation generator with metadata collection, Jinja2 templates, JSON schema validation, file integrity checksums, and comprehensive test suite." },
    { dateISO: "2025-10-29T01:15:00.000000Z", note: "M6 SOP Indexer (RAG + Guidance Mapping) completed — local vector index built, reason→clause mapping exposed, comprehensive test suite with mock corpus, ChromaDB/FAISS support, JSONL audit logs." },
    { dateISO: "2025-10-29T10:00:00.000000Z", note: "M5 Taxonomy Manager completed — fuzzy clustering, versioned YAML, drift CSV, JSONL changes, comprehensive test suite." },
    { dateISO: "2025-10-28T17:00:00.000000Z", note: "M4 Log Manager & QA Traceability completed - Centralized JSONL ingestion, monthly roll-up with CSV appender mode, confidence sparklines, and integrity tracking" },
    { dateISO: "2025-10-28T16:30:00.000000Z", note: "M3 Excel Writer completed - Safe AI_ sheet creation with backup, JSONL logging, win32com/openpyxl support, and comprehensive test suite" },
    { dateISO: "2025-10-28T15:45:00.000000Z", note: "M2 AI Review Assistant completed - RAG + LLM integration with ChromaDB, LM Studio, and comprehensive test suite" }, { dateISO: "2025-10-28T14:18:31.001672Z", note: "Begin development of AI Review Assistant" }, { dateISO: "2025-10-28T13:18:13.956345Z", note: "Update M2 status - development in progress" }, { dateISO: "2025-10-28T13:18:00.677210Z", note: "Regenerate M1.2 with actual content" }, { dateISO: "2025-10-28T13:17:55.754787Z", note: "Regenerate M1.1 with actual content" }, { dateISO: "2025-10-28T13:17:47.584359Z", note: "Regenerate M1 with actual content" }, { dateISO: "2025-10-28T13:11:23.094564Z", note: "Test sequential numbering for M2" }, { dateISO: "2025-10-28T13:10:33.557677Z", note: "Create module-03 for M1.2" }, { dateISO: "2025-10-28T13:10:00.452413Z", note: "Create module-02 for M1.1" }, { dateISO: "2025-10-28T13:08:49.050817Z", note: "Create module-02 for M1.1" }, { dateISO: "2025-10-28T13:01:28.688212Z", note: "Regenerate snapshot with sub-phases" }, { dateISO: "2025-10-28T13:00:21.018833Z", note: "M3 planned for Excel Writer" }, { dateISO: "2025-10-28T13:00:18.596023Z", note: "Meta Automation system completed" }, { dateISO: "2025-10-28T13:00:13.185267Z", note: "Basic Excel Reader completed" }, { dateISO: "2025-10-28T12:56:00.871124Z", note: "Kick off AI Review Assistant" }, {
      dateISO: new Date().toISOString(),
      note: "Initialized ProjectVision.ts; marked M1 as completed and defined roadmap M1→M9."
    }
  ]
};

export function snapshot(): string {
  const done =
    Project.phases.filter(p => p.status === "completed").map(p => p.id).join(", ") || "—";
  const active =
    Project.phases.filter(p => p.status === "active").map(p => p.id).join(", ") || "—";
  const next =
    Project.phases.filter(p => p.status === "planned").map(p => p.id).slice(0, 2).join(", ") || "—";
  return `Completed: ${done} | Active: ${active} | Next: ${next}`;
}