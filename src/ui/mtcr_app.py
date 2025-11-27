# ⚠️ Compliance Notice:
# This UI operates in assistive mode only.
# It must NOT overwrite validated cells/ranges in `MTCR Data.xlsm`.
# All AI outputs are suggestions only and must remain read-only.

"""
MTCR Streamlit UI - Module 11 (M11)

Professional chat interface for MTCR Assistant with KPI overview and dataset context.

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
from src.excel.mtcr_reader import read_quality_review
from src.utils.lmstudio_chat import send_message, get_lm_studio_url
from src.ai.review_assistant import ReviewAssistant


# ============================================================================
# Data Loading Functions
# ============================================================================


@st.cache_data
def load_quality_review_dataframe() -> pd.DataFrame:
    """
    Load the Quality Review sheet from MTCR Data.xlsm.

    This function is cached to avoid reloading the Excel file on every interaction.
    MUST be read-only - no modifications to the source file.

    Returns:
        pd.DataFrame: The Quality Review data

    Raises:
        RuntimeError: If the file cannot be loaded
    """
    try:
        cfg = load_config()
        df, profile = read_quality_review(cfg)
        return df
    except Exception as e:
        raise RuntimeError(f"Failed to load Quality Review data: {e}")


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
    Compute basic KPIs from the Quality Review dataset.

    Args:
        df: Quality Review DataFrame

    Returns:
        dict: KPIs including total_rows, rows_with_comment, distinct_reviewers,
              rows_with_ai_reason, etc.
    """
    kpis = {}

    # Total rows
    kpis["total_rows"] = len(df)

    # Rows with comment (check for common comment column names)
    # Try multiple possible column names (same as ReviewAssistant uses)
    comment_col = None
    for col_name in ["Site Review", "Comment", "Review Comment", "ReviewComment"]:
        if col_name in df.columns:
            comment_col = col_name
            break
    
    # If not found, try case-insensitive search
    if comment_col is None:
        comment_cols = [col for col in df.columns if "comment" in col.lower() or "review" in col.lower()]
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


def build_sheet_context(df: pd.DataFrame, analyzed_df: pd.DataFrame = None, max_rows: int = 5) -> str:
    """
    Build a short text summary of the dataset for the LLM.

    This context will be prepended to the user's question so the assistant
    "knows" what the current sheet looks like.

    Args:
        df: Quality Review DataFrame (original data)
        analyzed_df: DataFrame with AI columns (if analysis has been performed)
        max_rows: Maximum number of example rows to include

    Returns:
        str: Text summary of the dataset
    """
    # Use analyzed_df if available, otherwise use original df
    context_df = analyzed_df if analyzed_df is not None else df
    kpis = compute_basic_kpis(context_df)

    context_parts = []
    context_parts.append("=== MTCR Dataset Context ===")
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
        context_parts.append(f"\nAI-generated columns ({kpis['ai_columns_count']}): {', '.join(kpis['ai_columns'])}")

    # Add top AI reasons if available
    if kpis["top_ai_reasons"]:
        context_parts.append("\nTop 5 AI Reason Suggestions:")
        for reason, count in list(kpis["top_ai_reasons"].items())[:5]:
            context_parts.append(f"  - {reason}: {count} occurrences")

    # Add a few example comments if available
    comment_col = None
    for col_name in ["Site Review", "Comment", "Review Comment", "ReviewComment"]:
        if col_name in context_df.columns:
            comment_col = col_name
            break
    
    if comment_col is None:
        comment_cols = [col for col in context_df.columns if "comment" in col.lower() or "review" in col.lower()]
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
        context_parts.append(f"AI has analyzed {len(analyzed_df)} rows from the dataset.")
        if "AI_Confidence" in analyzed_df.columns:
            avg_conf = analyzed_df["AI_Confidence"].mean()
            context_parts.append(f"Average AI confidence: {avg_conf:.2f}")
        context_parts.append("The AI has generated standardized reason suggestions for these rows.")
        context_parts.append("You can reference these AI suggestions when answering questions.")

    context_parts.append("=" * 30)

    return "\n".join(context_parts)


# ============================================================================
# LLM Integration
# ============================================================================


