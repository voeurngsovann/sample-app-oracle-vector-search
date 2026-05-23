@echo off
echo ================================================
echo  Setting up virtual environment in .venv
echo ================================================
echo.

:: Remove broken venv if it exists
if exist .venv (
    echo Removing existing .venv...
    rmdir /s /q .venv
)

:: Create fresh venv using the confirmed Python 3.14
C:\Python314\python.exe -m venv .venv

echo.
echo Upgrading pip inside venv...
.venv\Scripts\python.exe -m pip install --upgrade pip

echo.
echo Installing project packages...
.venv\Scripts\python.exe -m pip install -r requirements.txt

echo.
echo ================================================
echo  Verifying installation...
echo ================================================
.venv\Scripts\python.exe check_env.py

echo.
echo ================================================
echo  Setup complete! Run the app with:  run.bat
echo ================================================
pause
