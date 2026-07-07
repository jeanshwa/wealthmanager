#!/bin/bash
cd "$(dirname "$0")"
echo "📦 Pushing code + data to Git..."
git add -A
git commit -m "Update $(date '+%Y-%m-%d %H:%M')"
git push
if [ $? -eq 0 ]; then
    echo "✅ Done! Code + data pushed. Streamlit Cloud will auto-redeploy with your data."
else
    echo "❌ Push failed. Check your git remote config."
fi