def call_mtcr_assistant(question: str, df: pd.DataFrame, config: Config, analyzed_df: pd.DataFrame = None) -> str:
    """
    Call the MTCR assistant with the user's question and dataset context.

    This is a high-level wrapper that:
    1. Builds the dataset context (including AI analysis if available)
    2. Creates a full prompt with system message and context
    3. Calls LM Studio via the existing helper
    4. Returns the assistant's answer

    Args:
        question: User's question
        df: Quality Review DataFrame (original data)
        config: Configuration object
        analyzed_df: DataFrame with AI columns (if analysis has been performed)

    Returns:
        str: Assistant's answer
    """
    # Build dataset context (include analyzed data if available)
    sheet_context = build_sheet_context(df, analyzed_df=analyzed_df)

    # Build the full prompt
    system_message = """You are an assistant specialized in MTCR (Monthly Technical Complaints Review) at bioMérieux.

You are connected to a local agentic pipeline that analyzes the Quality Review sheet of MTCR Data.xlsm.

=== CREATOR & ARCHITECT INFORMATION ===
- The MTCR Agentic Automation system was created, designed, and developed entirely by Navid Broumandfar
- Navid Broumandfar is the sole creator, author, AI Agent, and Cognitive Systems Architect of this system
- This is a prototype developed in the Service Analytics department, CHP, bioMérieux
- When asked about the creator, designer, or architect, you must accurately state that Navid Broumandfar is the creator

=== WHAT IS MTCR? ===
MTCR (Monthly Technical Complaints Review) is a monthly process that:
- Consolidates technical complaints across all regions and product lines
- Ensures quality and consistency of investigations
- Guarantees alignment with SOP 029014 and governance rules
- Provides visibility via KPIs and dashboards for management and operations
- Is driven by CRM/TWD complaint data, IU/Site review comments, sampling rules, and Tableau dashboards

=== OBJECTIVES OF THE AUTOMATION ===
The agentic automation system aims to:
1. Accelerate review: Reduce processing time for comments, automate standardized reason suggestions
2. Improve consistency: Standardize correction reasons per SOP 029014, reduce variations between reviewers
3. Assist reviewers: Provide suggestions with confidence scores, enable manual validation (assistive mode only)

=== SYSTEM ARCHITECTURE & DESIGN ===
The system is designed as a modular architecture with the following components:
- M1: Excel Reader - Safe read-only ingestion of MTCR Data.xlsm
- M2: AI Review Assistant - Comment analysis with RAG + local LLM
- M3: Safe Writer - Secure writing of AI_ columns (no modification of validated data)
- M4: Log Manager - Centralized JSONL log management for traceability
- M5: Taxonomy Manager - Standardized reason dictionary management
- M6: SOP Indexer - RAG index for SOP 029014 context retrieval
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
- SOP 029014 compliance: Alignment with governance standards

=== ADVANTAGES OF THE AUTOMATION ===
1. Efficiency: Automated comment processing, instant reason suggestions, reduced manual review time
2. Accuracy: Alignment with SOP 029014, confidence scores for validation, reason standardization
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
- M9: Publication Agent (Active)
- M10: Orchestrator ✅
- M11: Streamlit UI ✅

Future Phases (Planned):
- M12+: MCP/Tools integration for extensions
- M13+: Advanced QA dashboards
- M14+: Data Lake + internal LLM APIs

=== YOUR ROLE ===
- Answer questions about the MTCR dataset and process
- Explain what MTCR is and the objectives of the automation
- Describe the system architecture and design (by Navid Broumandfar)
- Present the advantages of the automation
- Discuss the roadmap and project phases
- Provide insights based on the data context provided
- Follow SOP 029014 guidelines for Technical Complaint Reviews
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

Please answer concisely and clearly, based on this context and SOP-aligned reasoning.
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
            return "[ERREUR] L'assistant n'a pas pu générer de réponse. Veuillez vérifier que LM Studio est démarré, qu'un modèle est chargé, et réessayer."
        return response
    except Exception as e:
        error_msg = str(e) if e else "Erreur inconnue"
        return f"[ERREUR] Impossible de contacter le modèle LM Studio: {error_msg}\n\nVeuillez vérifier que LM Studio est démarré et qu'un modèle est chargé."


# ============================================================================
# Streamlit UI
# ============================================================================


def main():
    """Main Streamlit application."""

    # Page configuration
    st.set_page_config(
        page_title="MTCR AI Assistant",
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
            <h1 class="main-title">🤖 MTCR Agentic Assistant</h1>
            <p class="subtitle">Prototype d'assistant IA local pour la revue MTCR (read-only, suggestions uniquement)</p>
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
        df = load_quality_review_dataframe()
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des données: {e}")
        st.info(
            "Veuillez vérifier que le fichier MTCR Data.xlsm existe dans le dossier 'data/' et que config.json est correct."
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
    tab1, tab2, tab3 = st.tabs(["📊 Vue d'ensemble", "💬 Chat avec l'assistant MTCR", "📖 Présentation"])

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
                help="Nombre total de lignes dans le dataset Quality Review",
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
                    value="mtcr_ai_analysis",
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
        
        - Posez des questions sur les données MTCR actuelles
        - Demandez des analyses ou des insights sur les corrections
        - Interrogez l'assistant sur le processus MTCR et SOP 029014
        
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
                response = call_mtcr_assistant(user_question, df, config, analyzed_df=analyzed_df_for_chat)

                # Validate response
                if not response or not response.strip():
                    response = "[ERREUR] L'assistant n'a pas pu générer de réponse. Veuillez vérifier la connexion à LM Studio et réessayer."

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
                    response = call_mtcr_assistant(
                        "Quels sont les principaux types de corrections dans cet échantillon?",
                        df,
                        config,
                        analyzed_df=analyzed_df_for_chat,
                    )
                    # Validate response
                    if not response or not response.strip():
                        response = "[ERREUR] L'assistant n'a pas pu générer de réponse. Veuillez vérifier la connexion à LM Studio et réessayer."
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": response}
                )
                st.rerun()

        with col2:
            if st.button("Qu'est-ce que MTCR?", use_container_width=True):
                st.session_state.chat_history.append(
                    {
                        "role": "user",
                        "content": "Qu'est-ce que MTCR et quel est son rôle dans le processus de plaintes techniques?",
                    }
                )
                with st.spinner("🤔 L'assistant réfléchit..."):
                    analyzed_df_for_chat = (
                        st.session_state.analyzed_df
                        if "analyzed_df" in st.session_state
                        and st.session_state.analyzed_df is not None
                        else None
                    )
                    response = call_mtcr_assistant(
                        "Qu'est-ce que MTCR et quel est son rôle dans le processus de plaintes techniques?",
                        df,
                        config,
                        analyzed_df=analyzed_df_for_chat,
                    )
                    # Validate response
                    if not response or not response.strip():
                        response = "[ERREUR] L'assistant n'a pas pu générer de réponse. Veuillez vérifier la connexion à LM Studio et réessayer."
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": response}
                )
                st.rerun()

        with col3:
            if st.button("Architecture du système", use_container_width=True):
                st.session_state.chat_history.append(
                    {
                        "role": "user",
                        "content": "Explique-moi l'architecture et la conception du système d'automatisation MTCR. Qui l'a conçu et quels sont les avantages?",
                    }
                )
                with st.spinner("🤔 L'assistant réfléchit..."):
                    analyzed_df_for_chat = (
                        st.session_state.analyzed_df
                        if "analyzed_df" in st.session_state
                        and st.session_state.analyzed_df is not None
                        else None
                    )
                    response = call_mtcr_assistant(
                        "Explique-moi l'architecture et la conception du système d'automatisation MTCR. Qui l'a conçu et quels sont les avantages?",
                        df,
                        config,
                        analyzed_df=analyzed_df_for_chat,
                    )
                    # Validate response
                    if not response or not response.strip():
                        response = "[ERREUR] L'assistant n'a pas pu générer de réponse. Veuillez vérifier la connexion à LM Studio et réessayer."
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
                        "content": "Quels sont les objectifs de l'automatisation agentique MTCR?",
                    }
                )
                with st.spinner("🤔 L'assistant réfléchit..."):
                    analyzed_df_for_chat = (
                        st.session_state.analyzed_df
                        if "analyzed_df" in st.session_state
                        and st.session_state.analyzed_df is not None
                        else None
                    )
                    response = call_mtcr_assistant(
                        "Quels sont les objectifs de l'automatisation agentique MTCR?",
                        df,
                        config,
                        analyzed_df=analyzed_df_for_chat,
                    )
                    # Validate response
                    if not response or not response.strip():
                        response = "[ERREUR] L'assistant n'a pas pu générer de réponse. Veuillez vérifier la connexion à LM Studio et réessayer."
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": response}
                )
                st.rerun()
        
        with col5:
            if st.button("Roadmap du projet", use_container_width=True):
                st.session_state.chat_history.append(
                    {
                        "role": "user",
                        "content": "Quelle est la roadmap du projet MTCR Agentic Automation? Quelles phases sont complétées et quelles sont les prochaines étapes?",
                    }
                )
                with st.spinner("🤔 L'assistant réfléchit..."):
                    analyzed_df_for_chat = (
                        st.session_state.analyzed_df
                        if "analyzed_df" in st.session_state
                        and st.session_state.analyzed_df is not None
                        else None
                    )
                    response = call_mtcr_assistant(
                        "Quelle est la roadmap du projet MTCR Agentic Automation? Quelles phases sont complétées et quelles sont les prochaines étapes?",
                        df,
                        config,
                        analyzed_df=analyzed_df_for_chat,
                    )
                    # Validate response
                    if not response or not response.strip():
                        response = "[ERREUR] L'assistant n'a pas pu générer de réponse. Veuillez vérifier la connexion à LM Studio et réessayer."
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": response}
                )
                st.rerun()
                st.session_state.chat_history.append(
                    {
                        "role": "user",
                        "content": "Explique-moi le rôle de MTCR dans le process de plaintes techniques.",
                    }
                )
                with st.spinner("🤔 L'assistant réfléchit..."):
                    analyzed_df_for_chat = (
                        st.session_state.analyzed_df
                        if "analyzed_df" in st.session_state
                        and st.session_state.analyzed_df is not None
                        else None
                    )
                    response = call_mtcr_assistant(
                        "Explique-moi le rôle de MTCR dans le process de plaintes techniques.",
                        df,
                        config,
                        analyzed_df=analyzed_df_for_chat,
                    )
                    # Validate response
                    if not response or not response.strip():
                        response = "[ERREUR] L'assistant n'a pas pu générer de réponse. Veuillez vérifier la connexion à LM Studio et réessayer."
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": response}
                )
                st.rerun()

    # ========================================================================
    # TAB 3: Presentation
    # ========================================================================
    with tab3:
        st.markdown("## 📖 MTCR Agentic Automation - Présentation")
        
        # What is MTCR
        st.markdown("---")
        st.markdown("### 📋 Qu'est-ce que MTCR?")
        st.info("""
        **MTCR = Monthly Technical Complaints Review** (Revue Mensuelle des Plaintes Techniques)
        
        MTCR est un processus mensuel qui:
        - **Consolide** les plaintes techniques de toutes les régions et lignes de produits
        - **Assure** la qualité et la cohérence des investigations
        - **Garantit** l'alignement avec la SOP 029014 et les règles de gouvernance
        - **Fournit** de la visibilité via des KPIs et tableaux de bord pour la direction et les opérations
        
        Le processus est alimenté par:
        - Les données de plaintes CRM / TWD
        - Les commentaires de revue IU / Site
        - Les règles d'échantillonnage et critères techniques
        - Les tableaux de bord Tableau et cycles de revue par email
        """)
        
        # Objectives
        st.markdown("---")
        st.markdown("### 🎯 Objectifs de l'Automatisation Agentique")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Objectifs Principaux:**
            
            1. **Accélérer la revue**
               - Réduire le temps de traitement des commentaires
               - Automatiser la suggestion de raisons standardisées
            
            2. **Améliorer la cohérence**
               - Standardiser les raisons de correction selon SOP 029014
               - Réduire les variations entre reviewers
            
            3. **Assister les reviewers**
               - Fournir des suggestions avec scores de confiance
               - Permettre la validation manuelle (mode assistif uniquement)
            """)
        
        with col2:
            st.markdown("""
            **Bénéfices Attendus:**
            
            ✅ **Efficacité**: Traitement plus rapide des cas
            ✅ **Qualité**: Suggestions alignées avec la SOP
            ✅ **Traçabilité**: Logs JSONL pour audit et QA
            ✅ **Sécurité**: Mode lecture seule, aucune modification des données validées
            ✅ **Local**: Traitement local avec modèles LLM locaux (pas de données externes)
            """)
        
        # Architecture & Design
        st.markdown("---")
        st.markdown("### 🏗️ Architecture & Conception")
        
        st.markdown("""
        **Conçu et développé par:** Navid Broumandfar  
        **Rôle:** Author, AI Agent & Cognitive Systems Architect  
        **Département:** Service Analytics, CHP, bioMérieux
        """)
        
        st.markdown("""
        **Architecture Modulaire:**
        
        Le système est conçu comme une série de modules interconnectés:
        
        1. **M1 - Excel Reader**: Lecture sécurisée (read-only) du fichier MTCR Data.xlsm
        2. **M2 - AI Review Assistant**: Analyse des commentaires avec RAG + LLM local
        3. **M3 - Safe Writer**: Écriture sécurisée des colonnes AI_ (pas de modification des données validées)
        4. **M4 - Log Manager**: Gestion centralisée des logs JSONL pour traçabilité
        5. **M5 - Taxonomy Manager**: Gestion du dictionnaire de raisons standardisées
        6. **M6 - SOP Indexer**: Index RAG pour récupération de contexte SOP 029014
        7. **M7 - Model Card Generator**: Documentation de conformité des modèles
        8. **M8 - Correction Tracker**: Comparaison AI vs corrections humaines
        9. **M9 - Publication Agent**: Génération d'emails bilingues avec KPIs
        10. **M10 - Orchestrator**: Orchestration du pipeline end-to-end
        11. **M11 - Streamlit UI**: Interface web pour interaction et présentation
        """)
        
        st.markdown("""
        **Principes de Conception:**
        
        - 🔒 **Mode Assistif Uniquement**: Toutes les sorties AI sont des suggestions
        - 📝 **Colonnes AI_ Préfixées**: Toutes les sorties AI vont dans de nouvelles colonnes
        - 📊 **Logs JSONL**: Traçabilité complète pour audit et QA
        - 🏠 **Local First**: Utilisation de modèles LLM locaux (LM Studio)
        - ✅ **Compliance SOP 029014**: Alignement avec les standards de gouvernance
        """)
        
        # Advantages
        st.markdown("---")
        st.markdown("### ✨ Avantages de l'Automatisation")
        
        advantage_cols = st.columns(3)
        
        with advantage_cols[0]:
            st.markdown("""
            **🚀 Efficacité**
            - Traitement automatisé des commentaires
            - Suggestions instantanées de raisons
            - Réduction du temps de revue manuelle
            """)
        
        with advantage_cols[1]:
            st.markdown("""
            **🎯 Précision**
            - Alignement avec SOP 029014
            - Scores de confiance pour validation
            - Standardisation des raisons
            """)
        
        with advantage_cols[2]:
            st.markdown("""
            **📈 Visibilité**
            - KPIs en temps réel
            - Logs traçables pour audit
            - Tableaux de bord intégrés
            """)
        
        st.markdown("""
        **Autres Avantages Clés:**
        
        - 🔐 **Sécurité**: Données restent locales, pas d'envoi vers serveurs externes
        - 🔄 **Réversibilité**: Toutes les suggestions peuvent être validées/modifiées manuellement
        - 📚 **Apprentissage**: Le système s'améliore avec plus de données
        - 🌐 **Bilingue**: Support français et anglais
        - 🛡️ **Compliance**: Respect total des règles de gouvernance
        """)
        
        # Roadmap
        st.markdown("---")
        st.markdown("### 🗺️ Roadmap du Projet")
        
        roadmap_data = {
            "Phase": ["M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "M10", "M11"],
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
                "Streamlit UI"
            ],
            "Statut": [
                "✅ Complété",
                "✅ Complété",
                "✅ Complété",
                "✅ Complété",
                "✅ Complété",
                "✅ Complété",
                "✅ Complété",
                "✅ Complété",
                "🔄 Actif",
                "✅ Complété",
                "✅ Complété"
            ]
        }
        
        roadmap_df = pd.DataFrame(roadmap_data)
        st.dataframe(roadmap_df, use_container_width=True, hide_index=True)
        
        st.markdown("""
        **Phases Futures (Planifiées):**
        
        - **M12+**: Intégration MCP/Tools pour extensions
        - **M13+**: Dashboards QA avancés
        - **M14+**: Data Lake + APIs LLM internes
        
        **Note:** Le système est conçu de manière modulaire pour permettre l'ajout de nouvelles fonctionnalités sans perturber les modules existants.
        """)
        
        # Technical Stack
        st.markdown("---")
        st.markdown("### 🛠️ Stack Technique")
        
        tech_cols = st.columns(2)
        
        with tech_cols[0]:
            st.markdown("""
            **Technologies Principales:**
            - Python 3.11+
            - pandas, openpyxl (traitement Excel)
            - LM Studio (inférence LLM locale)
            - ChromaDB / FAISS (RAG)
            - Streamlit (interface web)
            """)
        
        with tech_cols[1]:
            st.markdown("""
            **Outils de Développement:**
            - JSONL (logs structurés)
            - Jinja2 (templates)
            - Pydantic (validation)
            - pytest (tests)
            """)
        
        # Contact & Support
        st.markdown("---")
        st.markdown("### 📞 Contact & Support")
        
        st.markdown("""
        **Architecte & Développeur:** Navid Broumandfar  
        **Département:** Service Analytics, CHP  
        **Organisation:** bioMérieux
        
        **Note:** Ce système est un prototype local développé pour démonstration.  
        Pour un déploiement officiel, une gouvernance et validation sont requises.
        """)

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #94a3b8; font-size: 0.875rem; padding: 1rem 0;">
            <p>
                <strong>MTCR Agentic Automation</strong> · Module M11 · Streamlit UI<br>
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
