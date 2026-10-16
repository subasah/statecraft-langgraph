#!/usr/bin/env bash
set -e

# StateCraft Launcher Script
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

VENV=".venv"
if [ ! -d "$VENV" ]; then
    echo "Creating virtual environment..."
    uv venv .venv
    source .venv/bin/activate
    uv pip install -e .
else
    source .venv/bin/activate
fi

echo "=========================================================="
echo "         STATECRAFT: STATEFUL AGENTIC WORKFLOWS           "
echo "=========================================================="
echo "Select execution target:"
echo "  1) Run All Pytests (14/14 tests)"
echo "  2) Launch Streamlit Visual Studio (Web Dashboard)"
echo "  3) Launch Interactive Rich CLI"
echo "  4) Start FastAPI REST API Server"
echo "  5) Open Interactive HTML Documentation in Browser"
echo "  0) Exit"
echo ""

read -p "Enter choice [1-5]: " choice

case "$choice" in
    1)
        pytest tests/ -v
        ;;
    2)
        streamlit run streamlit_app.py
        ;;
    3)
        python -m statecraft.cli
        ;;
    4)
        uvicorn statecraft.api:app --reload --port 8000
        ;;
    5)
        open docs/index.html || xdg-open docs/index.html || echo "Open docs/index.html in your browser."
        ;;
    0)
        echo "Exiting."
        exit 0
        ;;
    *)
        echo "Invalid selection."
        exit 1
        ;;
esac
