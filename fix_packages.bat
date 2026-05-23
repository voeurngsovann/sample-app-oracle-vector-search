@echo off
echo ================================================
echo  Installing missing packages into .venv
echo ================================================
echo.

echo Installing pymupdf...
.venv\Scripts\python.exe -m pip install "pymupdf>=1.27.2.3"

echo.
echo Installing python-docx...
.venv\Scripts\python.exe -m pip install "python-docx>=1.1.0"

echo.
echo Verifying...
.venv\Scripts\python.exe -c "import pymupdf; print('pymupdf OK:', pymupdf.__version__)"
.venv\Scripts\python.exe -c "import docx; print('python-docx OK')"

echo.
echo ================================================
echo  Done — run the app with: run.bat
echo ================================================
pause
