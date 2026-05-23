@echo off
echo === Checking pymupdf availability for Python 3.14 Windows ===
echo.
echo -- pip index (available versions) --
.venv\Scripts\python.exe -m pip index versions pymupdf
echo.
echo -- attempting install with verbose output --
.venv\Scripts\python.exe -m pip install "pymupdf>=1.27.2.3" -v 2>&1 | findstr /i "found looking requires python version"
echo.
echo -- checking what is installed --
.venv\Scripts\python.exe -m pip show pymupdf
echo.
echo -- trying direct import --
.venv\Scripts\python.exe -c "import pymupdf; print('pymupdf OK:', pymupdf.__version__)"
.venv\Scripts\python.exe -c "import fitz; print('fitz OK:', fitz.__version__)"
pause
