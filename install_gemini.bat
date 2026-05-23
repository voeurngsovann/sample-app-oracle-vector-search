@echo off
echo Installing google-generativeai into .venv...
.venv\Scripts\python.exe -m pip install "google-generativeai>=0.8.0"
echo.
echo Verifying...
.venv\Scripts\python.exe -c "import google.generativeai; print('google-generativeai OK:', google.generativeai.__version__)"
pause
