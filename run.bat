@echo off
echo === Running diagnostics ===
.venv\Scripts\python.exe diag.py
if %errorlevel% neq 0 (
    echo DIAGNOSTIC FAILED — check diag.log
    pause
    exit /b 1
)
echo === Starting Streamlit ===
.venv\Scripts\python.exe -m streamlit run app.py
