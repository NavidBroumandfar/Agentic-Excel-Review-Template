# ⚠️ Compliance Notice:
# Assistive mode only. This is a simple chat interface for testing.
# Uses the same LM Studio endpoint as the Excel Review agent.

"""
Interactive Chat Interface for LM Studio with Excel Review Context
Chat with the same LLM model used by the Excel Review agent.
"""

from __future__ import annotations
import json
import sys
import os
from pathlib import Path
import requests

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.utils.config_loader import load_config
from src.utils.sop_indexer import SOPIndexer


def get_excel_review_system_prompt() -> str:
    """Get the Excel review system prompt to give the LLM context awareness."""
    return """You are an AI assistant integrated into an Agentic Excel Review system.

Your role and context:
- You are part of an agentic AI system that processes review comments from Excel workbooks
- You follow documented SOPs for review processes
- You understand review terminology, workflows, and processes
- You can access SOP knowledge through the RAG (Retrieval-Augmented Generation) system
- You help with review comment analysis, standardized action suggestions, and review-related questions

Key concepts you understand:
- Review Sheet: Dataset containing records requiring review
- Suggested Action: Standardized taxonomy from documented SOPs
- Review Comments: Analysis and notes from reviewers
- AI_SuggestedAction: AI-generated standardized action suggestions
- Confidence scores: 0.0 to 1.0 indicating certainty of suggestions
- SOPs: Standard operating procedures governing the review process

When answering questions:
- Be accurate and reference relevant SOPs when available
- If you don't know something specific, say so rather than hallucinating
- You can ask for clarification if needed
- Provide helpful, context-aware responses about review processes

You are helpful, accurate, and aware of your role in the agentic automation workflow."""


def get_lm_studio_url() -> str:
    """Get LM Studio URL from config or use default."""
    try:
        config_path = Path("config.json")
        if config_path.exists():
            config = json.loads(config_path.read_text(encoding="utf-8"))
            lm_studio_url = config.get("lm_studio_url", "http://127.0.0.1:1234/v1")
        else:
            lm_studio_url = "http://127.0.0.1:1234/v1"
    except Exception:
        lm_studio_url = "http://127.0.0.1:1234/v1"

    # Ensure URL ends with /v1
    if not lm_studio_url.endswith("/v1"):
        if lm_studio_url.endswith("/"):
            lm_studio_url = lm_studio_url + "v1"
        else:
            lm_studio_url = lm_studio_url + "/v1"

    return lm_studio_url


def get_rag_context(message: str, sop_indexer: SOPIndexer = None) -> str:
    """
    Get relevant SOP context using RAG if available and if message is Review-related.

    Args:
        message: User's message
        sop_indexer: SOPIndexer instance (optional)

    Returns:
        Context string with relevant SOP information
    """
    if sop_indexer is None:
        return ""

    # Check if message is Review-related
    mtcr_keywords = [
        "mtcr",
        "sop",
        "SOP-EXAMPLE",
        "quality review",
        "reason for correction",
        "complaint",
        "correction",
        "standardized",
        "site review",
        "technical",
    ]
    message_lower = message.lower()

    if not any(keyword in message_lower for keyword in mtcr_keywords):
        return ""

    try:
        # Retrieve relevant context
        context_chunks = sop_indexer.vector_store.search(message, top_k=3)
        if context_chunks:
            context_text = "\n\n".join(
                [
                    chunk.get("content", chunk.get("text", ""))[:500]
                    for chunk in context_chunks
                ]
            )
            return f"\n\nRelevant SOP Context:\n{context_text}"
    except Exception:
        pass

    return ""


