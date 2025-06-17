set -e  # Stop on error

echo "📁 Creating 'nmat' folder..."
mkdir -p nmat
cd nmat

echo "📦 Installing system dependencies..."
sudo apt update && sudo apt install git python3-venv -y

echo "🐍 Creating Python virtual environment in ./nlmt_env ..."
python3 -m venv nlmt_env
source nlmt_env/bin/activate

echo "📥 Cloning NLMT repository into ./nmat/nlmt ..."
git clone https://github.com/samiemostafavi/nlmt.git

echo "🔧 Installing NLMT from source..."
cd nlmt
pip install .
cd ..

echo "📜 Installing requirements.txt if available..."
if [ -f "../requirements.txt" ]; then
    cp ../requirements.txt .
    pip install -r requirements.txt
else
    echo "⚠️  requirements.txt not found in parent folder. Skipping."
fi

echo "✅ Installation complete."
echo "👉 To run: source nmat/nlmt_env/bin/activate && streamlit run main_ui.py"
