#!/bin/bash
set -e

echo "🔧 Making setup.sh and script.sh executable..."
chmod +x setup.sh script.sh

echo "🚀 Running setup.sh..."
./setup.sh

echo "📁 Creating desktop shortcut for Streamlit UI..."

DESKTOP_FILE="$HOME/.local/share/applications/InterfaceUI.desktop"
PYTHON_FILE_PATH="$(pwd)/nmat/ui_interface.py"
VENV_ACTIVATE_PATH="$(pwd)/nmat/nlmt_env/bin/activate"

mkdir -p "$(dirname "$DESKTOP_FILE")"

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=Interface UI
Comment=Launch the Streamlit UI Interface
Exec=bash -c "cd $(pwd)/nmat && source nlmt_env/bin/activate && cd .. && streamlit run ui_interface.py"
Icon=utilities-terminal
Terminal=true
Type=Application
Categories=Utility;
EOF

chmod +x "$DESKTOP_FILE"

echo "✅ Desktop shortcut created at: $DESKTOP_FILE"

