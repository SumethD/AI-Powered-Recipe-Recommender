#!/bin/bash

# Bash script to run all services for the AI-Powered Recipe Recommender

echo -e "\033[0;32mStarting AI-Powered Recipe Recommender...\033[0m"
echo -e "\033[0;33mPress Ctrl+C to stop all services\033[0m"

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Check if ports are available
PORTS_TO_CHECK=(5000 8002 3000)
PORT_CONFLICTS=()

for port in "${PORTS_TO_CHECK[@]}"; do
    if check_port $port; then
        PORT_CONFLICTS+=($port)
    fi
done

if [ ${#PORT_CONFLICTS[@]} -gt 0 ]; then
    echo -e "\033[0;31mError: The following ports are already in use: ${PORT_CONFLICTS[*]}\033[0m"
    echo -e "\033[0;31mPlease close the applications using these ports and try again.\033[0m"
    exit 1
fi

# Create a directory for logs if it doesn't exist
mkdir -p logs

# Start the AllRecipes API
echo -e "\033[0;36mStarting AllRecipes API on port 8002...\033[0m"
python backend/allrecipes_api.py > logs/allrecipes_api.log 2> logs/allrecipes_api_error.log &
ALLRECIPES_API_PID=$!

# Wait for the AllRecipes API to start
echo -e "\033[0;36mWaiting for AllRecipes API to start...\033[0m"
sleep 3

# Start the main backend API
echo -e "\033[0;36mStarting Main Backend API on port 5000...\033[0m"
python backend/app.py > logs/main_api.log 2> logs/main_api_error.log &
MAIN_API_PID=$!

# Wait for the main backend API to start
echo -e "\033[0;36mWaiting for Main Backend API to start...\033[0m"
sleep 3

# Start the frontend
echo -e "\033[0;36mStarting Frontend on port 3000...\033[0m"
cd frontend
npm start > ../logs/frontend.log 2> ../logs/frontend_error.log &
FRONTEND_PID=$!
cd ..

echo -e "\033[0;32mAll services started successfully!\033[0m"
echo -e "\033[0;32mFrontend: http://localhost:3000\033[0m"
echo -e "\033[0;32mMain Backend API: http://localhost:5000\033[0m"
echo -e "\033[0;32mAllRecipes API: http://localhost:8002\033[0m"
echo -e "\033[0;32mLogs are being saved to the 'logs' directory\033[0m"

# Function to clean up processes on exit
cleanup() {
    echo -e "\n\033[0;33mStopping all services...\033[0m"
    
    # Kill the processes
    if ps -p $ALLRECIPES_API_PID > /dev/null; then
        echo -e "\033[0;33mStopping AllRecipes API (PID: $ALLRECIPES_API_PID)...\033[0m"
        kill $ALLRECIPES_API_PID
    fi
    
    if ps -p $MAIN_API_PID > /dev/null; then
        echo -e "\033[0;33mStopping Main Backend API (PID: $MAIN_API_PID)...\033[0m"
        kill $MAIN_API_PID
    fi
    
    if ps -p $FRONTEND_PID > /dev/null; then
        echo -e "\033[0;33mStopping Frontend (PID: $FRONTEND_PID)...\033[0m"
        kill $FRONTEND_PID
    fi
    
    echo -e "\033[0;32mAll services stopped.\033[0m"
    exit 0
}

# Set up trap to call cleanup function on Ctrl+C
trap cleanup SIGINT SIGTERM

# Keep the script running until the user presses Ctrl+C
while true; do
    sleep 1
done 