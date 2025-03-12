# Quick Start Guide

This guide will help you get the AI-Powered Recipe Recommender up and running quickly.

## Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/AI-Powered-Recipe-Recommender.git
cd AI-Powered-Recipe-Recommender
```

## Step 2: Install Dependencies

### Backend Dependencies

```bash
pip install -r requirements.txt
```

### Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

## Step 3: Set Up OpenAI API Key (Optional)

If you want to use the AI-powered recipe instruction generation feature, you'll need to set up an OpenAI API key:

```bash
# For Windows PowerShell
$env:OPENAI_API_KEY="your_api_key_here"

# For Windows Command Prompt
set OPENAI_API_KEY=your_api_key_here

# For macOS/Linux
export OPENAI_API_KEY=your_api_key_here
```

## Step 4: Start the Services

### Start the AllRecipes API

Open a new terminal window and run:

```bash
python backend/allrecipes_api.py
```

This will start the AllRecipes API on port 8002.

### Start the Main Backend API

Open another terminal window and run:

```bash
python backend/app.py
```

This will start the main backend API on port 5000.

### Start the Frontend

Open a third terminal window and run:

```bash
cd frontend
npm start
```

This will start the frontend on port 3000 and open it in your default browser.

## Step 5: Use the Application

1. Open your browser and navigate to `http://localhost:3000` if it doesn't open automatically.
2. Enter a recipe URL in the input field.
3. Click "Get Instructions" to fetch the recipe instructions.
4. The application will:
   - Try to scrape the instructions from the provided URL
   - Use the specialized AllRecipes API if it's an AllRecipes URL
   - Generate instructions using AI if scraping fails
   - Provide basic instructions as a last resort

## Troubleshooting

### Port Conflicts

If you see an error about ports being in use, you can change the ports:

- For the AllRecipes API: Edit `backend/allrecipes_api.py` and change the port number in the `uvicorn.run` line
- For the main backend API: Edit `backend/app.py` and change the port number in the `app.run` line
- For the frontend: Edit `frontend/package.json` and add a `PORT=xxxx` before `react-scripts start` in the `start` script

### API Key Issues

If you're having issues with the OpenAI API:

1. Verify that your API key is correct
2. Check that you have access to the required models
3. The application will still work without an API key, but will fall back to basic instructions when scraping fails

### Scraping Issues

If scraping fails for a specific URL:

1. Try using a different URL from the same website
2. Check if the website has changed its structure
3. The application will fall back to AI-generated or basic instructions 