def send_message(
    lm_studio_url: str,
    message: str,
    conversation_history: list = None,
    sop_indexer: SOPIndexer = None,
    include_rag: bool = True,
) -> tuple[str, list]:
    """
    Send a message to LM Studio and get response with review context.

    Args:
        lm_studio_url: LM Studio API endpoint
        message: User's message
        conversation_history: Previous messages in the conversation
        sop_indexer: SOPIndexer instance for RAG context (optional)
        include_rag: Whether to include RAG context for review-related questions

    Returns:
        Tuple of (response_text, updated_conversation_history)
    """
    if conversation_history is None:
        conversation_history = []

    # Add RAG context if available and message is review-related
    enhanced_message = message
    if include_rag and sop_indexer:
        rag_context = get_rag_context(message, sop_indexer)
        if rag_context:
            enhanced_message = f"{message}{rag_context}"

    # Add user message to history
    conversation_history.append({"role": "user", "content": enhanced_message})

    try:
        payload = {
            "model": "local-model",
            "messages": conversation_history,
            "temperature": 0.7,  # Slightly higher for more natural conversation
            "max_tokens": 1000,
            "stream": False,
        }

        response = requests.post(
            f"{lm_studio_url}/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60,
        )

        if response.status_code == 200:
            result = response.json()
            assistant_message = (
                result.get("choices", [{}])[0].get("message", {}).get("content", "")
            )

            # Add assistant response to history
            conversation_history.append(
                {"role": "assistant", "content": assistant_message}
            )

            return assistant_message, conversation_history
        else:
            return (
                f"[ERROR] Server returned status {response.status_code}: {response.text[:200]}",
                conversation_history,
            )

    except requests.exceptions.ConnectionError:
        return (
            "[ERROR] Cannot connect to LM Studio. Please ensure the server is running.",
            conversation_history,
        )
    except Exception as e:
        return f"[ERROR] {str(e)}", conversation_history


def main():
    """Main chat loop with Excel Review context awareness."""
    print("=" * 60)
    print("Excel Review Agent - LM Studio Chat Interface")
    print("=" * 60)
    print("\nThis connects to the same LLM model used by the Excel Review agent.")
    print("The LLM is aware of review workflows, SOPs, and agentic processes.")
    print("\nCommands:")
    print("  'quit' or 'exit' - End conversation")
    print("  'clear' - Clear conversation history")
    print("  'rag on/off' - Toggle RAG context (default: on)")
    print("=" * 60)
    print()

    lm_studio_url = get_lm_studio_url()
    print(f"Connecting to: {lm_studio_url}\n")

    # Initialize SOP indexer for RAG (optional)
    sop_indexer = None
    try:
        sop_indexer = SOPIndexer(embeddings_dir="data/embeddings")
        print("[OK] SOP Indexer loaded - RAG context available\n")
    except Exception as e:
        print(f"[INFO] SOP Indexer not available - RAG disabled ({str(e)[:50]})\n")

    # Initialize conversation with system prompt
    system_prompt = get_excel_review_system_prompt()
    conversation_history = [{"role": "system", "content": system_prompt}]

    # Test connection first
    test_response, _ = send_message(
        lm_studio_url,
        "Hello, are you connected and aware of your Excel Review role?",
        conversation_history.copy(),
        sop_indexer,
        include_rag=False,
    )
    if "[ERROR]" in test_response:
        print(f"{test_response}\n")
        print("Please:")
        print("  1. Open LM Studio")
        print("  2. Load a model")
        print("  3. Go to 'Local Server' tab")
        print("  4. Click 'Start Server'")
        print("  5. Run this script again")
        sys.exit(1)

    print("[OK] Connected to LM Studio with Excel Review context!\n")
    print("-" * 60)
    print()

    rag_enabled = True

    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.lower() in ["quit", "exit", "q"]:
                print("\nGoodbye!")
                break

            if user_input.lower() == "clear":
                # Reset to just system prompt
                conversation_history = [{"role": "system", "content": system_prompt}]
                print("[Conversation history cleared]\n")
                continue

            if user_input.lower() in ["rag on", "rag enable"]:
                rag_enabled = True
                print("[RAG context enabled]\n")
                continue

            if user_input.lower() in ["rag off", "rag disable"]:
                rag_enabled = False
                print("[RAG context disabled]\n")
                continue

            # Send message and get response
            print("Thinking...", end="\r")
            response, conversation_history = send_message(
                lm_studio_url,
                user_input,
                conversation_history,
                sop_indexer if rag_enabled else None,
                include_rag=rag_enabled,
            )
            print(" " * 20, end="\r")  # Clear "Thinking..." message

            print(f"Assistant: {response}\n")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except EOFError:
            print("\n\nGoodbye!")
            break


if __name__ == "__main__":
    main()
