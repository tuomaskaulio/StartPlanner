#!/usr/bin/env bash
# Launch StartPlanner on macOS.
# Removes the quarantine attribute (applied by macOS when downloading from
# the internet) so Gatekeeper doesn't block the unsigned bundled binaries.
set -euo pipefail
APP_DIR="$(cd "$(dirname "$0")" && pwd)"

# Remove quarantine attributes so Gatekeeper doesn't block the app
xattr -rd com.apple.quarantine "$APP_DIR" 2>/dev/null || true

# Launch the app
exec "$APP_DIR/StartPlanner"