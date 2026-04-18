@echo off
REM Frontend Startup Script for Windows
REM Tendworks Private Limited

echo.
echo ====================================
echo Leave Agent Manager Dashboard
echo ====================================
echo.

REM Check if in frontend directory
if not exist "app.py" (
    echo Error: Please run this script from the frontend directory
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo Error installing dependencies
    pause
    exit /b 1
)

REM Check if backend is running
echo.
echo Checking backend API...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Backend API is not responding
    echo Please start the backend first:
    echo   cd ..
    echo   python -m uvicorn app.main:app --reload
    echo.
    set /p continue="Continue anyway? (y/n): "
    if /i not "%continue%"=="y" exit /b 1
) else (
    echo Backend API is running - OK
)

echo.
echo ====================================
echo Starting dashboard...
echo Dashboard: http://localhost:8501
echo ====================================
echo.

REM Start Streamlit
streamlit run app.py
