#!/usr/bin/env bash
# Fast pre-commit guard - only check essential governance
set -euo pipefail

# Quick check: if /src changed, ensure governance files were touched
if git diff --cached --name-only | grep -q '^src/'; then
  if ! git diff --cached --name-only | grep -qE '^(src/context/ProjectVision\.ts|docs/prompts/)'; then
    echo "❌ Quick check: Modified /src but no governance update detected"
    echo "   → Update ProjectVision.ts or docs/prompts/ files"
    echo "   → Or use: git commit --no-verify to skip"
    exit 1
  fi
fi
echo '✅ Pre-commit checks passed.'
