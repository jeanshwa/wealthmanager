#!/bin/bash
cd "$(dirname "$0")"
if [ ! -d "venv" ]; then
    echo "⏳ First time setup — installing dependencies..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi
echo "🚀 Starting Wealth Manager at http://localhost:8501"
streamlit run app.py
