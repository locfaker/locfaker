@echo off
echo 🚀 Pushing to GitHub Profile Repository...
echo.

git status
echo.

echo Adding all files...
git add .

echo.
echo Committing changes...
git commit -m "✨ Update GitHub profile with beautiful animations and dynamic effects"

echo.
echo Pushing to GitHub...
git push -u origin main

if %errorlevel% == 0 (
    echo.
    echo ✅ SUCCESS! Your GitHub profile has been updated!
    echo 🌟 Visit: https://github.com/locfaker
    echo.
) else (
    echo.
    echo ❌ Push failed. Please check:
    echo 1. Repository 'locfaker' exists on GitHub
    echo 2. You have push permissions
    echo 3. Internet connection is stable
    echo.
)

pause
