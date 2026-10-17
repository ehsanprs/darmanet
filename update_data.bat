@echo off
rem Double-click to refresh the website data from darmanet.ir
chcp 65001 >nul
cd /d "%~dp0"
rem Get location edits made in the website admin mode (committed on GitHub) first.
git pull --ff-only || echo Warning: could not pull the latest version from GitHub; continuing.
if not exist .venv\Scripts\python.exe (
  echo Creating Python environment...
  python -m venv .venv || goto :error
  .venv\Scripts\python -m pip install -q -r requirements.txt || goto :error
)
set PYTHONIOENCODING=utf-8
.venv\Scripts\python update_data.py %* || goto :error
echo.
echo Done. Next, run geocode_data.bat to find locations of new centers.
pause
exit /b 0
:error
echo.
echo Update failed. See the messages above.
pause
exit /b 1
