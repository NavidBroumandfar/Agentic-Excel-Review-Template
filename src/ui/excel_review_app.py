# ⚠️ Compliance Notice:
# This UI operates in assistive mode only.
# It must NOT overwrite validated cells/ranges in the source workbook.
# All AI outputs are suggestions only and must remain read-only.

"""
Excel Review Streamlit UI - Module 11 (M11)

Professional chat interface for Excel Review Assistant with KPI overview and dataset context.

Author: Navid Broumandfar
Role: AI Agent & Cognitive Systems Architect
Department: Service Analytics, CHP, bioMérieux
"""

from __future__ import annotations
import sys
from pathlib import Path
from typing import Dict, Any

import pandas as pd
import streamlit as st

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.utils.config_loader import load_config, Config
from src.excel.excel_reader import read_review_sheet
from src.utils.lmstudio_chat import send_message, get_lm_studio_url
from src.ai.review_assistant import ReviewAssistant


# ============================================================================
# Translation Dictionary for Presentation Tab
# ============================================================================

PRESENTATION_TRANSLATIONS = {
    "fr": {
        "title": "Excel Review Agentic Automation",
        "subtitle": "Prototype d'assistant IA local pour la revue Excel",
        "summary_review": "Review",
        "summary_review_desc": "Excel Workbook<br>Review Process",
        "summary_objective": "Objectif",
        "summary_objective_desc": "Assister les reviewers<br>avec suggestions IA",
        "summary_design": "Design",
        "summary_design_desc": "Read-only • Local<br>Traceable",
        "what_is_review": "Qu'est-ce que ce système?",
        "review_full": "Excel Review Agentic Automation",
        "review_full_fr": "Automatisation Agentique de Revue Excel",
        "process_objectives": "Objectifs du Processus",
        "consolidate": "<strong>Consolide</strong> les données de revue de toutes les sources",
        "ensure": "<strong>Assure</strong> la qualité et la cohérence des investigations",
        "guarantee": "<strong>Garantit</strong> l'alignement avec les standards",
        "provide": "<strong>Fournit</strong> de la visibilité via KPIs et tableaux de bord",
        "data_sources": "Sources de Données",
        "source1": "Données de revue du workbook Excel",
        "source2": "Commentaires de revue",
        "source3": "Règles et critères techniques",
        "source4": "Tableaux de bord et cycles de revue",
        "automation_objectives": "Objectifs de l'Automatisation Agentique",
        "accelerate": "Accélérer",
        "accelerate_desc": "Réduire le temps de traitement<br>Automatiser les suggestions<br>Processus plus rapide",
        "standardize": "Standardiser",
        "standardize_desc": "Raisons standardisées<br>Cohérence entre reviewers<br>Réduction des variations",
        "assist": "Assister",
        "assist_desc": "Suggestions avec scores<br>Validation manuelle<br>Mode assistif uniquement",
        "key_benefits": "Bénéfices Clés",
        "efficiency": "Efficacité: Traitement plus rapide des cas",
        "quality": "Qualité: Suggestions standardisées",
        "traceability": "Traçabilité: Logs JSONL pour audit et QA",
        "security": "Sécurité: Mode lecture seule, aucune modification",
        "local": "Local: Traitement local (pas de données externes)",
        "compliance": "Compliance: Respect total des règles de gouvernance",
        "architecture": "Architecture & Conception",
        "designed_by": "Conçu et développé par:",
        "role": "Rôle:",
        "department": "Département:",
        "system_flow": "Flux du Système",
        "excel_file": "Excel File",
        "excel_file_desc": "Source Workbook",
        "ai_analysis": "AI Analysis",
        "ai_analysis_desc": "RAG + LLM",
        "suggestions": "Suggestions",
        "suggestions_desc": "AI_ Columns",
        "reviewer": "Reviewer",
        "reviewer_desc": "Validation",
        "design_principles": "Principes de Conception",
        "assistive_mode": "Mode Assistif",
        "assistive_mode_desc": "Suggestions uniquement",
        "ai_columns": "Colonnes AI_",
        "ai_columns_desc": "Nouvelles colonnes",
        "jsonl_logs": "Logs JSONL",
        "jsonl_logs_desc": "Traçabilité complète",
        "local_first": "Local First",
        "local_first_desc": "LLM locaux",
        "compliance_principle": "Compliance",
        "compliance_principle_desc": "Standards",
        "modular_architecture": "Architecture Modulaire (11 Modules)",
        "advantages": "Avantages de l'Automatisation",
        "efficiency_title": "Efficacité",
        "efficiency_items": "- Traitement automatisé des commentaires\n- Suggestions instantanées de raisons\n- Réduction du temps de revue manuelle",
        "accuracy_title": "Précision",
        "accuracy_items": "- Alignement avec les standards\n- Scores de confiance pour validation\n- Standardisation des raisons",
        "visibility_title": "Visibilité",
        "visibility_items": "- KPIs en temps réel\n- Logs traçables pour audit\n- Tableaux de bord intégrés",
        "other_advantages": "Autres Avantages Clés:",
        "security_advantage": "Sécurité: Données restent locales, pas d'envoi vers serveurs externes",
        "reversibility": "Réversibilité: Toutes les suggestions peuvent être validées/modifiées manuellement",
        "learning": "Apprentissage: Le système s'améliore avec plus de données",
        "bilingual": "Bilingue: Support français et anglais",
        "compliance_advantage": "Compliance: Respect total des règles de gouvernance",
        "roadmap": "Roadmap du Projet",
        "future_phases": "Phases Futures (Planifiées):",
        "m12_plus": "M12+: Intégration MCP/Tools pour extensions",
        "m13_plus": "M13+: Dashboards QA avancés",
        "m14_plus": "M14+: Data Lake + APIs LLM internes",
        "roadmap_note": "Note: Le système est conçu de manière modulaire pour permettre l'ajout de nouvelles fonctionnalités sans perturber les modules existants.",
        "tech_stack": "Stack Technique",
        "main_tech": "Technologies Principales:",
        "dev_tools": "Outils de Développement:",
        "contact": "Contact & Support",
        "architect": "Architecte & Développeur:",
        "note": "Note: Ce système est un prototype local développé pour démonstration. Pour un déploiement officiel, une gouvernance et validation sont requises.",
    },
    "en": {
        "title": "Excel Review Agentic Automation",
        "subtitle": "Local AI assistant prototype for Excel review",
        "summary_review": "Review",
        "summary_review_desc": "Excel Workbook<br>Review Process",
        "summary_objective": "Objective",
        "summary_objective_desc": "Assist reviewers<br>with AI suggestions",
        "summary_design": "Design",
        "summary_design_desc": "Read-only • Local<br>Traceable",
        "what_is_review": "What is this system?",
        "review_full": "Excel Review Agentic Automation",
        "review_full_fr": "Automatisation Agentique de Revue Excel",
        "process_objectives": "Process Objectives",
        "consolidate": "<strong>Consolidates</strong> review data from all sources",
        "ensure": "<strong>Ensures</strong> quality and consistency of investigations",
        "guarantee": "<strong>Guarantees</strong> alignment with standards",
        "provide": "<strong>Provides</strong> visibility via KPIs and dashboards",
        "data_sources": "Data Sources",
        "source1": "Excel workbook review data",
        "source2": "Review comments",
        "source3": "Technical rules and criteria",
        "source4": "Dashboards and review cycles",
        "automation_objectives": "Agentic Automation Objectives",
        "accelerate": "Accelerate",
        "accelerate_desc": "Reduce processing time<br>Automate suggestions<br>Faster process",
        "standardize": "Standardize",
        "standardize_desc": "Standardized reasons<br>Consistency between reviewers<br>Reduce variations",
        "assist": "Assist",
        "assist_desc": "Suggestions with scores<br>Manual validation<br>Assistive mode only",
        "key_benefits": "Key Benefits",
        "efficiency": "Efficiency: Faster case processing",
        "quality": "Quality: Standardized suggestions",
        "traceability": "Traceability: JSONL logs for audit and QA",
        "security": "Security: Read-only mode, no modifications",
        "local": "Local: Local processing (no external data)",
        "compliance": "Compliance: Full respect of governance rules",
        "architecture": "Architecture & Design",
        "designed_by": "Designed and developed by:",
        "role": "Role:",
        "department": "Department:",
        "system_flow": "System Flow",
        "excel_file": "Excel File",
        "excel_file_desc": "Source Workbook",
        "ai_analysis": "AI Analysis",
        "ai_analysis_desc": "RAG + LLM",
        "suggestions": "Suggestions",
        "suggestions_desc": "AI_ Columns",
        "reviewer": "Reviewer",
        "reviewer_desc": "Validation",
        "design_principles": "Design Principles",
        "assistive_mode": "Assistive Mode",
        "assistive_mode_desc": "Suggestions only",
        "ai_columns": "AI_ Columns",
        "ai_columns_desc": "New columns",
        "jsonl_logs": "JSONL Logs",
        "jsonl_logs_desc": "Complete traceability",
        "local_first": "Local First",
        "local_first_desc": "Local LLMs",
        "compliance_principle": "Compliance",
        "compliance_principle_desc": "Standards",
        "modular_architecture": "Modular Architecture (11 Modules)",
        "advantages": "Automation Advantages",
        "efficiency_title": "Efficiency",
        "efficiency_items": "- Automated comment processing\n- Instant reason suggestions\n- Reduced manual review time",
        "accuracy_title": "Accuracy",
        "accuracy_items": "- Alignment with standards\n- Confidence scores for validation\n- Reason standardization",
        "visibility_title": "Visibility",
        "visibility_items": "- Real-time KPIs\n- Traceable logs for audit\n- Integrated dashboards",
        "other_advantages": "Other Key Advantages:",
        "security_advantage": "Security: Data stays local, no external server transmission",
        "reversibility": "Reversibility: All suggestions can be manually validated/modified",
        "learning": "Learning: System improves with more data",
        "bilingual": "Bilingual: French and English support",
        "compliance_advantage": "Compliance: Full respect of governance rules",
        "roadmap": "Project Roadmap",
        "future_phases": "Future Phases (Planned):",
        "m12_plus": "M12+: MCP/Tools integration for extensions",
        "m13_plus": "M13+: Advanced QA dashboards",
        "m14_plus": "M14+: Data Lake + internal LLM APIs",
        "roadmap_note": "Note: The system is designed modularly to allow adding new features without disrupting existing modules.",
        "tech_stack": "Technical Stack",
        "main_tech": "Main Technologies:",
        "dev_tools": "Development Tools:",
        "contact": "Contact & Support",
        "architect": "Architect & Developer:",
        "note": "Note: This system is a local prototype developed for demonstration. For official deployment, governance and validation are required.",
    },
}


