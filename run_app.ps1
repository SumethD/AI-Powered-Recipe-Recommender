# PowerShell script to run all services for the AI-Powered Recipe Recommender

Write-Host "Starting AI-Powered Recipe Recommender..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow

# Function to check if a port is in use
function Test-PortInUse {
    param (
        [int]$Port
    )
    
    $connections = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -eq $Port }
    return $null -ne $connections
}

# Check if ports are available
$portsToCheck = @(5000, 8002, 3000)
$portConflicts = @()

foreach ($port in $portsToCheck) {
    if (Test-PortInUse -Port $port) {
        $portConflicts += $port
    }
}

if ($portConflicts.Count -gt 0) {
    Write-Host "Error: The following ports are already in use: $($portConflicts -join ', ')" -ForegroundColor Red
    Write-Host "Please close the applications using these ports and try again." -ForegroundColor Red
    exit 1
}

# Create a directory for logs if it doesn't exist
if (-not (Test-Path -Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}

# Start the AllRecipes API
Write-Host "Starting AllRecipes API on port 8002..." -ForegroundColor Cyan
Start-Process -FilePath "python" -ArgumentList "backend/allrecipes_api.py" -RedirectStandardOutput "logs/allrecipes_api.log" -RedirectStandardError "logs/allrecipes_api_error.log" -NoNewWindow

# Wait for the AllRecipes API to start
Write-Host "Waiting for AllRecipes API to start..." -ForegroundColor Cyan
Start-Sleep -Seconds 3

# Start the main backend API
Write-Host "Starting Main Backend API on port 5000..." -ForegroundColor Cyan
Start-Process -FilePath "python" -ArgumentList "backend/app.py" -RedirectStandardOutput "logs/main_api.log" -RedirectStandardError "logs/main_api_error.log" -NoNewWindow

# Wait for the main backend API to start
Write-Host "Waiting for Main Backend API to start..." -ForegroundColor Cyan
Start-Sleep -Seconds 3

# Start the frontend
Write-Host "Starting Frontend on port 3000..." -ForegroundColor Cyan
Set-Location -Path "frontend"
Start-Process -FilePath "npm" -ArgumentList "start" -RedirectStandardOutput "..\logs\frontend.log" -RedirectStandardError "..\logs\frontend_error.log" -NoNewWindow
Set-Location -Path ".."

Write-Host "All services started successfully!" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Green
Write-Host "Main Backend API: http://localhost:5000" -ForegroundColor Green
Write-Host "AllRecipes API: http://localhost:8002" -ForegroundColor Green
Write-Host "Logs are being saved to the 'logs' directory" -ForegroundColor Green

# Keep the script running until the user presses Ctrl+C
try {
    while ($true) {
        Start-Sleep -Seconds 1
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
            Write-Host "Stopping process with ID $($_.Id)..." -ForegroundColor Yellow
            Stop-Process -Id $_.Id -Force 
        }
    }
    
    # Find and stop the npm process for the frontend
    $npmProcesses = Get-Process -Name node -ErrorAction SilentlyContinue | 
                   Where-Object { $_.CommandLine -like "*react-scripts start*" }
    
    if ($npmProcesses) {
        $npmProcesses | ForEach-Object { 
            Write-Host "Stopping process with ID $($_.Id)..." -ForegroundColor Yellow
            Stop-Process -Id $_.Id -Force 
        }
    }
    
    Write-Host "All services stopped." -ForegroundColor Green
} 