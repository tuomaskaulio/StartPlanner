#!/usr/bin/env bash
# Build StartPlanner one-folder app for macOS (unsigned).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python -m pip install -e ".[packaging]"
pyinstaller --noconfirm --clean packaging/startplanner.spec

# Re-sign all bundled binaries with fresh adhoc signatures.
# PyInstaller bundles .so/.dylib files that carry stale adhoc signatures
# from the build machine's Python install. macOS rejects these when the
# app is downloaded and run on another machine ("library load disallowed
# by system policy"). Removing and re-signing adhoc fixes this.
find "$ROOT/dist/StartPlanner" \( -name "*.so" -o -name "*.dylib" \) -exec codesign --remove-signature {} \; 2>/dev/null || true
codesign --force --deep --sign - "$ROOT/dist/StartPlanner/StartPlanner" 2>/dev/null || true

# Remove quarantine attributes so Gatekeeper doesn't block the app
xattr -rd com.apple.quarantine "$ROOT/dist/StartPlanner/" 2>/dev/null || true
echo "Built: $ROOT/dist/StartPlanner/"
echo "Note: Gatekeeper may block unsigned apps; allow in System Settings if needed."
