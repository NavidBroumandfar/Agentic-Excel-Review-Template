# ⚠️ Compliance Notice:
# This module provides a conversational interface to the local MTCR agent.
# It must not modify any validated Excel files or production systems.
# All interactions are read-only and for exploratory / assistive purposes.

"""
MTCR Chat Interface - Interactive chat UI for MTCR agent

Provides a conversational interface to the local MTCR-specialized agent
running through LM Studio for Q&A and explanations about the MTCR process.

Created by: Navid Broumandfar (Service Analytics, CHP, bioMérieux)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import requests

from src.utils.config_loader import load_config


def _build_system_prompt() -> str:
    """
    System prompt for the MTCR-specialized chat agent.

    This should keep the model focused on:
    - MTCR process (Monthly Technical Complaints Review)
    - The MTCR_Agentic_Automation pipeline (M1–M10)
    - Explanation, clarification, and analysis
    - Never claiming to be modifying production systems directly
    """
    return (
        "You are an AI assistant specialized in the Monthly Technical Complaints Review (MTCR) "
        "process at bioMérieux. You know that:\n"
        "- This MTCR Agentic Automation system was created by Navid Broumandfar (Service Analytics, CHP).\n"
        "- MTCR Data.xlsm is a validated Excel orchestrator (Dashboard + Quality Review sheets).\n"
        "- The MTCR_Agentic_Automation project adds an assistive AI layer on top of this Excel file, "
        "with modules M1–M10 (Excel reader, AI review assistant, safe writer, log manager, taxonomy, "
        "SOP/RAG indexer (RAG = Retrieval-Augmented Generation), model card generator, tracker agent, "
        "publication agent, orchestrator demo).\n"
        "- The AI works in assistive mode only: it suggests Reasons for Correction, rationales, and "
        "confidence scores; it writes AI_ columns to demo outputs; and it logs everything for QA.\n\n"
        "When the user asks questions:\n"
        "- Explain the MTCR process and the automation clearly, in short paragraphs.\n"
        "- If they ask for analysis ideas, suggest how the existing pipeline could be used.\n"
        "- If you don't know something, say so instead of inventing details.\n"
        "- Do NOT claim to directly modify live systems or databases.\n"
    )


def mtcr_chat(user_message: str) -> str:
    """
    Send a chat-style request to the local LLM (LM Studio) using the same
    endpoint configuration as the rest of the project and return the reply text.

    Args:
        user_message: The user's message/question

    Returns:
        The agent's reply text, or an error message if the request fails
    """
    # Load config to get LM Studio URL (same pattern as existing code)
    try:
        config_path = Path("config.json")
        if config_path.exists():
            config = json.loads(config_path.read_text(encoding="utf-8"))
            lm_studio_url = config.get("lm_studio_url", "http://127.0.0.1:1234/v1")
        else:
            lm_studio_url = "http://127.0.0.1:1234/v1"
    except Exception:
        lm_studio_url = "http://127.0.0.1:1234/v1"

    # Ensure URL ends with /v1 if not present (same pattern as lmstudio_smoketest.py)
    if not lm_studio_url.endswith("/v1"):
        if lm_studio_url.endswith("/"):
            lm_studio_url = lm_studio_url + "v1"
        else:
            lm_studio_url = lm_studio_url + "/v1"

    url = f"{lm_studio_url}/chat/completions"
    system_prompt = _build_system_prompt()

    # Use the same payload structure as review_assistant.py and lmstudio_smoketest.py
    payload = {
        "model": "local-model",  # LM Studio uses this for local models
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.3,
        "max_tokens": 512,
        "stream": False,
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()

        # Extract content using the same pattern as existing code
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

        return (
            content.strip()
            if isinstance(content, str)
            else json.dumps(content, indent=2)
        )

    except requests.exceptions.ConnectionError:
        return "[MTCR chat error] Could not connect to LM Studio. Please ensure LM Studio is running and the server is started."
    except requests.exceptions.Timeout:
        return "[MTCR chat error] Request timed out. The LLM may be processing a long response."
    except requests.exceptions.HTTPError as e:
        return f"[MTCR chat error] HTTP error: {e.response.status_code} - {e.response.text[:200]}"
    except Exception as exc:  # noqa: BLE001
        return f"[MTCR chat error] {exc}"
