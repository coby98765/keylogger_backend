@echo off
echo Activating virtual environment...
call .venv\Scripts\activate

echo Installing dependencies from pyproject.toml...
poetry install

echo Starting Flask server...
flask --app logger_backend run

pause
