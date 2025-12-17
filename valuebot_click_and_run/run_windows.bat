@echo off
setlocal
cd /d %~dp0

if not exist .venv (
  py -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul
pip install -r requirements.txt

start "" http://localhost:8501
streamlit run app.py
