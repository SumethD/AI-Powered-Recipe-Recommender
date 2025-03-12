@echo off
echo Starting Recipe Instructions Service...

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH. Please install Python 3.8 or higher.
    exit /b 1
)

REM Check Python version
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"
if %ERRORLEVEL% NEQ 0 (
    echo Python 3.8 or higher is required.
    exit /b 1
)

REM Check if virtual environment exists, create if not
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists, create from example if not
if not exist .env (
    if exist .env.example (
        echo Creating .env file from example...
        copy .env.example .env
        echo Please edit the .env file and add your OpenAI API key.
    ) else (
        echo Creating default .env file...
        echo OPENAI_API_KEY=your_api_key_here > .env
        echo PORT=8000 >> .env
        echo HOST=0.0.0.0 >> .env
        echo CACHE_TTL=86400 >> .env
        echo SCRAPING_RATE_LIMIT=100 >> .env
        echo OPENAI_RATE_LIMIT=20 >> .env
        echo Please edit the .env file and add your OpenAI API key.
    )
)

REM Start the service
echo Starting Recipe Instructions Service...
python -m uvicorn recipe_instructions_service:app --host 0.0.0.0 --port 8000 --reload

REM Deactivate virtual environment when done
call venv\Scripts\deactivate.bat 