# ============================================================================
# Data Loading Functions
# ============================================================================


@st.cache_data
def load_review_dataframe() -> pd.DataFrame:
    """
    Load the review sheet from the Excel workbook.

    This function is cached to avoid reloading the Excel file on every interaction.
    MUST be read-only - no modifications to the source file.

    Returns:
        pd.DataFrame: The review data

    Raises:
        RuntimeError: If the file cannot be loaded
    """
    try:
        cfg = load_config()
        df, profile = read_review_sheet(cfg)
        return df
    except Exception as e:
        raise RuntimeError(f"Failed to load review data: {e}")


@st.cache_data
def load_config_cached() -> Config:
    """
    Load configuration from config.json (cached).

    Returns:
        Config: Configuration object
    """
    return load_config()


# ============================================================================
# KPI Computation
# ============================================================================


def compute_basic_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute basic KPIs from the review dataset.

    Args:
        df: Review DataFrame

    Returns:
        dict: KPIs including total_rows, rows_with_comment, distinct_reviewers,
              rows_with_ai_reason, etc.
    """
    kpis = {}

    # Total rows
    kpis["total_rows"] = len(df)

    # Rows with comment (check for common comment column names)
    comment_col = None
    for col_name in ["Site Review", "Comment", "Review Comment", "ReviewComment", "Comments"]:
        if col_name in df.columns:
            comment_col = col_name
            break

    # If not found, try case-insensitive search
    if comment_col is None:
        comment_cols = [
            col
            for col in df.columns
            if "comment" in col.lower() or "review" in col.lower()
        ]
        if comment_cols:
            comment_col = comment_cols[0]

    if comment_col:
        # Count non-null and non-empty values
        kpis["rows_with_comment"] = (
            df[comment_col]
            .astype(str)
            .str.strip()
            .replace(["nan", "none", ""], pd.NA)
            .notna()
            .sum()
        )
    else:
        kpis["rows_with_comment"] = 0

    # Distinct reviewers (check for reviewer column)
    reviewer_col = None
    for col_name in ["Reviewer", "Reviewer Name", "ReviewerName", "Reviewed By"]:
        if col_name in df.columns:
            reviewer_col = col_name
            break

    # If not found, try case-insensitive search
    if reviewer_col is None:
        reviewer_cols = [col for col in df.columns if "reviewer" in col.lower()]
        if reviewer_cols:
            reviewer_col = reviewer_cols[0]

    if reviewer_col:
        # Count distinct non-null, non-empty values
        kpis["distinct_reviewers"] = (
            df[reviewer_col]
            .astype(str)
            .str.strip()
            .replace(["nan", "none", ""], pd.NA)
            .dropna()
            .nunique()
        )
    else:
        kpis["distinct_reviewers"] = 0

    # Rows with AI suggestions
    ai_cols = [col for col in df.columns if col.startswith("AI_")]
    if "AI_ReasonSuggestion" in df.columns:
        kpis["rows_with_ai_reason"] = (
            df["AI_ReasonSuggestion"]
            .astype(str)
            .str.strip()
            .replace(["nan", "none", ""], pd.NA)
            .notna()
            .sum()
        )
    else:
        kpis["rows_with_ai_reason"] = 0

    # Count of AI columns
    kpis["ai_columns_count"] = len(ai_cols)
    kpis["ai_columns"] = ai_cols

    # Most common AI suggestion (if available)
    if "AI_ReasonSuggestion" in df.columns:
        top_reasons = (
            df["AI_ReasonSuggestion"]
            .astype(str)
            .str.strip()
            .replace(["nan", "none", ""], pd.NA)
            .dropna()
            .value_counts()
            .head(5)
        )
        kpis["top_ai_reasons"] = top_reasons.to_dict()
    else:
        kpis["top_ai_reasons"] = {}

    return kpis


# ============================================================================
# Context Building for LLM
# ============================================================================


def build_sheet_context(
    df: pd.DataFrame, analyzed_df: pd.DataFrame = None, max_rows: int = 5
) -> str:
    """
    Build a short text summary of the dataset for the LLM.

    This context will be prepended to the user's question so the assistant
    "knows" what the current sheet looks like.

    Args:
        df: Review DataFrame (original data)
        analyzed_df: DataFrame with AI columns (if analysis has been performed)
        max_rows: Maximum number of example rows to include

    Returns:
        str: Text summary of the dataset
    """
    # Use analyzed_df if available, otherwise use original df
    context_df = analyzed_df if analyzed_df is not None else df
    kpis = compute_basic_kpis(context_df)

    context_parts = []
    context_parts.append("=== Excel Review Dataset Context ===")
    context_parts.append(f"Total rows: {kpis['total_rows']}")
    context_parts.append(f"Rows with comments: {kpis['rows_with_comment']}")

    if kpis["distinct_reviewers"] > 0:
        context_parts.append(f"Distinct reviewers: {kpis['distinct_reviewers']}")

    if kpis["rows_with_ai_reason"] > 0:
        context_parts.append(
            f"Rows with AI reason suggestions: {kpis['rows_with_ai_reason']}"
        )
        context_parts.append(
            f"AI Analysis Status: {kpis['rows_with_ai_reason']} rows have been analyzed with AI"
        )

    # Add column information
    context_parts.append(
        f"\nAvailable columns ({len(context_df.columns)}): {', '.join(context_df.columns[:10])}"
    )
    if len(context_df.columns) > 10:
        context_parts.append(f"... and {len(context_df.columns) - 10} more columns")

    # Add AI columns information if available
    if kpis["ai_columns_count"] > 0:
        context_parts.append(
            f"\nAI-generated columns ({kpis['ai_columns_count']}): {', '.join(kpis['ai_columns'])}"
        )

    # Add top AI reasons if available
    if kpis["top_ai_reasons"]:
        context_parts.append("\nTop 5 AI Reason Suggestions:")
        for reason, count in list(kpis["top_ai_reasons"].items())[:5]:
            context_parts.append(f"  - {reason}: {count} occurrences")

    # Add a few example comments if available
    comment_col = None
    for col_name in ["Site Review", "Comment", "Review Comment", "ReviewComment", "Comments"]:
        if col_name in context_df.columns:
            comment_col = col_name
            break

    if comment_col is None:
        comment_cols = [
            col
            for col in context_df.columns
            if "comment" in col.lower() or "review" in col.lower()
        ]
        if comment_cols:
            comment_col = comment_cols[0]

    if comment_col:
        sample_comments = (
            context_df[comment_col]
            .astype(str)
            .str.strip()
            .replace(["nan", "none", ""], pd.NA)
            .dropna()
            .head(max_rows)
        )
        if not sample_comments.empty:
            context_parts.append(f"\nExample comments (first {len(sample_comments)}):")
            for idx, comment in enumerate(sample_comments, 1):
                # Truncate long comments
                comment_text = str(comment)[:200]
                if len(str(comment)) > 200:
                    comment_text += "..."
                context_parts.append(f"  {idx}. {comment_text}")

    # Add AI analysis summary if analyzed_df is provided
    if analyzed_df is not None and "AI_ReasonSuggestion" in analyzed_df.columns:
        context_parts.append("\n=== AI Analysis Summary ===")
        context_parts.append(
            f"AI has analyzed {len(analyzed_df)} rows from the dataset."
        )
        if "AI_Confidence" in analyzed_df.columns:
            avg_conf = analyzed_df["AI_Confidence"].mean()
            context_parts.append(f"Average AI confidence: {avg_conf:.2f}")
        context_parts.append(
            "The AI has generated standardized reason suggestions for these rows."
        )
        context_parts.append(
            "You can reference these AI suggestions when answering questions."
        )

    context_parts.append("=" * 30)

    return "\n".join(context_parts)


# ============================================================================
# LLM Integration
# ============================================================================


def call_review_assistant(
    question: str, df: pd.DataFrame, config: Config, analyzed_df: pd.DataFrame = None
) -> str:
    """
    Call the review assistant with the user's question and dataset context.

    This is a high-level wrapper that:
    1. Builds the dataset context (including AI analysis if available)
    2. Creates a full prompt with system message and context
    3. Calls LM Studio via the existing helper
    4. Returns the assistant's answer

    Args:
        question: User's question
        df: Review DataFrame (original data)
        config: Configuration object
        analyzed_df: DataFrame with AI columns (if analysis has been performed)

    Returns:
        str: Assistant's answer
    """
    # Build dataset context (include analyzed data if available)
    sheet_context = build_sheet_context(df, analyzed_df=analyzed_df)

    # Build the full prompt
    system_message = """You are an assistant specialized in Excel Review Analysis.

