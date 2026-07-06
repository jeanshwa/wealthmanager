@echo off
cd /d "%~dp0"
if not exist "venv" (
    echo First time setup - installing dependencies...
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate
)
echo Starting Wealth Manager at http://localhost:8501
streamlit run app.py
pause
