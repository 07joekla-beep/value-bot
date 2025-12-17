#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
python -m pip install --upgrade pip >/dev/null
pip install -r requirements.txt >/dev/null

# Open browser (best-effort)
python - <<'PY'
import webbrowser
webbrowser.open("http://localhost:8501")
PY

streamlit run app.py

./run_mac_linux.sh

