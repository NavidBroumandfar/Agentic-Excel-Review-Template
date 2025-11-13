"""
Interactive LM Studio Test Script
This script helps you test LM Studio connection and see it in action.
"""

import sys
import json
import requests
from pathlib import Path

def test_connection():
    """Test basic connection to LM Studio."""
    print("=" * 60)
    print("LM Studio Connection Test")
    print("=" * 60)
    
    # Get LM Studio URL
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
    
    print(f"\nTesting connection to: {lm_studio_url}\n")
    
    try:
        # Test 1: Basic connection
        print("[TEST 1] Testing basic connection...")
        response = requests.get(f"{lm_studio_url.replace('/v1', '')}/v1/models", timeout=5)
        if response.status_code == 200:
            models = response.json()
            print(f"  [OK] Connected! Found {len(models.get('data', []))} model(s)")
            if models.get('data'):
                print(f"  Available models:")
                for model in models['data'][:3]:  # Show first 3
                    print(f"    - {model.get('id', 'Unknown')}")
        else:
            print(f"  [WARNING] Server responded with status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("  [ERROR] Cannot connect to LM Studio server")
        print("  -> Please start LM Studio and click 'Start Server'")
        return False
    except Exception as e:
        print(f"  [ERROR] {str(e)}")
        return False
    
    # Test 2: Chat completion
    print("\n[TEST 2] Testing chat completion...")
    try:
        payload = {
            "model": "local-model",
            "messages": [
                {
                    "role": "user",
                    "content": "Say hello, you are connected to MTCR Agentic Pipeline. Respond in one short sentence."
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
            timeout=30,
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"  [OK] Chat completion successful!")
            print(f"  Response: {content}")
            return True
        else:
            print(f"  [ERROR] Server returned status {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"  [ERROR] {str(e)}")
        return False

def main():
    """Main entry point."""
    success = test_connection()
    
    print("\n" + "=" * 60)
    if success:
        print("[SUCCESS] LM Studio is connected and working!")
        print("\nNext steps:")
        print("  1. Run full demo: python src/run_mtcr_demo.py --n 5")
        print("  2. Check logs: logs/mtcr_review_assistant.jsonl")
    else:
        print("[FAILED] LM Studio is not connected")
        print("\nTo fix:")
        print("  1. Open LM Studio application")
        print("  2. Load a model")
        print("  3. Go to 'Local Server' tab")
        print("  4. Click 'Start Server'")
        print("  5. Run this test again")
    print("=" * 60)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