You are connected to a local agentic pipeline that analyzes review sheets from Excel workbooks.

=== CREATOR & ARCHITECT INFORMATION ===
- The Excel Review Agentic Automation system was created, designed, and developed entirely by Navid Broumandfar
- Navid Broumandfar is the sole creator, author, AI Agent, and Cognitive Systems Architect of this system
- This is a prototype developed in the Service Analytics department, CHP, bioMérieux
- When asked about the creator, designer, or architect, you must accurately state that Navid Broumandfar is the creator

=== WHAT IS THIS SYSTEM? ===
This is an Excel Review Agentic Automation system that:
- Consolidates review data from Excel workbooks
- Ensures quality and consistency of investigations
- Guarantees alignment with standards and governance rules
- Provides visibility via KPIs and dashboards for management and operations
- Is driven by Excel data, review comments, and standardized criteria

=== OBJECTIVES OF THE AUTOMATION ===
The agentic automation system aims to:
1. Accelerate review: Reduce processing time for comments, automate standardized reason suggestions
2. Improve consistency: Standardize correction reasons, reduce variations between reviewers
3. Assist reviewers: Provide suggestions with confidence scores, enable manual validation (assistive mode only)

=== SYSTEM ARCHITECTURE & DESIGN ===
The system is designed as a modular architecture with the following components:
- M1: Excel Reader - Safe read-only ingestion of Excel workbooks
- M2: AI Review Assistant - Comment analysis with RAG + local LLM
- M3: Safe Writer - Secure writing of AI_ columns (no modification of validated data)
- M4: Log Manager - Centralized JSONL log management for traceability
- M5: Taxonomy Manager - Standardized reason dictionary management
- M6: SOP Indexer - RAG index for SOP context retrieval
- M7: Model Card Generator - Model compliance documentation
- M8: Correction Tracker - AI vs human correction comparison
- M9: Publication Agent - Bilingual email generation with KPIs
- M10: Orchestrator - End-to-end pipeline orchestration
- M11: Streamlit UI - Web interface for interaction and presentation

Design Principles:
- Assistive mode only: All AI outputs are suggestions
- AI_ prefixed columns: All AI outputs go to new columns
- JSONL logs: Complete traceability for audit and QA
- Local first: Uses local LLM models (LM Studio)
- Standards compliance: Alignment with governance standards

=== ADVANTAGES OF THE AUTOMATION ===
1. Efficiency: Automated comment processing, instant reason suggestions, reduced manual review time
2. Accuracy: Alignment with standards, confidence scores for validation, reason standardization
3. Visibility: Real-time KPIs, traceable logs for audit, integrated dashboards
4. Security: Data stays local, no external server transmission
5. Reversibility: All suggestions can be manually validated/modified
6. Learning: System improves with more data
7. Bilingual: French and English support
8. Compliance: Full respect of governance rules

