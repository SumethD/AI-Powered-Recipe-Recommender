# AI-Powered Recipe Recommender Backend

This is the backend for the AI-Powered Recipe Recommender application. It's built with Flask, OpenAI API, and Spoonacular API.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip

### Installation

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Create a `.env` file in the backend directory
   - Add the following variables:
     ```
     OPENAI_API_KEY=your_openai_api_key
     SPOONACULAR_API_KEY=your_spoonacular_api_key
     FLASK_ENV=development
     DEBUG=True
     PORT=5000
     ```

5. Run the application:
   ```
   python app.py
   ```

## Project Structure

- `app.py`: Main application file
- `models/`: Data models
- `services/`: Service layer
- `data/`: Data storage

## API Endpoints

### Recipe Endpoints

- `GET /api/recipes/ingredients`: Search recipes by ingredients
- `GET /api/recipes/search`: Search recipes by query with filters
- `GET /api/recipes/random`: Get random recipes
- `GET /api/recipes/:id`: Get recipe details

### User Endpoints

- `GET /api/users/:id`: Get user information
- `GET /api/users/:id/favorites`: Get user's favorite recipes
- `POST /api/users/:id/favorites`: Add a recipe to favorites
- `DELETE /api/users/:id/favorites/:recipeId`: Remove a recipe from favorites
- `PUT /api/users/:id/preferences`: Update user preferences

### Chat Endpoints

- `POST /api/chat/ask`: Send a message to the AI assistant
- `POST /api/chat/feedback`: Submit feedback on AI responses

## Features

- Recipe recommendations based on available ingredients using Spoonacular API
- Detailed recipe information including ingredients, instructions, and nutritional data
- AI-powered culinary advice using OpenAI API

## Setup

### Prerequisites

- Python 3.8 or higher
- Spoonacular API key (get one at [Spoonacular API](https://spoonacular.com/food-api))
- OpenAI API key (get one at [OpenAI](https://platform.openai.com/))

### Installation

1. Clone the repository
2. Navigate to the backend directory:
   ```
   cd backend
   ```
3. Create a virtual environment:
   ```
   python -m venv venv
   ```
4. Activate the virtual environment:
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```
5. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
6. Create a `.env` file based on `.env.example` and add your API keys:
   ```
   cp .env.example .env
   ```
   Then edit the `.env` file to add your API keys.

### Running the Application

To run the application in development mode:

```
flask run
```

Or:

```
python app.py
```

The API will be available at `http://localhost:5000`.

### Verifying Setup

To verify that your application is properly set up, you can run the verification script:

```
python verify_setup.py
```

This script checks:
- Required environment variables
- Python dependencies
- Directory structure
- Flask application import

### Logging

The application uses a comprehensive logging system that logs to both the console and a rotating file in the `logs` directory. You can configure the log level in your `.env` file:

```
LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

Logs are stored in `logs/app.log` and are rotated when they reach 10KB in size, with a maximum of 10 backup files.

### Error Handling

The application includes a robust error handling system that:
- Returns appropriate HTTP status codes
- Provides meaningful error messages
- Logs errors with context information
- Handles specific API errors from Spoonacular and OpenAI

## API Documentation

### Recipe Endpoints

#### Find Recipes by Ingredients

**Endpoint:** `POST /api/recipes/by-ingredients`

**Description:** Find recipes based on available ingredients.

**Request Body:**
```json
{
  "ingredients": ["apple", "flour", "sugar"],  // Required: List of ingredients
  "limit": 10,                                 // Optional: Number of recipes to return (default: 10)
  "ranking": 1,                                // Optional: Ranking strategy (1=maximize used ingredients, 2=minimize missing ingredients)
  "ignore_pantry": false                       // Optional: Whether to ignore pantry items (default: false)
}
```

**Response:**
```json
{
  "success": true,
  "count": 2,
  "recipes": [
    {
      "id": 12345,
      "title": "Apple Pie",
      "image": "https://spoonacular.com/recipeImages/12345-312x231.jpg",
      "used_ingredients": [
        {
          "id": 9003,
          "name": "apple",
          "amount": 2,
          "unit": "",
          "original": "2 apples"
          // Additional ingredient details...
        },
        // More used ingredients...
      ],
      "missed_ingredients": [
        {
          "id": 2010,
          "name": "cinnamon",
          "amount": 1,
          "unit": "tsp",
          "original": "1 teaspoon of cinnamon"
          // Additional ingredient details...
        },
        // More missed ingredients...
      ],
      "used_ingredient_count": 2,
      "missed_ingredient_count": 3,
      "used_ingredient_names": ["apple", "flour"],
      "missed_ingredient_names": ["cinnamon", "butter", "egg"],
      "likes": 150
    },
    // More recipes...
  ]
}
```

#### Get Recipe Details

**Endpoint:** `GET /api/recipes/<recipe_id>`

**Description:** Get detailed information about a specific recipe.

**Response:**
```json
{
  "success": true,
  "recipe": {
    "id": 12345,
    "title": "Apple Pie",
    "image": "https://spoonacular.com/recipeImages/12345-312x231.jpg",
    "summary": "This apple pie is...",
    "instructions": "1. Preheat oven to 350°F...",
    "readyInMinutes": 60,
    "servings": 8,
    "sourceUrl": "https://example.com/apple-pie",
    "nutrition": {
      // Nutrition details...
    },
    "extendedIngredients": [
      // Detailed ingredients list...
    ]
    // Additional recipe details...
  }
}
```

### Chat Endpoints

- `POST /api/chat/ask` - Get culinary advice using AI

## Project Structure

```
backend/
├── app.py                  # Main application file
├── config/                 # Configuration files
│   └── config.py           # Environment configuration
├── models/                 # Data models
│   └── recipe.py           # Recipe model
├── routes/                 # API routes
│   ├── chat_routes.py      # Chat API routes
│   └── recipe_routes.py    # Recipe API routes
├── services/               # External API services
│   ├── openai_service.py   # OpenAI API integration
│   └── spoonacular_service.py # Spoonacular API integration
└── utils/                  # Utility functions
    └── error_handlers.py   # Error handling utilities
``` 