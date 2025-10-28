#!/usr/bin/env bash
# Block commits if /src changes but no vision/log updates were touched.
set -euo pipefail
CHANGED=$(git diff --cached --name-only || true)

needs_guard=false
echo "$CHANGED" | grep -E '^src/' >/dev/null && needs_guard=true || true

if [ "$needs_guard" = true ]; then
  echo "$CHANGED" | grep -E '^(src/context/ProjectVision\.ts|docs/prompts/log\.jsonl|docs/prompts/module-.*\.txt)$' >/dev/null || {
    echo "❌ Pre-commit guard:"
    echo "   You modified /src but did not update ProjectVision.ts or prompt logs."
    echo "   → Add an entry to docs/prompts/log.jsonl AND paste prompt to docs/prompts/module-XX.txt"
    echo "   → If you changed phase status, run VisionSync, e.g.:"
    echo "      python scripts/vision_sync.py --phase M2 --status active --note 'Start M2 dev'"
    echo "      python scripts/vision_sync.py --phase M1.2 --status completed --note 'Sub-phase done'"
    echo "   → Auto-create module files with: --create-module flag"
    exit 1
  }
fi
echo '✅ Pre-commit checks passed.'
