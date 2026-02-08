@echo off
echo 🚀 Auto-pushing to GitHub Profile Repository...
echo.
echo Waiting for repository locfaker/locfaker to be created...
echo.

:retry
echo Trying to push... (Press Ctrl+C to stop)
git push -u origin main
if %errorlevel% == 0 (
    echo.
    echo ✅ SUCCESS! Your GitHub profile has been updated!
    echo 🌟 Visit: https://github.com/locfaker/locfaker
    echo.
    pause
    exit
) else (
    echo ❌ Repository not found yet. Retrying in 10 seconds...
    timeout /t 10 /nobreak >nul
    goto retry
)
