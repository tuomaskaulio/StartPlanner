#!/usr/bin/env bash
# Build StartPlanner one-folder app for macOS (unsigned).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python -m pip install -e ".[packaging]"
pyinstaller --noconfirm --clean packaging/startplanner.spec
# Remove quarantine attributes so Gatekeeper doesn't block the app
xattr -rd com.apple.quarantine "$ROOT/dist/StartPlanner/" 2>/dev/null || true
echo "Built: $ROOT/dist/StartPlanner/"
echo "Note: Gatekeeper may block unsigned apps; allow in System Settings if needed."
