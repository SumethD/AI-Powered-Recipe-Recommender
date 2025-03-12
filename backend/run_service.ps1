# Recipe Instructions Service Launcher
Write-Host "Starting Recipe Instructions Service..." -ForegroundColor Cyan

# Check if Python is installed
try {
    $pythonVersion = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    Write-Host "Found Python $pythonVersion" -ForegroundColor Green
    
    # Check Python version
    $versionParts = $pythonVersion.Split('.')
    $major = [int]$versionParts[0]
    $minor = [int]$versionParts[1]
    
    if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
        Write-Host "Python 3.8 or higher is required. You have $pythonVersion" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Python is not installed or not in PATH. Please install Python 3.8 or higher." -ForegroundColor Red
    exit 1
}

# Set working directory to the script's location
Set-Location $PSScriptRoot

# Check if virtual environment exists, create if not
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Check if .env file exists, create from example if not
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Write-Host "Creating .env file from example..." -ForegroundColor Yellow
        Copy-Item .env.example .env
        Write-Host "Please edit the .env file and add your OpenAI API key." -ForegroundColor Magenta
    } else {
        Write-Host "Creating default .env file..." -ForegroundColor Yellow
        @"
OPENAI_API_KEY=your_api_key_here
PORT=8000
HOST=0.0.0.0
CACHE_TTL=86400
SCRAPING_RATE_LIMIT=100
OPENAI_RATE_LIMIT=20
"@ | Out-File -FilePath .env -Encoding utf8
        Write-Host "Please edit the .env file and add your OpenAI API key." -ForegroundColor Magenta
    }
}

# Start the service
Write-Host "Starting Recipe Instructions Service..." -ForegroundColor Green
python -m uvicorn recipe_instructions_service:app --host 0.0.0.0 --port 8000 --reload

# Deactivate virtual environment when done
deactivate