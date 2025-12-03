# ⚠️ Compliance Notice:
# Assistive mode only. No modifications to validated Excel ranges.
# All AI outputs must be written to new files or new columns prefixed with "AI_".
# This module is for local prototype demonstration only.

"""
LM Studio Smoke Test
Tests connection to LM Studio API endpoint.
"""

from __future__ import annotations
import json
import sys
from pathlib import Path
import requests

from src.utils.config_loader import load_config


def test_lm_studio_connection(lm_studio_url: str = None) -> bool:
    """
    Test connection to LM Studio API.

    Args:
        lm_studio_url: LM Studio API endpoint (defaults to config.json or http://127.0.0.1:1234/v1)

    Returns:
        True if connection successful, False otherwise
    """
    # Load config to get LM Studio URL if not provided
    if lm_studio_url is None:
        try:
            config_path = Path("config.json")
            if config_path.exists():
                config = json.loads(config_path.read_text(encoding="utf-8"))
                lm_studio_url = config.get("lm_studio_url", "http://127.0.0.1:1234/v1")
            else:
                lm_studio_url = "http://127.0.0.1:1234/v1"
        except Exception:
            lm_studio_url = "http://127.0.0.1:1234/v1"

    # Ensure URL ends with /v1 if not present
    if not lm_studio_url.endswith("/v1"):
        if lm_studio_url.endswith("/"):
            lm_studio_url = lm_studio_url + "v1"
        else:
            lm_studio_url = lm_studio_url + "/v1"

    print(f"[SMOKE TEST] Testing connection to: {lm_studio_url}")

    try:
        # Test basic chat completion
        payload = {
            "model": "local-model",
            "messages": [
                {
                    "role": "user",
                    "content": "Say hello, you are connected to Excel Review Agentic Pipeline.",
                }
            ],
            "temperature": 0.1,
            "max_tokens": 50,
            "stream": False,
        }

        response = requests.post(
            f"{lm_studio_url}/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )

        if response.status_code == 200:
            result = response.json()
            content = (
                result.get("choices", [{}])[0].get("message", {}).get("content", "")
            )
            print("[OK] Connected to LM Studio")
            print(f"  Response: {content[:100]}...")
            return True
        else:
            print(f"[ERROR] Connection failed: Status {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Connection failed: Could not connect to {lm_studio_url}")
        print(f"  Please ensure LM Studio is running and the server is started.")
        return False
    except requests.exceptions.Timeout:
        print(f"[ERROR] Connection failed: Request timed out")
        return False
    except Exception as e:
        print(f"[ERROR] Connection failed: {str(e)}")
        return False


def test_lmstudio_connection() -> bool:
    """
    Programmatic smoke test for LM Studio connection.
    
    Returns:
        True if the test request succeeds and a response is returned.
        False if the request fails or the server is not reachable.
    """
    return test_lm_studio_connection()


def main():
    """Main entry point for smoke test."""
    success = test_lmstudio_connection()
    print("LM Studio connection OK" if success else "LM Studio connection FAILED")
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
