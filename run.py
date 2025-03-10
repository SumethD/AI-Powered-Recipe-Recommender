import os
import subprocess
import sys
import time
import webbrowser
from threading import Thread

def check_backend():
    """Check if the backend can run."""
    print("Checking if the backend can run...")
    os.chdir("backend")
    
    # Check if the check_backend.py script exists
    if os.path.isfile("check_backend.py"):
        # Run the check_backend.py script
        if sys.platform == "win32":
            result = subprocess.run(["python", "check_backend.py"], capture_output=True, text=True)
        else:
            result = subprocess.run(["python3", "check_backend.py"], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(result.stdout)
            print(result.stderr)
            return False
    else:
        # Check if the required files exist
        required_files = ["app.py", ".env"]
        for file in required_files:
            if not os.path.isfile(file):
                print(f"Error: {file} not found")
                return False
    
    os.chdir("..")
    return True

def check_frontend():
    """Check if the frontend can run."""
    print("Checking if the frontend can run...")
    os.chdir("frontend")
    
    # Check if the check_frontend.js script exists
    if os.path.isfile("check_frontend.js"):
        # Run the check_frontend.js script
        result = subprocess.run(["node", "check_frontend.js"], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(result.stdout)
            print(result.stderr)
            return False
    else:
        # Check if the required files exist
        required_files = ["package.json", "src/index.tsx", "src/App.tsx"]
        for file in required_files:
            if not os.path.isfile(file):
                print(f"Error: {file} not found")
                return False
    
    os.chdir("..")
    return True

def run_backend():
    """Run the Flask backend server."""
    os.chdir("backend")
    try:
        if sys.platform == "win32":
            subprocess.run(["python", "app.py"], check=True)
        else:
            subprocess.run(["python3", "app.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running backend: {e}")
    except KeyboardInterrupt:
        print("Backend stopped by user")

def run_frontend():
    """Run the React frontend development server."""
    os.chdir("frontend")
    try:
        if sys.platform == "win32":
            subprocess.run(["npm", "start"], check=True)
        else:
            subprocess.run(["npm", "start"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running frontend: {e}")
    except KeyboardInterrupt:
        print("Frontend stopped by user")

def open_browser():
    """Open the browser after a delay."""
    time.sleep(5)  # Wait for servers to start
    try:
        webbrowser.open("http://localhost:3000")
    except Exception as e:
        print(f"Error opening browser: {e}")

if __name__ == "__main__":
    print("Starting AI-Powered Recipe Recommender...")
    
    # Check if the backend and frontend can run
    if not check_backend():
        print("Error: Backend check failed")
        sys.exit(1)
    
    if not check_frontend():
        print("Error: Frontend check failed")
        sys.exit(1)
    
    # Start the backend in a separate thread
    backend_thread = Thread(target=run_backend)
    backend_thread.daemon = True
    backend_thread.start()
    
    # Wait a moment for the backend to start
    time.sleep(2)
    
    # Open the browser in a separate thread
    browser_thread = Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start the frontend (this will block until the frontend is closed)
    try:
        run_frontend()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"\nError: {str(e)}")
    
    print("Application stopped.") 