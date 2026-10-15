@echo off
rem Double-click to refresh the website data from darmanet.ir
chcp 65001 >nul
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo Creating Python environment...
  python -m venv .venv || goto :error
  .venv\Scripts\python -m pip install -q -r requirements.txt || goto :error
)
set PYTHONIOENCODING=utf-8
.venv\Scripts\python update_data.py %* || goto :error
echo.
echo Done. Open site\index.html to see the updated data.
pause
exit /b 0
:error
echo.
echo Update failed. See the messages above.
pause
exit /b 1
