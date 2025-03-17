# PowerShell script to run backend services for the AI-Powered Recipe Recommender

Write-Host "Starting AI-Powered Recipe Recommender Backend..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow

# Function to check if a port is in use
function Test-PortInUse {
    param (
        [int]$Port
    )
    
    $connections = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -eq $Port }
    return $connections
}

# Function to kill a process that's using a port
function Stop-ProcessUsingPort {
    param (
        [int]$Port
    )
    
    $connections = Test-PortInUse -Port $Port
    if ($connections) {
        $procIds = $connections | Select-Object -ExpandProperty OwningProcess -Unique
        
        foreach ($procId in $procIds) {
            $process = Get-Process -Id $procId -ErrorAction SilentlyContinue
            if ($process) {
                Write-Host "Found process using port ${Port}: $($process.ProcessName) (PID: $procId)" -ForegroundColor Yellow
                Write-Host "Stopping process..." -ForegroundColor Yellow
                Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
                Start-Sleep -Seconds 1
                
                # Check if process is still running
                $processStillRunning = Get-Process -Id $procId -ErrorAction SilentlyContinue
                if ($processStillRunning) {
                    Write-Host "Failed to stop process. Please stop it manually." -ForegroundColor Red
                    return $false
                } else {
                    Write-Host "Successfully stopped process using port ${Port}" -ForegroundColor Green
                    return $true
                }
            }
        }
    }
    
    return $false
}

# Function to check if an API is available and responding
function Test-ApiAvailable {
    param (
        [string]$Url,
        [int]$MaxAttempts = 15,
        [int]$DelaySeconds = 2
    )
    
    Write-Host "Testing API availability: $Url" -ForegroundColor Cyan
    $available = $false
    $attempts = 0
    
    while (-not $available -and $attempts -lt $MaxAttempts) {
        try {
            $attempts++
            Write-Host "Attempt $attempts of $MaxAttempts..." -ForegroundColor Cyan
            $response = Invoke-WebRequest -Uri $Url -Method GET -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                $available = $true
                Write-Host "API is available at $Url" -ForegroundColor Green
            }
        }
        catch {
            Write-Host "API not yet available. Waiting $DelaySeconds seconds before retry..." -ForegroundColor Yellow
            Start-Sleep -Seconds $DelaySeconds
        }
    }
    
    if (-not $available) {
        Write-Host "WARNING: API at $Url could not be reached after $MaxAttempts attempts" -ForegroundColor Red
    }
    
    return $available
}