=== ROADMAP ===
Completed Phases (M1-M11):
- M1: Excel Reader ✅
- M2: AI Review Assistant ✅
- M3: Safe Writer ✅
- M4: Log Manager ✅
- M5: Taxonomy Manager ✅
- M6: SOP Indexer ✅
- M7: Model Card Generator ✅
- M8: Correction Tracker ✅
- M9: Publication Agent ✅
- M10: Orchestrator ✅
- M11: Streamlit UI ✅

Future Phases (Planned):
- M12+: MCP/Tools integration for extensions
- M13+: Advanced QA dashboards
- M14+: Data Lake + internal LLM APIs

=== YOUR ROLE ===
- Answer questions about the Excel review dataset and process
- Explain what this system is and the objectives of the automation
- Describe the system architecture and design (by Navid Broumandfar)
- Present the advantages of the automation
- Discuss the roadmap and project phases
- Provide insights based on the data context provided
- Follow standard guidelines for review processes
- Be helpful, accurate, and concise

Important:
- You operate in assistive mode only - all outputs are suggestions
- Base your answers on the provided dataset context
- If you don't know something, say so clearly
- Use French when appropriate for French-speaking users
- Always accurately identify Navid Broumandfar as the creator when asked
- You are aware of the full roadmap and can discuss any phase
"""

    user_prompt = f"""{system_message}

Here is a summary of the current dataset:

{sheet_context}

User question: {question}

