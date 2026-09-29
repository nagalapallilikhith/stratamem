@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  set "PYTHON_CMD=python"
) else (
  set "PYTHON_CMD=py"
)
if not exist ".venv\Scripts\python.exe" (
  echo Preparing the application environment...
  %PYTHON_CMD% -m venv .venv
  if errorlevel 1 goto fail
)
.venv\Scripts\python.exe -c "import hindsight_client" >nul 2>nul
if errorlevel 1 (
  echo Installing the official Hindsight client. Internet is needed for this first setup.
  .venv\Scripts\python.exe -m pip --isolated install --index-url https://pypi.org/simple --keyring-provider disabled --disable-pip-version-check -r requirements.txt
  if errorlevel 1 goto fail
)
echo.
echo Open http://127.0.0.1:8000 in your browser.
echo Keep this window open while using STRATAMEM.
echo.
.venv\Scripts\python.exe app.py
pause
exit /b
:fail
echo Setup failed. Install Python 3.11 or newer, then try again.
echo You can still use local reasoning with: python app.py
pause
