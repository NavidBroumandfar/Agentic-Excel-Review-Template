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
      outputs: ["review_assistant.py", "ai/prompts/review_prompt.txt"],
      status: "active"
    },
    {
      id: "M3",
      title: "Excel Writer (Safe AI_ Columns)",
      folder: "/src/excel/",
      objective:
        "Append AI_ReasonSuggestion, AI_Confidence, etc., without touching validated ranges.",
      outputs: ["mtcr_writer.py"],
      status: "planned"
    },
    {
      id: "M4",
      title: "Log Manager",
      folder: "/src/logging/",
      objective: "Structured JSONL logging for each inference/action.",
      outputs: ["log_manager.py", "logs/monthly_metrics_summary.csv"],
      status: "planned"
    },
    {
      id: "M5",
      title: "Taxonomy Manager",
      folder: "/src/utils/",
      objective: "Dictionary + validation for Reason-for-Correction taxonomy.",
      outputs: ["taxonomy_manager.py"],
      status: "planned"
    },
    {
      id: "M6",
      title: "SOP Indexer (RAG)",
      folder: "/src/utils/",
      objective: "Embed SOPs and guides for retrieval.",
      outputs: ["sop_indexer.py", "data/embeddings/*"],
      status: "planned"
    },
    {
      id: "M7",
      title: "Model Card Generator",
      folder: "/src/compliance/",
      objective: "Record model metadata, accuracy, and governance details.",
      outputs: ["model_card_generator.py", "docs/AI_Model_Card.md"],
      status: "planned"
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
  lastUpdatedISO: "2025-10-28T13:11:23.093945Z",
  changelog: [
    { dateISO: "2025-10-28T13:11:23.094564Z", note: "Test sequential numbering for M2" }, { dateISO: "2025-10-28T13:10:33.557677Z", note: "Create module-03 for M1.2" }, { dateISO: "2025-10-28T13:10:00.452413Z", note: "Create module-02 for M1.1" }, { dateISO: "2025-10-28T13:08:49.050817Z", note: "Create module-02 for M1.1" }, { dateISO: "2025-10-28T13:01:28.688212Z", note: "Regenerate snapshot with sub-phases" }, { dateISO: "2025-10-28T13:00:21.018833Z", note: "M3 planned for Excel Writer" }, { dateISO: "2025-10-28T13:00:18.596023Z", note: "Meta Automation system completed" }, { dateISO: "2025-10-28T13:00:13.185267Z", note: "Basic Excel Reader completed" }, { dateISO: "2025-10-28T12:56:00.871124Z", note: "Kick off AI Review Assistant" }, {
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