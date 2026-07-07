#!/bin/bash
cd "$(dirname "$0")"

# Check if data file exists
if [ ! -f "wealth_data.json" ]; then
    echo "⚠️  wealth_data.json not found!"
    echo "   Open the app, enter some data first, then run this again."
    exit 1
fi

# Check if git repo exists
if [ ! -d ".git" ]; then
    echo "⚠️  Not a git repo. Run: git init && git remote add origin <your-repo-url>"
    exit 1
fi

# Force add data file (in case it was previously gitignored)
git add --force wealth_data.json
git add -A

# Show what's being pushed
echo "📦 Files to push:"
git status --short

git commit -m "Update $(date '+%Y-%m-%d %H:%M')"
git push

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Done! Code + data pushed to GitHub."
    echo "   Streamlit Cloud will auto-redeploy with your data."
else
    echo ""
    echo "❌ Push failed. Check:"
    echo "   1. git remote -v  (is remote set?)"
    echo "   2. git status     (any conflicts?)"
fi
