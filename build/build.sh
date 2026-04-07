#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Building PITH binary..."
pyinstaller "$SCRIPT_DIR/pith.spec" --clean --distpath "$PROJECT_ROOT/dist/"

BINARY="$PROJECT_ROOT/dist/pith"
if [ -f "$BINARY" ]; then
    echo "Build complete: $BINARY"
else
    echo "Build failed: binary not found at $BINARY" >&2
    exit 1
fi
