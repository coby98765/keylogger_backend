@echo off
echo Activating virtual environment...

REM Check if the .venv folder exists
IF NOT EXIST .venv (
    echo Virtual environment not found. Creating one...
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate

REM Ensure Poetry is installed inside the virtual environment
where poetry >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo Poetry not found in virtual environment. Installing...
    pip install poetry
)

REM Install dependencies
echo Installing dependencies from pyproject.toml...
python -m poetry install

REM Start Flask server
echo Starting Flask server...
flask --app logger_backend run

pause