# Function to start a process and verify it's running
function Start-ServiceProcess {
    param (
        [string]$Name,
        [string]$FilePath,
        [string]$Arguments,
        [string]$LogFile,
        [string]$ErrorLogFile,
        [string]$HealthCheckUrl = $null,
        [int]$HealthCheckMaxAttempts = 15
    )
    
    Write-Host "Starting $Name..." -ForegroundColor Cyan
    
    # Check if process is already running
    $existingProcess = Get-Process | Where-Object { $_.CommandLine -like "*$Arguments*" } -ErrorAction SilentlyContinue
    if ($existingProcess) {
        Write-Host "WARNING: $Name appears to be already running (PID: $($existingProcess.Id))" -ForegroundColor Yellow
        Write-Host "Trying to stop the existing process..." -ForegroundColor Yellow
        Stop-Process -Id $existingProcess.Id -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
    
    # Start the process
    $process = Start-Process -FilePath $FilePath -ArgumentList $Arguments -RedirectStandardOutput $LogFile -RedirectStandardError $ErrorLogFile -NoNewWindow -PassThru
    
    if (-not $process) {
        Write-Host "ERROR: Failed to start $Name" -ForegroundColor Red
        return $false
    }
    
    Write-Host "$Name started with PID: $($process.Id)" -ForegroundColor Green
    
    # Wait a moment for the process to initialize
    Start-Sleep -Seconds 3
    
    # Verify the process is still running
    $processStillRunning = Get-Process -Id $process.Id -ErrorAction SilentlyContinue
    if (-not $processStillRunning) {
        Write-Host "ERROR: $Name process terminated unexpectedly. Check error log at $ErrorLogFile" -ForegroundColor Red
        return $false
    }
    
    # If a health check URL is provided, verify the service is responding
    if ($HealthCheckUrl) {
        $apiAvailable = Test-ApiAvailable -Url $HealthCheckUrl -MaxAttempts $HealthCheckMaxAttempts
        if (-not $apiAvailable) {
            Write-Host "ERROR: $Name is running but not responding at $HealthCheckUrl" -ForegroundColor Red
            Write-Host "Check logs at $LogFile and $ErrorLogFile" -ForegroundColor Red
            return $false
        }
    }
    
    return $true
}

# Function to install or update required Python packages
function Install-RequiredPackages {
    Write-Host "Checking and installing required Python packages..." -ForegroundColor Cyan
    
    # Install youtube-transcript-api with a specific version that's confirmed to work
    Write-Host "Installing youtube-transcript-api..." -ForegroundColor Cyan
    & python -m pip install --upgrade youtube-transcript-api
    
    # Install other required packages
    Write-Host "Installing other required packages from requirements.txt..." -ForegroundColor Cyan
    if (Test-Path -Path "backend/requirements.txt") {
        & python -m pip install -r backend/requirements.txt
    } else {
        Write-Host "WARNING: requirements.txt not found. Skipping package installation." -ForegroundColor Yellow
    }
}

# Check if ports are available
$portsToCheck = @(
    @{Port = 5000; Service = "Main Backend API"; Required = $true},
    @{Port = 8002; Service = "AllRecipes API"; Required = $false}
)
$portConflicts = @()

foreach ($portInfo in $portsToCheck) {
    $connections = Test-PortInUse -Port $portInfo.Port
    if ($connections) {
        $portConflicts += $portInfo
    }
}

if ($portConflicts.Count -gt 0) {
    Write-Host "Port conflicts detected:" -ForegroundColor Yellow
    foreach ($conflict in $portConflicts) {
        $process = Get-Process -Id (Test-PortInUse -Port $conflict.Port | Select-Object -First 1).OwningProcess -ErrorAction SilentlyContinue
        $processName = if ($process) { "$($process.ProcessName) (PID: $($process.Id))" } else { "Unknown process" }
        
        if ($conflict.Required) {
            Write-Host "  - Port $($conflict.Port) is required for $($conflict.Service) but is in use by $processName" -ForegroundColor Red
        } else {
            Write-Host "  - Port $($conflict.Port) is used by $($conflict.Service) but is in use by $processName" -ForegroundColor Yellow
        }
    }
    
    $choice = Read-Host "Would you like to: (K)ill conflicting processes, (S)kip affected services, or (E)xit? [K/S/E]"
    
    switch ($choice.ToUpper()) {
        "K" {
            Write-Host "Attempting to kill conflicting processes..." -ForegroundColor Cyan
            $allKilled = $true
            
            foreach ($conflict in $portConflicts) {
                $killed = Stop-ProcessUsingPort -Port $conflict.Port
                if (-not $killed -and $conflict.Required) {
                    Write-Host "ERROR: Failed to free up required port $($conflict.Port) for $($conflict.Service)" -ForegroundColor Red
                    $allKilled = $false
                }
            }
            
            if (-not $allKilled) {
                Write-Host "Not all required processes could be killed. Please close them manually and try again." -ForegroundColor Red
                exit 1
            }
        }
        "S" {
            $requiredConflicts = $portConflicts | Where-Object { $_.Required }
            if ($requiredConflicts.Count -gt 0) {
                Write-Host "Cannot skip required services. Please free up the following ports and try again:" -ForegroundColor Red
                foreach ($conflict in $requiredConflicts) {
                    Write-Host "  - Port $($conflict.Port) for $($conflict.Service)" -ForegroundColor Red
                }
                exit 1
            } else {
                Write-Host "Will skip non-essential services with port conflicts." -ForegroundColor Yellow
                # Set flag to skip specific services
                $skipAllRecipesApi = $true
            }
        }
        default {
            Write-Host "Exiting script." -ForegroundColor Red
            exit 1
        }
    }
}

# Create a directory for logs if it doesn't exist
if (-not (Test-Path -Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
    Write-Host "Created logs directory" -ForegroundColor Green
}

# Clear previous log files if they exist
if (Test-Path -Path "logs/allrecipes_api.log") { Clear-Content -Path "logs/allrecipes_api.log" }
if (Test-Path -Path "logs/allrecipes_api_error.log") { Clear-Content -Path "logs/allrecipes_api_error.log" }
if (Test-Path -Path "logs/main_api.log") { Clear-Content -Path "logs/main_api.log" }
if (Test-Path -Path "logs/main_api_error.log") { Clear-Content -Path "logs/main_api_error.log" }

# Install or update required packages
Install-RequiredPackages

Write-Host "Starting backend services..." -ForegroundColor Green

# Start the AllRecipes API if not skipped
$allrecipesStarted = $false
if (-not $skipAllRecipesApi) {
    $allrecipesStarted = Start-ServiceProcess -Name "AllRecipes API" -FilePath "python" -Arguments "backend/allrecipes_api.py" -LogFile "logs/allrecipes_api.log" -ErrorLogFile "logs/allrecipes_api_error.log" -HealthCheckUrl "http://localhost:8002/health"

    if (-not $allrecipesStarted) {
        Write-Host "WARNING: Continuing without AllRecipes API. Some features may not work." -ForegroundColor Yellow
    } else {
        Write-Host "AllRecipes API started successfully on port 8002" -ForegroundColor Green
    }
} else {
    Write-Host "Skipping AllRecipes API due to port conflict." -ForegroundColor Yellow
}

# Start the main backend API
$backendStarted = Start-ServiceProcess -Name "Main Backend API" -FilePath "python" -Arguments "backend/app.py" -LogFile "logs/main_api.log" -ErrorLogFile "logs/main_api_error.log" -HealthCheckUrl "http://localhost:5000/api/health"

if (-not $backendStarted) {
    Write-Host "ERROR: Failed to start Main Backend API. Check logs for details." -ForegroundColor Red
    
    # Display the last few lines of the error log
    if (Test-Path -Path "logs/main_api_error.log") {
        Write-Host "Last 10 lines of backend error log:" -ForegroundColor Red
        Get-Content -Path "logs/main_api_error.log" -Tail 10
    }
    
    $continueAnyway = Read-Host -Prompt "Do you want to continue anyway? (y/n)"
    if ($continueAnyway -ne "y") {
        Write-Host "Exiting script." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Main Backend API started successfully on port 5000" -ForegroundColor Green
}

Write-Host "`nBackend services started!" -ForegroundColor Green
Write-Host "Main Backend API: http://localhost:5000" -ForegroundColor Green
if ($allrecipesStarted) {
    Write-Host "AllRecipes API: http://localhost:8002" -ForegroundColor Green
}
Write-Host "Logs are being saved to the 'logs' directory" -ForegroundColor Green
Write-Host "`nTIP: If you encounter connection issues, check the log files for errors:" -ForegroundColor Yellow
Write-Host "  - logs/main_api_error.log" -ForegroundColor Yellow
if (-not $skipAllRecipesApi) {
    Write-Host "  - logs/allrecipes_api_error.log" -ForegroundColor Yellow
}

Write-Host "`nTo start the frontend separately, run 'cd frontend && npm start' in another terminal window" -ForegroundColor Cyan

# Keep the script running until the user presses Ctrl+C
try {
    Write-Host "`nPress Ctrl+C to stop all services..." -ForegroundColor Cyan
    while ($true) {
        Start-Sleep -Seconds 5
        
        # Check if services are still running and display status
        $mainApiRunning = Test-ApiAvailable -Url "http://localhost:5000/api/health" -MaxAttempts 1 -DelaySeconds 1
        
        if (-not $mainApiRunning) {
            Write-Host "WARNING: Main Backend API is not responding. Check logs/main_api_error.log" -ForegroundColor Red
        }
        
        if ($allrecipesStarted) {
            $allrecipesApiRunning = Test-ApiAvailable -Url "http://localhost:8002/health" -MaxAttempts 1 -DelaySeconds 1
            if (-not $allrecipesApiRunning) {
                Write-Host "WARNING: AllRecipes API is not responding. Check logs/allrecipes_api_error.log" -ForegroundColor Yellow
            }
        }
    }
}
finally {
    # This block will execute when the user presses Ctrl+C
    Write-Host "`nStopping all services..." -ForegroundColor Yellow
    
    # Find and stop all Python processes running our scripts
    $pythonProcesses = Get-Process -Name python -ErrorAction SilentlyContinue | 
                      Where-Object { $_.CommandLine -like "*backend/app.py*" -or $_.CommandLine -like "*backend/allrecipes_api.py*" }
    
    if ($pythonProcesses) {
        $pythonProcesses | ForEach-Object { 
            Write-Host "Stopping Python process with ID $($_.Id)..." -ForegroundColor Yellow
            Stop-Process -Id $_.Id -Force 
        }
    } else {
        Write-Host "No Python processes found to stop." -ForegroundColor Yellow
    }
    
    Write-Host "All services stopped." -ForegroundColor Green
}

# First, make sure python-dotenv is installed
pip install python-dotenv

# Navigate to the backend directory
cd backend

# Start the Flask application
python app.py 