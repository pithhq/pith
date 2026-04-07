#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BINARY="$PROJECT_ROOT/dist/pith"
APPDIR="$PROJECT_ROOT/dist/PITH.AppDir"

if [ ! -f "$BINARY" ]; then
    echo "Binary not found at $BINARY. Run build.sh first." >&2
    exit 1
fi

if ! command -v appimagetool &>/dev/null; then
    echo "appimagetool not found." >&2
    echo "Install it:" >&2
    echo "  wget https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage" >&2
    echo "  chmod +x appimagetool-x86_64.AppImage" >&2
    echo "  sudo mv appimagetool-x86_64.AppImage /usr/local/bin/appimagetool" >&2
    exit 1
fi

rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin"

cp "$BINARY" "$APPDIR/usr/bin/pith"

cat > "$APPDIR/pith.desktop" <<DESKTOP
[Desktop Entry]
Name=PITH
Exec=pith
Icon=pith
Type=Application
Categories=Utility;
DESKTOP

# Placeholder icon — replace with actual icon before release
if [ -f "$SCRIPT_DIR/assets/icon.png" ]; then
    cp "$SCRIPT_DIR/assets/icon.png" "$APPDIR/pith.png"
else
    # Create a 1x1 placeholder so appimagetool does not fail
    convert -size 256x256 xc:transparent "$APPDIR/pith.png" 2>/dev/null || \
        printf '' > "$APPDIR/pith.png"
fi

cat > "$APPDIR/AppRun" <<'APPRUN'
#!/usr/bin/env bash
HERE="$(dirname "$(readlink -f "$0")")"
exec "$HERE/usr/bin/pith" "$@"
APPRUN
chmod +x "$APPDIR/AppRun"

OUTPUT="$PROJECT_ROOT/dist/PITH-x86_64.AppImage"
ARCH=x86_64 appimagetool "$APPDIR" "$OUTPUT"

rm -rf "$APPDIR"
echo "AppImage created: $OUTPUT"
