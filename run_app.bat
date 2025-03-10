@echo off
echo Starting AI-Powered Recipe Recommender...

REM Start the backend server
start cmd /k "cd backend && python app.py"

REM Wait for the backend to start
timeout /t 5

REM Start the frontend server
start cmd /k "cd frontend && npm start"

REM Wait for the frontend to start
timeout /t 5

REM Open the application in the default browser
start http://localhost:3000

echo Application started successfully!
echo Backend server running on http://localhost:5000
echo Frontend server running on http://localhost:3000
echo Press Ctrl+C in the respective command windows to stop the servers. 