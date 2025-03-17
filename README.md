# AI-Powered Recipe Recommender

An application that extracts recipe instructions from URLs and enhances them using AI when needed.

## Features

- Extract recipe instructions from various recipe websites
- Specialized handling for AllRecipes.com URLs
- AI-powered recipe instruction generation when scraping fails
- Robust error handling and fallback mechanisms
- Multiple API endpoints for different use cases
- Generate comprehensive shopping lists from multiple recipes
- **NEW: AI-powered ingredient consolidation** - Intelligently combines similar ingredients and converts between units

## Architecture

The application consists of several components:

1. **Frontend** - React application that allows users to input recipe URLs and view instructions
2. **Main Backend API** - Handles general recipe instruction extraction and AI generation
3. **AllRecipes API** - Specialized API for extracting instructions from AllRecipes.com URLs
4. **Recipe Instructions Service** - Core service that handles scraping and AI generation logic

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- npm 6 or higher

### Backend Setup

1. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up OpenAI API key:
   ```
   # Create a .env file in the backend directory
   echo "OPENAI_API_KEY=your_api_key_here" > backend/.env
   ```
   This API key is used for both recipe instruction generation and ingredient consolidation.

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

## Running the Application

### Using the Combined Script

For convenience, you can use the provided script to start all services:

```
# On Windows
.\run_app.ps1

# On Linux/Mac
./run_app.sh
```

### Start the Backend Services Manually

1. Start the AllRecipes API:
   ```
   python backend/allrecipes_api.py
   ```
   This will start the API on port 8002.

2. Start the Main Backend API:
   ```
   python backend/app.py
   ```
   This will start the API on port 5000.

### Start the Frontend

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Start the development server:
   ```
   npm start
   ```
   This will start the frontend on port 3000.

## API Endpoints

### AllRecipes API

- **POST /api/allrecipes**
  - Request body: `{ "url": "https://www.allrecipes.com/recipe/..." }`
  - Response: `{ "instructions": "Step 1: ... Step 2: ..." }`

### Main Backend API

- **POST /api/recipe-instructions**
  - Request body: `{ "url": "https://example.com/recipe/...", "recipe_id": "optional-id" }`
  - Response: `{ "instructions": "Step 1: ... Step 2: ...", "recipe_id": "id", "source": "scraped|ai|basic", "cached": true|false }`

- **GET /health**
  - Response: `{ "status": "ok" }`

### Shopping List API

- **POST /api/shopping-list/generate**
  - Request body: `{ "recipes": [{"id": "recipe-id", "extendedIngredients": [...]}] }`
  - Response: `{ "shopping_list": [{...ingredients with amounts and categories}] }`

- **POST /api/shopping-list/consolidate**
  - Request body: `{ "ingredients": [...], "prompt": "..." }`
  - Response: `{ "consolidatedItems": [...], "explanation": [...] }`

## Testing

Run the integration tests to verify that all components are working correctly:

```
python backend/test_integration.py
```

## Using AI-Powered Ingredient Consolidation

The application now features an AI-powered ingredient consolidation system that:
- Identifies similar ingredients (e.g., "chicken broth" and "chicken stock")
- Converts between different units (e.g., ml to cups)
- Standardizes ingredient names
- Provides a cleaner, more accurate shopping list

To use this feature:
1. Add recipes to your shopping list
2. Generate the shopping list
3. Click the "AI Consolidate" button
4. The system will use OpenAI to analyze and consolidate similar ingredients
5. Switch between the original and AI-consolidated views using the toggle button

## Troubleshooting

- If you encounter port conflicts, ensure no other services are running on ports 3000, 5000, or 8002.
- If the OpenAI API is not working, check that your API key is set correctly and that you have access to the required models.
- If scraping fails for a specific URL, try using the AllRecipes API for AllRecipes URLs or the Main API for other URLs.

## License

MIT