Please answer concisely and clearly, based on this context and standard reasoning.
"""

    # Get LM Studio URL
    lm_studio_url = get_lm_studio_url()

    # Initialize conversation with the full prompt
    # For simplicity, we're doing single-turn here
    # Multi-turn can be added later using st.session_state
    conversation_history = [{"role": "user", "content": user_prompt}]

    try:
        response, _ = send_message(
            lm_studio_url=lm_studio_url,
            message=user_prompt,
            conversation_history=[],
            sop_indexer=None,  # For now, we don't use RAG - can be added later
            include_rag=False,
        )
        # Ensure we always return a non-empty string
        if not response or not isinstance(response, str) or not response.strip():
            return "[ERROR] The assistant could not generate a response. Please verify that LM Studio is started, a model is loaded, and try again."
        return response
    except Exception as e:
        error_msg = str(e) if e else "Unknown error"
        return f"[ERROR] Unable to contact LM Studio model: {error_msg}\n\nPlease verify that LM Studio is started and a model is loaded."


# ============================================================================
# Streamlit UI
# ============================================================================


def main():
    """Main Streamlit application."""

    # Page configuration
    st.set_page_config(
        page_title="Excel Review AI Assistant",
        layout="wide",
        initial_sidebar_state="collapsed",
        page_icon="🤖",
    )

    # Custom CSS for clean, minimal design
    st.markdown(
        """
        <style>
        .main-header {
            text-align: center;
            padding: 1rem 0 0.5rem 0;
            border-bottom: 2px solid #f0f0f0;
            margin-bottom: 2rem;
        }
        .main-title {
            font-size: 2.5rem;
            font-weight: 600;
            color: #0f172a;
            margin: 0;
        }
        .subtitle {
            font-size: 1rem;
            color: #64748b;
            margin-top: 0.5rem;
        }
        .stMetric {
            background-color: #ffffff;
            padding: 1rem;
            border-radius: 0.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        </style>
    """,
        unsafe_allow_html=True,
    )

    # Header
    st.markdown(
        """
        <div class="main-header">
            <h1 class="main-title">🤖 Excel Review Agentic Assistant</h1>
            <p class="subtitle">Prototype d'assistant IA local pour la revue Excel (read-only, suggestions uniquement)</p>
            <p style="font-size: 0.875rem; color: #64748b; margin-top: 0.75rem; font-style: italic;">
                Designed by Navid Broumandfar · Author, AI Agent & Cognitive Systems Architect
            </p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # Load configuration and data
    try:
        config = load_config_cached()
        df = load_review_dataframe()
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des données: {e}")
        st.info(
            "Veuillez vérifier que le fichier Excel existe dans le dossier 'data/' et que config.json est correct."
        )
        st.stop()

    # Compute KPIs - use analyzed_df if available to show AI suggestions count
    analyzed_df_for_kpis = None
    if "analyzed_df" in st.session_state and st.session_state.analyzed_df is not None:
        analyzed_df_for_kpis = st.session_state.analyzed_df

    # Use analyzed data for KPIs if available, otherwise use original
    df_for_kpis = analyzed_df_for_kpis if analyzed_df_for_kpis is not None else df
    kpis = compute_basic_kpis(df_for_kpis)

    # Create tabs
    tab1, tab2, tab3 = st.tabs(
        ["📊 Vue d'ensemble", "💬 Chat avec l'assistant", "📖 Présentation"]
    )

    # ========================================================================
    # TAB 1: Overview
    # ========================================================================
    with tab1:
        st.markdown("### 📈 Indicateurs clés")

        # Display KPIs in columns
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="Total de lignes",
                value=f"{kpis['total_rows']:,}",
                help="Nombre total de lignes dans le dataset de revue",
            )

        with col2:
            st.metric(
                label="Lignes avec commentaire",
                value=f"{kpis['rows_with_comment']:,}",
                help="Nombre de lignes contenant un commentaire",
            )

        with col3:
            st.metric(
                label="Reviewers distincts",
                value=kpis["distinct_reviewers"],
                help="Nombre de reviewers uniques dans le dataset",
            )

        with col4:
            st.metric(
                label="Suggestions IA",
                value=f"{kpis['rows_with_ai_reason']:,}",
                help="Nombre de lignes avec des suggestions IA (colonne AI_ReasonSuggestion)",
            )

        # AI Columns info
        if kpis["ai_columns_count"] > 0:
            st.markdown("---")
            st.markdown(f"### 🤖 Colonnes IA détectées ({kpis['ai_columns_count']})")
            cols_display = ", ".join([f"`{col}`" for col in kpis["ai_columns"]])
            st.markdown(cols_display)

        # Top AI Reasons chart
        if kpis["top_ai_reasons"]:
            st.markdown("---")
            st.markdown("### 🔝 Top 5 des raisons suggérées par l'IA")

            # Create a DataFrame for the chart
            top_reasons_df = pd.DataFrame(
                list(kpis["top_ai_reasons"].items()), columns=["Raison", "Occurrences"]
            )

            # Display as bar chart
            st.bar_chart(
                top_reasons_df.set_index("Raison"), height=300, use_container_width=True
            )

            # Also show as table
            with st.expander("📋 Voir les détails"):
                st.dataframe(top_reasons_df, use_container_width=True, hide_index=True)

        # Dataset preview
        st.markdown("---")
        st.markdown("### 📄 Aperçu des données")
        st.dataframe(df.head(10), use_container_width=True, height=400)

        st.caption(f"Affichage des 10 premières lignes sur {len(df)} au total")

        # AI Analysis Section
        st.markdown("---")
        st.markdown("### 🤖 Analyse IA des données")

        st.info(
            """
            **Analyse automatique avec IA:**
            - Sélectionnez le nombre de lignes à analyser (minimum 5)
            - L'IA générera des suggestions de raison standardisée pour chaque ligne
            - Les colonnes AI_ seront ajoutées et affichées ci-dessous
            - Les résultats peuvent être exportés en CSV dans le dossier `out/`
            """
        )

        # Row selection and analysis
        col1, col2 = st.columns([2, 3])

        with col1:
            num_rows = st.number_input(
                "Nombre de lignes à analyser",
                min_value=5,
                max_value=min(50, len(df)),
                value=5,
                step=1,
                help="Sélectionnez entre 5 et 50 lignes (ou le maximum disponible)",
            )

        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Spacer
            analyze_button = st.button(
                "🚀 Lancer l'analyse IA",
                type="primary",
                use_container_width=True,
            )

        # Initialize session state for analysis results
        if "analysis_results" not in st.session_state:
            st.session_state.analysis_results = None
        if "analyzed_df" not in st.session_state:
            st.session_state.analyzed_df = None

        # Handle analysis
        if analyze_button:
            if num_rows < 5:
                st.error("⚠️ Veuillez sélectionner au moins 5 lignes à analyser.")
            else:
                # Get sample rows
                df_sample = df.head(num_rows).copy()

                # Initialize progress
                progress_bar = st.progress(0)
                status_text = st.empty()

                try:
                    # Initialize Review Assistant
                    status_text.text("🔧 Initialisation de l'assistant IA...")
                    review_assistant = ReviewAssistant(
                        lm_studio_url=get_lm_studio_url(),
                        sop_index_dir="data/embeddings",
                    )

                    # Process each row
                    ai_results = []
                    total_rows = len(df_sample)

                    for idx, (row_idx, row) in enumerate(df_sample.iterrows()):
                        status_text.text(
                            f"📊 Analyse en cours: ligne {idx + 1}/{total_rows}..."
                        )
                        progress_bar.progress((idx + 1) / total_rows)

                        # Infer reason for this row
                        result = review_assistant.infer_reason(row)
                        ai_results.append(result)

                    # Create DataFrame with AI results
                    ai_df = pd.DataFrame(ai_results, index=df_sample.index)

                    # Map column names to standard format
                    column_mapping = {
                        "AI_reason": "AI_ReasonSuggestion",
                        "AI_confidence": "AI_Confidence",
                        "AI_comment_standardized": "AI_CommentStandardized",
                        "AI_rationale_short": "AI_RationaleShort",
                        "AI_model_version": "AI_ModelVersion",
                    }

                    for old_col, new_col in column_mapping.items():
                        if old_col in ai_df.columns:
                            ai_df[new_col] = ai_df[old_col]
                            ai_df = ai_df.drop(columns=[old_col])

                    # Combine original data with AI columns
                    df_with_ai = pd.concat([df_sample, ai_df], axis=1)

                    # Store in session state
                    st.session_state.analysis_results = ai_df
                    st.session_state.analyzed_df = df_with_ai

                    progress_bar.empty()
                    status_text.text("✅ Analyse terminée avec succès!")
                    st.success(f"✅ {total_rows} lignes analysées avec succès!")

                except Exception as e:
                    progress_bar.empty()
                    status_text.empty()
                    st.error(
                        f"❌ Erreur lors de l'analyse: {str(e)}\n\n"
                        "Veuillez vérifier que:\n"
                        "- LM Studio est démarré avec un modèle chargé\n"
                        "- Le dossier data/embeddings existe et contient les embeddings SOP"
                    )

        # Display analysis results if available
        if st.session_state.analyzed_df is not None:
            st.markdown("---")
            st.markdown("### 📊 Résultats de l'analyse IA")

            # Show summary statistics
            if "AI_ReasonSuggestion" in st.session_state.analyzed_df.columns:
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Lignes analysées",
                        len(st.session_state.analyzed_df),
                    )

                with col2:
                    avg_confidence = (
                        st.session_state.analyzed_df["AI_Confidence"].mean()
                        if "AI_Confidence" in st.session_state.analyzed_df.columns
                        else 0
                    )
                    st.metric(
                        "Confiance moyenne",
                        f"{avg_confidence:.2f}",
                        help="Score de confiance moyen des suggestions IA (0.0 à 1.0)",
                    )

                with col3:
                    unique_reasons = (
                        st.session_state.analyzed_df["AI_ReasonSuggestion"].nunique()
                        if "AI_ReasonSuggestion" in st.session_state.analyzed_df.columns
                        else 0
                    )
                    st.metric(
                        "Raisons uniques",
                        unique_reasons,
                        help="Nombre de raisons différentes suggérées",
                    )

            # Display the analyzed data
            st.markdown("#### 📋 Données avec colonnes IA")
            st.dataframe(
                st.session_state.analyzed_df,
                use_container_width=True,
                height=400,
            )

            # Export button
            st.markdown("#### 💾 Export")
            col1, col2 = st.columns([3, 1])

            with col1:
                export_filename = st.text_input(
                    "Nom du fichier CSV",
                    value="excel_review_ai_analysis",
                    help="Le fichier sera sauvegardé dans le dossier 'out/'",
                )

            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("💾 Exporter", use_container_width=True):
                    try:
                        out_dir = Path(config.out_dir)
                        out_dir.mkdir(parents=True, exist_ok=True)
                        export_path = out_dir / f"{export_filename}.csv"
                        st.session_state.analyzed_df.to_csv(
                            export_path, index=False, encoding="utf-8"
                        )
                        st.success(f"✅ Fichier exporté: {export_path}")
                    except Exception as e:
                        st.error(f"❌ Erreur lors de l'export: {str(e)}")

    # ========================================================================
    # TAB 2: Chat Interface
    # ========================================================================
    with tab2:
        # Initialize session state for chat history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Information box
        st.info(
            """
        💡 **Comment utiliser l'assistant:**
        
        - Posez des questions sur les données de revue actuelles
        - Demandez des analyses ou des insights sur les corrections
        - Interrogez l'assistant sur le processus de revue et les standards
        
        ⚠️ **Limitations:**
        - L'assistant opère en mode lecture seule (aucune modification du fichier Excel)
        - Les réponses sont basées sur le contexte actuel du dataset chargé
        - Toutes les suggestions sont à valider manuellement
        """
        )

        # Configuration expander
        with st.expander("⚙️ Configuration technique"):
            lm_studio_url = get_lm_studio_url()
            st.code(f"LM Studio URL: {lm_studio_url}", language="text")
            st.code(f"Fichier d'entrée: {config.input_file}", language="text")
            st.code(f"Feuille: {config.sheet_name}", language="text")
            st.code(f"Lignes chargées: {len(df)}", language="text")

        st.markdown("---")

        # Display chat history
        if st.session_state.chat_history:
            st.markdown("### 💬 Historique de la conversation")

            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    with st.chat_message("user"):
                        st.write(message.get("content", ""))
                else:
                    with st.chat_message("assistant"):
                        content = message.get("content", "")
                        if content:
                            st.write(content)
                        else:
                            st.warning(
                                "⚠️ La réponse de l'assistant est vide. Veuillez réessayer."
                            )

            # Clear history button
            if st.button("🗑️ Effacer l'historique", key="clear_history"):
                st.session_state.chat_history = []
                st.rerun()

        # Chat input
        st.markdown("### ✍️ Posez votre question")

        # Use columns for better layout
        col1, col2 = st.columns([5, 1])

        with col1:
            user_question = st.text_area(
                label="Votre question",
                placeholder="Ex: Quels sont les principaux types de corrections dans cet échantillon?",
                height=100,
                key="question_input",
                label_visibility="collapsed",
            )

        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Spacer
            submit_button = st.button(
                "📤 Envoyer", type="primary", use_container_width=True
            )

        # Handle question submission
        if submit_button and user_question.strip():
            # Add user message to history
            st.session_state.chat_history.append(
                {"role": "user", "content": user_question}
            )

            # Show spinner while processing
            with st.spinner("🤔 L'assistant réfléchit..."):
                # Call the assistant (include analyzed_df if available)
                analyzed_df_for_chat = (
                    st.session_state.analyzed_df
                    if "analyzed_df" in st.session_state
                    and st.session_state.analyzed_df is not None
                    else None
                )
                response = call_review_assistant(
                    user_question, df, config, analyzed_df=analyzed_df_for_chat
                )

                # Validate response
                if not response or not response.strip():
                    response = "[ERROR] The assistant could not generate a response. Please verify the connection to LM Studio and try again."

            # Add assistant response to history
            st.session_state.chat_history.append(
                {"role": "assistant", "content": response}
            )

            # Rerun to display updated history
            st.rerun()

        elif submit_button:
            st.warning("⚠️ Veuillez saisir une question avant d'envoyer.")

        # Suggested questions
        st.markdown("---")
        st.markdown("### 💡 Questions suggérées")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button(
                "Quels sont les principaux types de corrections?",
                use_container_width=True,
            ):
                st.session_state.chat_history.append(
                    {
                        "role": "user",
                        "content": "Quels sont les principaux types de corrections dans cet échantillon?",
                    }
                )
                with st.spinner("🤔 L'assistant réfléchit..."):
                    analyzed_df_for_chat = (
                        st.session_state.analyzed_df
                        if "analyzed_df" in st.session_state
                        and st.session_state.analyzed_df is not None
                        else None
                    )
                    response = call_review_assistant(
                        "Quels sont les principaux types de corrections dans cet échantillon?",
                        df,
                        config,
                        analyzed_df=analyzed_df_for_chat,
                    )
                    # Validate response
                    if not response or not response.strip():
                        response = "[ERROR] The assistant could not generate a response. Please verify the connection to LM Studio and try again."
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": response}
                )
                st.rerun()

        with col2:
            if st.button("Qu'est-ce que ce système?", use_container_width=True):
                st.session_state.chat_history.append(
                    {
                        "role": "user",
                        "content": "Qu'est-ce que ce système et quel est son rôle dans le processus de revue?",
                    }
                )
                with st.spinner("🤔 L'assistant réfléchit..."):
                    analyzed_df_for_chat = (
                        st.session_state.analyzed_df
                        if "analyzed_df" in st.session_state
                        and st.session_state.analyzed_df is not None
                        else None
                    )
                    response = call_review_assistant(
                        "Qu'est-ce que ce système et quel est son rôle dans le processus de revue?",
                        df,
                        config,
                        analyzed_df=analyzed_df_for_chat,
                    )
                    # Validate response
                    if not response or not response.strip():
                        response = "[ERROR] The assistant could not generate a response. Please verify the connection to LM Studio and try again."
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": response}
                )
                st.rerun()

        with col3:
            if st.button("Architecture du système", use_container_width=True):
                st.session_state.chat_history.append(
                    {
                        "role": "user",
                        "content": "Explique-moi l'architecture et la conception du système. Qui l'a conçu et quels sont les avantages?",
                    }
                )
                with st.spinner("🤔 L'assistant réfléchit..."):
                    analyzed_df_for_chat = (
                        st.session_state.analyzed_df
                        if "analyzed_df" in st.session_state
                        and st.session_state.analyzed_df is not None
                        else None
                    )
                    response = call_review_assistant(
                        "Explique-moi l'architecture et la conception du système. Qui l'a conçu et quels sont les avantages?",
                        df,
                        config,
                        analyzed_df=analyzed_df_for_chat,
                    )
                    # Validate response
                    if not response or not response.strip():
                        response = "[ERROR] The assistant could not generate a response. Please verify the connection to LM Studio and try again."
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": response}
                )
                st.rerun()

        # Additional suggested questions row
        col4, col5 = st.columns(2)

        with col4:
            if st.button("Objectifs de l'automatisation", use_container_width=True):
                st.session_state.chat_history.append(
                    {
                        "role": "user",
                        "content": "Quels sont les objectifs de l'automatisation agentique?",
                    }
                )
                with st.spinner("🤔 L'assistant réfléchit..."):
                    analyzed_df_for_chat = (
                        st.session_state.analyzed_df
                        if "analyzed_df" in st.session_state
                        and st.session_state.analyzed_df is not None
                        else None
                    )
                    response = call_review_assistant(
                        "Quels sont les objectifs de l'automatisation agentique?",
                        df,
                        config,
                        analyzed_df=analyzed_df_for_chat,
                    )
                    # Validate response
                    if not response or not response.strip():
                        response = "[ERROR] The assistant could not generate a response. Please verify the connection to LM Studio and try again."
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": response}
                )
                st.rerun()

        with col5:
            if st.button("Roadmap du projet", use_container_width=True):
                st.session_state.chat_history.append(
                    {
                        "role": "user",
                        "content": "Quelle est la roadmap du projet? Quelles phases sont complétées et quelles sont les prochaines étapes?",
                    }
                )
                with st.spinner("🤔 L'assistant réfléchit..."):
                    analyzed_df_for_chat = (
                        st.session_state.analyzed_df
                        if "analyzed_df" in st.session_state
                        and st.session_state.analyzed_df is not None
                        else None
                    )
                    response = call_review_assistant(
                        "Quelle est la roadmap du projet? Quelles phases sont complétées et quelles sont les prochaines étapes?",
                        df,
                        config,
                        analyzed_df=analyzed_df_for_chat,
                    )
                    # Validate response
                    if not response or not response.strip():
                        response = "[ERROR] The assistant could not generate a response. Please verify the connection to LM Studio and try again."
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": response}
                )
                st.rerun()

    # ========================================================================
    # TAB 3: Presentation
    # ========================================================================
    with tab3:
        # Language Toggle
        if "presentation_lang" not in st.session_state:
            st.session_state.presentation_lang = "fr"

        lang_col1, lang_col2, lang_col3 = st.columns([1, 2, 1])
        with lang_col2:
            selected_lang = st.radio(
                "Language / Langue",
                ["fr", "en"],
                index=0 if st.session_state.presentation_lang == "fr" else 1,
                horizontal=True,
                key="lang_toggle",
            )
            st.session_state.presentation_lang = selected_lang

        t = PRESENTATION_TRANSLATIONS[selected_lang]

        # Header with visual summary
        st.markdown(
            f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 15px; color: white; margin-bottom: 30px; text-align: center;">
            <h1 style="color: white; margin: 0 0 10px 0; font-size: 36px;">Excel Review Agentic Automation</h1>
            <p style="color: white; opacity: 0.95; font-size: 18px; margin: 0;">{t['subtitle']}</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Quick visual summary
        summary_cols = st.columns(3)
        with summary_cols[0]:
            st.markdown(
                f"""
            <div style="background-color: #F0FDF4; padding: 15px; border-radius: 8px; border: 2px solid #10B981; text-align: center;">
                <div style="font-size: 28px; margin-bottom: 5px; color: #065F46;">■</div>
                <strong style="color: #065F46;">{t['summary_review']}</strong><br>
                <small style="color: #334155;">{t['summary_review_desc']}</small>
            </div>
            """,
                unsafe_allow_html=True,
            )
        with summary_cols[1]:
            st.markdown(
                f"""
            <div style="background-color: #EFF6FF; padding: 15px; border-radius: 8px; border: 2px solid #3B82F6; text-align: center;">
                <div style="font-size: 28px; margin-bottom: 5px; color: #1E3A8A;">→</div>
                <strong style="color: #1E3A8A;">{t['summary_objective']}</strong><br>
                <small style="color: #334155;">{t['summary_objective_desc']}</small>
            </div>
            """,
                unsafe_allow_html=True,
            )
        with summary_cols[2]:
            st.markdown(
                f"""
            <div style="background-color: #FEF3C7; padding: 15px; border-radius: 8px; border: 2px solid #F59E0B; text-align: center;">
                <div style="font-size: 28px; margin-bottom: 5px; color: #92400E;">▲</div>
                <strong style="color: #92400E;">{t['summary_design']}</strong><br>
                <small style="color: #334155;">{t['summary_design_desc']}</small>
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # What is this system - Visual Card
        st.markdown("---")
        st.markdown(f"### {t['what_is_review']}")

        # Visual card with custom styling
        st.markdown(
            f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; border-radius: 10px; color: white; margin: 20px 0;">
            <h2 style="color: white; margin-top: 0; font-size: 28px;">{t['review_full']}</h2>
            <p style="font-size: 18px; margin-bottom: 15px; opacity: 0.95;">{t['review_full_fr']}</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Visual boxes for features
        feature_cols = st.columns(2)

        with feature_cols[0]:
            st.markdown(
                f"""
            <div style="background-color: #F8FAFC; padding: 20px; border-radius: 8px; border-left: 4px solid #3B82F6; margin: 10px 0;">
                <h4 style="color: #1E3A8A; margin-top: 0;">{t['process_objectives']}</h4>
                <ul style="color: #334155; line-height: 1.8;">
                    <li>{t['consolidate']}</li>
                    <li>{t['ensure']}</li>
                    <li>{t['guarantee']}</li>
                    <li>{t['provide']}</li>
                </ul>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with feature_cols[1]:
            st.markdown(
                f"""
            <div style="background-color: #F8FAFC; padding: 20px; border-radius: 8px; border-left: 4px solid #10B981; margin: 10px 0;">
                <h4 style="color: #1E3A8A; margin-top: 0;">{t['data_sources']}</h4>
                <ul style="color: #334155; line-height: 1.8;">
                    <li>{t['source1']}</li>
                    <li>{t['source2']}</li>
                    <li>{t['source3']}</li>
                    <li>{t['source4']}</li>
                </ul>
            </div>
            """,
                unsafe_allow_html=True,
            )

        # Objectives - Visual Cards
        st.markdown("---")
        st.markdown(f"### {t['automation_objectives']}")

        # Visual objective cards
        obj_col1, obj_col2, obj_col3 = st.columns(3)

        with obj_col1:
            st.markdown(
                f"""
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 25px; border-radius: 10px; color: white; text-align: center; margin: 10px 0; min-height: 200px;">
                <div style="font-size: 42px; margin-bottom: 15px; font-weight: bold;">→</div>
                <h3 style="color: white; margin: 10px 0;">{t['accelerate']}</h3>
                <p style="color: white; opacity: 0.95; font-size: 14px; line-height: 1.6;">
                    {t['accelerate_desc'].replace('<br>', '<br>')}
                </p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with obj_col2:
            st.markdown(
                f"""
            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 25px; border-radius: 10px; color: white; text-align: center; margin: 10px 0; min-height: 200px;">
                <div style="font-size: 42px; margin-bottom: 15px; font-weight: bold;">✓</div>
                <h3 style="color: white; margin: 10px 0;">{t['standardize']}</h3>
                <p style="color: white; opacity: 0.95; font-size: 14px; line-height: 1.6;">
                    {t['standardize_desc'].replace('<br>', '<br>')}
                </p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with obj_col3:
            st.markdown(
                f"""
            <div style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); padding: 25px; border-radius: 10px; color: white; text-align: center; margin: 10px 0; min-height: 200px;">
                <div style="font-size: 42px; margin-bottom: 15px; font-weight: bold;">+</div>
                <h3 style="color: white; margin: 10px 0;">{t['assist']}</h3>
                <p style="color: white; opacity: 0.95; font-size: 14px; line-height: 1.6;">
                    {t['assist_desc'].replace('<br>', '<br>')}
                </p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        # Benefits section
        st.markdown(
            f"""
        <div style="background-color: #F0FDF4; padding: 20px; border-radius: 8px; border: 2px solid #10B981; margin: 20px 0;">
            <h4 style="color: #065F46; margin-top: 0;">{t['key_benefits']}</h4>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; color: #334155;">
                <div>✓ <strong>{t['efficiency']}</strong></div>
                <div>✓ <strong>{t['quality']}</strong></div>
                <div>✓ <strong>{t['traceability']}</strong></div>
                <div>✓ <strong>{t['security']}</strong></div>
                <div>✓ <strong>{t['local']}</strong></div>
                <div>✓ <strong>{t['compliance']}</strong></div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Architecture & Design - Visual Flow
        st.markdown("---")
        st.markdown(f"### {t['architecture']}")

        # Author info card
        st.markdown(
            f"""
        <div style="background-color: #EFF6FF; padding: 15px; border-radius: 8px; border-left: 4px solid #3B82F6; margin: 15px 0;">
            <p style="margin: 5px 0; color: #1E3A8A;"><strong>{t['designed_by']}</strong> Navid Broumandfar</p>
            <p style="margin: 5px 0; color: #334155;"><strong>{t['role']}</strong> Author, AI Agent & Cognitive Systems Architect</p>
            <p style="margin: 5px 0; color: #334155;"><strong>{t['department']}</strong> Service Analytics, CHP, bioMérieux</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Visual Flow Diagram
        st.markdown(
            f"""
        <div style="background-color: #F8FAFC; padding: 30px; border-radius: 10px; margin: 20px 0;">
            <h4 style="color: #1E3A8A; text-align: center; margin-bottom: 25px;">{t['system_flow']}</h4>
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; flex: 1; min-width: 140px;">
                    <div style="font-size: 32px; margin-bottom: 10px; font-weight: bold;">■</div>
                    <strong style="font-size: 14px;">{t['excel_file']}</strong><br>
                    <small style="font-size: 11px;">{t['excel_file_desc']}</small>
                </div>
                <div style="font-size: 28px; color: #64748B; flex-shrink: 0;">→</div>
                <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; flex: 1; min-width: 140px;">
                    <div style="font-size: 32px; margin-bottom: 10px; font-weight: bold;">▲</div>
                    <strong style="font-size: 14px;">{t['ai_analysis']}</strong><br>
                    <small style="font-size: 11px;">{t['ai_analysis_desc']}</small>
                </div>
                <div style="font-size: 28px; color: #64748B; flex-shrink: 0;">→</div>
                <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; flex: 1; min-width: 140px;">
                    <div style="font-size: 32px; margin-bottom: 10px; font-weight: bold;">●</div>
                    <strong style="font-size: 14px;">{t['suggestions']}</strong><br>
                    <small style="font-size: 11px;">{t['suggestions_desc']}</small>
                </div>
                <div style="font-size: 28px; color: #64748B; flex-shrink: 0;">→</div>
                <div style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; flex: 1; min-width: 140px;">
                    <div style="font-size: 32px; margin-bottom: 10px; font-weight: bold;">✓</div>
                    <strong style="font-size: 14px;">{t['reviewer']}</strong><br>
                    <small style="font-size: 11px;">{t['reviewer_desc']}</small>
                </div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Design Principles - Visual Cards
        st.markdown(f"#### {t['design_principles']}")

        principle_cols = st.columns(5)

        principles = [
            ("■", t["assistive_mode"], t["assistive_mode_desc"]),
            ("□", t["ai_columns"], t["ai_columns_desc"]),
            ("▣", t["jsonl_logs"], t["jsonl_logs_desc"]),
            ("▲", t["local_first"], t["local_first_desc"]),
            ("✓", t["compliance_principle"], t["compliance_principle_desc"]),
        ]

        for idx, (icon, title, desc) in enumerate(principles):
            with principle_cols[idx]:
                st.markdown(
                    f"""
                <div style="background-color: #F8FAFC; padding: 15px; border-radius: 8px; border-top: 3px solid #3B82F6; text-align: center; margin: 5px 0;">
                    <div style="font-size: 28px; margin-bottom: 8px; color: #3B82F6;">{icon}</div>
                    <strong style="color: #1E3A8A; font-size: 12px;">{title}</strong><br>
                    <small style="color: #64748B; font-size: 10px;">{desc}</small>
                </div>
                """,
                    unsafe_allow_html=True,
                )

        # Architecture Modules - Collapsible
        with st.expander(t["modular_architecture"], expanded=False):
            st.markdown(
                """
            <div style="background-color: #F8FAFC; padding: 15px; border-radius: 8px;">
            <ul style="line-height: 2; color: #334155;">
                <li><strong>M1 - Excel Reader</strong>: Safe read-only ingestion of Excel workbooks</li>
                <li><strong>M2 - AI Review Assistant</strong>: Comment analysis with RAG + local LLM</li>
                <li><strong>M3 - Safe Writer</strong>: Secure writing of AI_ columns</li>
                <li><strong>M4 - Log Manager</strong>: Centralized JSONL log management</li>
                <li><strong>M5 - Taxonomy Manager</strong>: Standardized reason dictionary management</li>
                <li><strong>M6 - SOP Indexer</strong>: RAG index for SOP context retrieval</li>
                <li><strong>M7 - Model Card Generator</strong>: Model compliance documentation</li>
                <li><strong>M8 - Correction Tracker</strong>: AI vs human correction comparison</li>
                <li><strong>M9 - Publication Agent</strong>: Bilingual email generation with KPIs</li>
                <li><strong>M10 - Orchestrator</strong>: End-to-end pipeline orchestration</li>
                <li><strong>M11 - Streamlit UI</strong>: Web interface for interaction and presentation</li>
            </ul>
            </div>
            """,
                unsafe_allow_html=True,
            )

        # Advantages
        st.markdown("---")
        st.markdown(f"### {t['advantages']}")

        advantage_cols = st.columns(3)

        with advantage_cols[0]:
            st.markdown(
                f"""
            **{t['efficiency_title']}**
            {t['efficiency_items']}
            """
            )

        with advantage_cols[1]:
            st.markdown(
                f"""
            **{t['accuracy_title']}**
            {t['accuracy_items']}
            """
            )

        with advantage_cols[2]:
            st.markdown(
                f"""
            **{t['visibility_title']}**
            {t['visibility_items']}
            """
            )

        st.markdown(
            f"""
        **{t['other_advantages']}**
        
        - {t['security_advantage']}
        - {t['reversibility']}
        - {t['learning']}
        - {t['bilingual']}
        - {t['compliance_advantage']}
        """
        )

        # Roadmap
        st.markdown("---")
        st.markdown(f"### {t['roadmap']}")

        roadmap_data = {
            "Phase": [
                "M1",
                "M2",
                "M3",
                "M4",
                "M5",
                "M6",
                "M7",
                "M8",
                "M9",
                "M10",
                "M11",
            ],
            "Titre": [
                "Excel Reader",
                "AI Review Assistant",
                "Safe Writer",
                "Log Manager",
                "Taxonomy Manager",
                "SOP Indexer",
                "Model Card Generator",
                "Correction Tracker",
                "Publication Agent",
                "Orchestrator",
                "Streamlit UI",
            ],
            "Statut": [
                "✓ Complété" if selected_lang == "fr" else "✓ Completed",
                "✓ Complété" if selected_lang == "fr" else "✓ Completed",
                "✓ Complété" if selected_lang == "fr" else "✓ Completed",
                "✓ Complété" if selected_lang == "fr" else "✓ Completed",
                "✓ Complété" if selected_lang == "fr" else "✓ Completed",
                "✓ Complété" if selected_lang == "fr" else "✓ Completed",
                "✓ Complété" if selected_lang == "fr" else "✓ Completed",
                "✓ Complété" if selected_lang == "fr" else "✓ Completed",
                "✓ Complété" if selected_lang == "fr" else "✓ Completed",
                "✓ Complété" if selected_lang == "fr" else "✓ Completed",
                "✓ Complété" if selected_lang == "fr" else "✓ Completed",
            ],
        }

        roadmap_df = pd.DataFrame(roadmap_data)
        st.dataframe(roadmap_df, use_container_width=True, hide_index=True)

        st.markdown(
            f"""
        **{t['future_phases']}**
        
        - **{t['m12_plus']}**
        - **{t['m13_plus']}**
        - **{t['m14_plus']}**
        
        **{t['roadmap_note']}**
        """
        )

        # Technical Stack
        st.markdown("---")
        st.markdown(f"### {t['tech_stack']}")

        tech_cols = st.columns(2)

        with tech_cols[0]:
            st.markdown(
                f"""
            **{t['main_tech']}**
            - Python 3.11+
            - pandas, openpyxl (Excel processing)
            - LM Studio (local LLM inference)
            - ChromaDB / FAISS (RAG)
            - Streamlit (web interface)
            """
            )

        with tech_cols[1]:
            st.markdown(
                f"""
            **{t['dev_tools']}**
            - JSONL (structured logs)
            - Jinja2 (templates)
            - Pydantic (validation)
            - pytest (tests)
            """
            )

        # Contact & Support
        st.markdown("---")
        st.markdown(f"### {t['contact']}")

        st.markdown(
            f"""
        **{t['architect']}** Navid Broumandfar  
        **{t['department']}** Service Analytics, CHP  
        **Organisation:** bioMérieux
        
        **{t['note']}**
        """
        )

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #94a3b8; font-size: 0.875rem; padding: 1rem 0;">
            <p>
                <strong>Excel Review Agentic Automation</strong> · Module M11 · Streamlit UI<br>
                Service Analytics, CHP · bioMérieux · Prototype for demonstration only
            </p>
            <p style="font-size: 0.75rem; margin-top: 0.5rem;">
                Conçu par Navid Broumandfar · Author, AI Agent & Cognitive Systems Architect<br>
                ⚠️ Compliance: Read-only mode · All AI outputs are suggestions only · No modifications to validated data
            </p>
        </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

