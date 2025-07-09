#!/bin/bash
set -e

echo "Creating 'nmat' folder..."
mkdir -p nmat
cd nmat

echo "📦 Installing system dependencies..."
sudo apt update && sudo apt install -y git python3-venv python3-pip

echo "🐍 Creating Python virtual environment in ./nlmt_env ..."
python3 -m venv nlmt_env

echo "🧪 Activating virtual environment..."
source nlmt_env/bin/activate

echo "installing iperf3"
sudo apt install iperf3
echo "sucessfully installed iperf3"

echo "📥 Cloning NLMT repository into ./nmat/nlmt ..."
git clone https://github.com/samiemostafavi/nlmt.git

cd nlmt

echo "🔍 Checking for installable Python package..."
if [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then
    echo "📦 Installing NLMT with pip..."
    pip install --upgrade pip setuptools
    pip install .
else
    echo "⚠️  No setup.py or pyproject.toml found. Skipping pip install."
fi
cd ..

echo "📜 Installing requirements.txt if available..."
if [ -f "../requirements.txt" ]; then
    cp ../requirements.txt .
    pip install -r requirements.txt
else
    echo "⚠️  requirements.txt not found in parent folder. Skipping."
fi

echo "✅ Installation complete."
echo ""
echo "👉 To run the app:"
echo "   source nmat/nlmt_env/bin/activate"
echo "   streamlit run nlmt/ui_interface.py"


#V1.2.1
