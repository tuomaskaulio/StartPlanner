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

# Copy launcher script into the app folder so users can launch without
# Gatekeeper blocking the unsigned bundled binaries
cp "$ROOT/packaging/launch_macos.sh" "$ROOT/dist/StartPlanner/launch_macos.sh"
chmod +x "$ROOT/dist/StartPlanner/launch_macos.sh"

# Remove quarantine attributes so Gatekeeper doesn't block the app
xattr -rd com.apple.quarantine "$ROOT/dist/StartPlanner/" 2>/dev/null || true
echo "Built: $ROOT/dist/StartPlanner/"
echo "Launch with: ./dist/StartPlanner/launch_macos.sh"
echo "Note: Gatekeeper may block unsigned apps; allow in System Settings if needed."

# The spec also produces a StartPlanner.app bundle (proper Finder/Dock icon).
# Same stale-signature issue applies, plus the bundled Python.framework
# binary (no file extension, so it's not caught by the *.so/*.dylib find above).
if [ -d "$ROOT/dist/StartPlanner.app" ]; then
  find "$ROOT/dist/StartPlanner.app" \( -name "*.so" -o -name "*.dylib" \) -exec codesign --remove-signature {} \; 2>/dev/null || true
  find "$ROOT/dist/StartPlanner.app/Contents/Frameworks" -type f ! -name "*.*" -exec sh -c 'file "$1" | grep -q "Mach-O" && codesign --remove-signature "$1"' _ {} \; 2>/dev/null || true
  codesign --force --deep --sign - "$ROOT/dist/StartPlanner.app" 2>/dev/null || true
  xattr -rd com.apple.quarantine "$ROOT/dist/StartPlanner.app" 2>/dev/null || true
  echo "Built: $ROOT/dist/StartPlanner.app"
fi
