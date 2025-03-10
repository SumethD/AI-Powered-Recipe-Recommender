# AI-Powered Recipe Recommender

An intelligent recipe recommendation system that helps users find, modify, and create recipes based on their preferences and available ingredients.

## Features

- Search for recipes based on available ingredients
- Filter recipes by dietary restrictions, cuisine, and more
- Get AI-powered recipe modifications for healthier options, dietary restrictions, etc.
- Save favorite recipes
- Chat with AI for cooking advice and recipe suggestions
- User preferences and favorites management
- Comprehensive testing suite for both frontend and backend

## Project Structure

The project is divided into two main parts:

- **Backend**: Python-based API server using Flask
- **Frontend**: React application with TypeScript and Material-UI

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- Python (v3.8 or higher)
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Set up environment variables:
   - Create a `.env` file in the backend directory
   - Add the following variables:
     ```
     OPENAI_API_KEY=your_openai_api_key
     SPOONACULAR_API_KEY=your_spoonacular_api_key
     FLASK_ENV=development
     ```

6. Start the backend server:
   ```
   python app.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```
   or
   ```
   yarn install
   ```

3. Start the development server:
   ```
   npm start
   ```
   or
   ```
   yarn start
   ```

4. Open your browser and navigate to `http://localhost:3000`

## API Endpoints

### Recipe Endpoints

- `GET /api/recipes/ingredients` - Search recipes by ingredients
- `GET /api/recipes/search` - Search recipes by query with filters
- `GET /api/recipes/random` - Get random recipes
- `GET /api/recipes/:id` - Get recipe details
- `GET /api/recipes/cuisines` - Get supported cuisines
- `GET /api/recipes/diets` - Get supported diets
- `GET /api/recipes/intolerances` - Get supported intolerances

### User Endpoints

- `GET /api/users/:id` - Get user information
- `GET /api/users/:id/favorites` - Get user's favorite recipes
- `POST /api/users/:id/favorites` - Add a recipe to favorites
- `DELETE /api/users/:id/favorites/:recipeId` - Remove a recipe from favorites
- `PUT /api/users/:id/preferences` - Update user preferences
- `GET /api/users/:id/preferences` - Get user preferences

### Chat Endpoints

- `POST /api/chat/ask` - Send a message to the AI assistant
- `POST /api/chat/feedback` - Submit feedback on AI responses

## Testing

The project includes a comprehensive testing suite for both frontend and backend. See [TESTING.md](TESTING.md) for detailed instructions on running tests.

### Running Tests

You can run all tests using the provided script:

```
python run_tests.py --all
```

Or run specific test suites:

```
python run_tests.py --frontend  # Run frontend tests only
python run_tests.py --backend   # Run backend tests only
```

## Technologies Used

### Backend
- Flask
- OpenAI API
- Spoonacular API
- Python
- unittest for testing

### Frontend
- React
- TypeScript (with strict mode)
- Material-UI
- React Router
- Context API
- Jest and React Testing Library for testing

## Development

### TypeScript Configuration

The project uses TypeScript with strict mode enabled, which includes:

- `noImplicitAny`: Raise error on expressions and declarations with an implied 'any' type
- `strictNullChecks`: Enable strict null checks
- `strictFunctionTypes`: Enable strict checking of function types
- `noUnusedLocals`: Report errors on unused locals
- `noUnusedParameters`: Report errors on unused parameters

### Code Quality Tools

- ESLint for JavaScript/TypeScript linting
- Flake8 for Python linting

## Future Enhancements

- User authentication
- Recipe sharing
- Meal planning
- Grocery list generation
- Mobile app version
- Enhanced AI recipe generation
- Nutritional analysis and tracking

## License

This project is licensed under the MIT License - see the LICENSE file for details.