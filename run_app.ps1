# PowerShell script to run the AI-Powered Recipe Recommender application
# This script starts both the backend and frontend servers

Write-Host "Starting AI-Powered Recipe Recommender..." -ForegroundColor Green

# Function to check if a port is in use
function Test-PortInUse {
    param (
        [int]$Port
    )
    
    $connections = Get-NetTCPConnection -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -eq $Port }
    return ($null -ne $connections)
}

# Check if ports are already in use
$backendPort = 5000
$frontendPort = 3000

if (Test-PortInUse -Port $backendPort) {
    Write-Host "Warning: Port $backendPort is already in use. The backend server may not start properly." -ForegroundColor Yellow
}

if (Test-PortInUse -Port $frontendPort) {
    Write-Host "Warning: Port $frontendPort is already in use. The frontend server may not start properly." -ForegroundColor Yellow
}

# Start the backend server
Write-Host "Starting backend server..." -ForegroundColor Cyan
$backendJob = Start-Process -FilePath "python" -ArgumentList "app.py" -WorkingDirectory ".\backend" -PassThru -WindowStyle Normal

# Wait a moment for the backend to initialize
Start-Sleep -Seconds 3

# Check if backend started successfully
if ($null -eq $backendJob -or $backendJob.HasExited) {
    Write-Host "Error: Failed to start backend server. Please check the logs for details." -ForegroundColor Red
    exit 1
}

Write-Host "Backend server started successfully on http://localhost:$backendPort" -ForegroundColor Green

# Start the frontend server
Write-Host "Starting frontend server..." -ForegroundColor Cyan
$frontendJob = Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WorkingDirectory ".\frontend" -PassThru -WindowStyle Normal

# Wait a moment for the frontend to initialize
Start-Sleep -Seconds 5

# Check if frontend started successfully
if ($null -eq $frontendJob -or $frontendJob.HasExited) {
    Write-Host "Error: Failed to start frontend server. Please check the logs for details." -ForegroundColor Red
    
    # Kill the backend process if it's still running
    if (-not $backendJob.HasExited) {
        $backendJob.Kill()
    }
    
    exit 1
}

Write-Host "Frontend server started successfully on http://localhost:$frontendPort" -ForegroundColor Green
Write-Host "AI-Powered Recipe Recommender is now running!" -ForegroundColor Green
Write-Host "Open your browser and navigate to http://localhost:$frontendPort to use the application." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop both servers." -ForegroundColor Yellow

try {
    # Keep the script running until user presses Ctrl+C
    while ($true) {
        Start-Sleep -Seconds 1
        
        # Check if either process has exited
        if ($backendJob.HasExited) {
            Write-Host "Backend server has stopped unexpectedly." -ForegroundColor Red
            break
        }
        
        if ($frontendJob.HasExited) {
            Write-Host "Frontend server has stopped unexpectedly." -ForegroundColor Red
            break
        }
    }
}
finally {
    # Clean up processes when the script is terminated
    Write-Host "Stopping servers..." -ForegroundColor Cyan
    
    if (-not $backendJob.HasExited) {
        $backendJob.Kill()
    }
    
    if (-not $frontendJob.HasExited) {
        $frontendJob.Kill()
    }
    
    Write-Host "Servers stopped." -ForegroundColor Green
} 