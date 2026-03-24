@echo off
echo =========================================
echo   🚀 Netlify 웹사이트 자동 업데이트 🚀
echo =========================================
cd /d "%~dp0"
python auto_update.py
echo.
pause