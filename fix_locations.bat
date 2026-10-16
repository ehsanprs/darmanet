@echo off
rem Double-click to fix missing or doubtful map points by searching center names (Neshan search)
chcp 65001 >nul
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo Creating Python environment...
  python -m venv .venv || goto :error
  .venv\Scripts\python -m pip install -q -r requirements.txt || goto :error
)
set PYTHONIOENCODING=utf-8
.venv\Scripts\python fix_locations.py %* || goto :error
echo.
echo Done. Centers that could not be fixed are listed in location_review.txt.
pause
exit /b 0
:error
echo.
echo Location fixing failed. See the messages above.
pause
exit /b 1
