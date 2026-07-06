@echo off
cd /d "%~dp0"
echo Pushing to Git...
git add -A
git commit -m "Update %date% %time%"
git push
if %errorlevel%==0 (
    echo Done! Streamlit Cloud will auto-redeploy.
) else (
    echo Push failed. Check your git remote config.
)
pause
