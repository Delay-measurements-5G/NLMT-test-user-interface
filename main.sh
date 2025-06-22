#!/bin/bash
set -e

echo "🔧 Making setup.sh and script.sh executable..."
chmod +x setup.sh script.sh

echo "🚀 Running setup.sh..."
./setup.sh

echo "📁 Creating desktop shortcut for UI..."

DESKTOP_FILE=~/.local/share/applications/InterfaceUI.desktop
SCRIPT_PATH="$(pwd)/script.sh"

mkdir -p ~/.local/share/applications

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=Interface UI
Comment=Launch the UI Interface
Exec=$SCRIPT_PATH
Icon=utilities-terminal
Terminal=true
Type=Application
Categories=Utility;
EOF

chmod +x "$DESKTOP_FILE"

echo "✅ Desktop shortcut created at: $DESKTOP_FILE"
