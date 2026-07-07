@echo off
cd /d "%~dp0"

if not exist "wealth_data.json" (
    echo WARNING: wealth_data.json not found!
    echo Open the app, enter some data first, then run this again.
    pause
    exit /b 1
)

if not exist ".git" (
    echo WARNING: Not a git repo. Run: git init
    pause
    exit /b 1
)

echo Pushing code + data to Git...
git add --force wealth_data.json
git add -A

echo Files to push:
git status --short

git commit -m "Update %date% %time%"
git push

if %errorlevel%==0 (
    echo.
    echo Done! Code + data pushed. Cloud will auto-redeploy.
) else (
    echo.
    echo Push failed. Check: git remote -v
)
pause
