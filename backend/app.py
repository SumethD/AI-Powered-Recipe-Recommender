import os
import logging
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from services.recipe_service import get_recipes_by_ingredients, get_recipe_details, search_recipes, get_random_recipes
from services.user_service import get_user, get_user_favorites, add_favorite, remove_favorite, update_user_preferences, get_user_preferences
from routes.chat_routes import chat_bp
from routes.recipe_routes import recipe_bp
from routes.video_routes import video_bp
from routes.shopping_list_routes import shopping_list_bp
from fastapi import Request
from fastapi.responses import JSONResponse
from recipe_instructions_service import get_recipe_instructions
import traceback
import datetime

# Add the current directory to the path to fix imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Force API_PROVIDER to be 'edamam'
os.environ['API_PROVIDER'] = 'edamam'

# Print environment variables for debugging
print(f"API_PROVIDER: {os.getenv('API_PROVIDER', 'edamam')}")
print(f"EDAMAM_API_KEY: {os.getenv('EDAMAM_API_KEY', 'not set')}")
print(f"EDAMAM_APP_ID: {os.getenv('EDAMAM_APP_ID', 'not set')}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("recipe_app")

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(recipe_bp, url_prefix='/api/recipes')
app.register_blueprint(chat_bp, url_prefix='/api/chat')
app.register_blueprint(video_bp, url_prefix='/api/videos')
app.register_blueprint(shopping_list_bp, url_prefix='/api/shopping-list')

# Add a test endpoint to check if the edamam_service is being imported correctly
@app.route('/api/test-edamam', methods=['GET'])
def test_edamam():
    """Test endpoint to verify Edamam API connectivity"""
    try:
        # Import the Edamam service
        from services.edamam_service import search
        
        # Try to search for a simple query
        results = search("pasta", 1)
        
        # Return success with the results
        return jsonify({
            "success": True,
            "message": "Edamam API is working correctly",
            "results": results
        })
    except Exception as e:
        # Log the error
        app.logger.error(f"Error testing Edamam API: {str(e)}")
        
        # Return error response
        return jsonify({
            "success": False,
            "message": f"Error testing Edamam API: {str(e)}"
        }), 500

# Add a test endpoint to check if the recipe_service is being used correctly
@app.route('/api/test-recipe-service', methods=['GET'])
def test_recipe_service():
    try:
        import services.recipe_service as recipe_service
        return jsonify({
            "success": True,
            "message": "Recipe service imported successfully",
            "api_provider": recipe_service.API_PROVIDER
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error importing recipe_service: {str(e)}"
        })

# Add a direct test endpoint for random recipes
@app.route('/api/test-random-recipes', methods=['GET'])
def test_random_recipes():
    try:
        import services.recipe_service as recipe_service
        result = recipe_service.get_random_recipes(number=2)
        return jsonify({
            "success": True,
            "message": "Random recipes retrieved successfully",
            "api_provider": recipe_service.API_PROVIDER,
            "recipes": result
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error getting random recipes: {str(e)}"
        })

# Add a direct test endpoint for the edamam_service
@app.route('/api/test-edamam-direct', methods=['GET'])
def test_edamam_direct():
    try:
        import services.edamam_service as edamam_service
        result = edamam_service.get_random_recipes(number=2)
        
        # Print the result for debugging
        print(f"Result type: {type(result)}")
        print(f"Result length: {len(result)}")
        if result:
            print(f"First recipe: {result[0].get('title', 'No title')}")
        
        return jsonify({
            "success": True,
            "message": "Edamam random recipes retrieved successfully",
            "recipes": result,
            "recipe_count": len(result),
            "recipe_titles": [r.get('title', 'No title') for r in result]
        })
    except Exception as e:
        print(f"Error in test_edamam_direct: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error getting Edamam random recipes: {str(e)}"
        })

# Recipe endpoints
@app.route('/api/recipes/ingredients', methods=['GET', 'POST'])
def recipes_by_ingredients():
    # Handle both GET and POST requests
    if request.method == 'POST':
        data = request.get_json()
        if not data or 'ingredients' not in data:
            return jsonify({"error": "No ingredients provided"}), 400
        
        ingredients = data['ingredients']
        
        # Validate ingredients
        if not ingredients or not isinstance(ingredients, list):
            return jsonify({"error": "Ingredients must be a non-empty list"}), 400
        
        # Clean ingredients
        ingredients_list = [ingredient.strip().lower() for ingredient in ingredients if isinstance(ingredient, str) and ingredient.strip()]
    else:  # GET request
        ingredients = request.args.get('ingredients', '')
        if not ingredients:
            return jsonify({"error": "No ingredients provided"}), 400
        
        # Split comma-separated ingredients
        ingredients_list = [i.strip().lower() for i in ingredients.split(',') if i.strip()]
    
    # Validate final ingredients list
    if not ingredients_list:
        return jsonify({"error": "No valid ingredients provided"}), 400
    
    # Get optional parameters
    try:
        limit = int(request.args.get('limit', 10))
        if limit < 1 or limit > 100:
            limit = 10
    except (ValueError, TypeError):
        limit = 10
    
    try:
        ranking = int(request.args.get('ranking', 1))
        if ranking not in [1, 2]:
            ranking = 1
    except (ValueError, TypeError):
        ranking = 1
    
    # Log the request
    app.logger.info(f"Searching for recipes with ingredients: {', '.join(ingredients_list)}")
    app.logger.info(f"Parameters: limit={limit}, ranking={ranking}")
    
    try:
        # Get recipes from Edamam
        recipes = get_recipes_by_ingredients(ingredients_list, limit, ranking)
        return jsonify(recipes)
    except Exception as e:
        app.logger.error(f"Error in recipes_by_ingredients: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/recipes/search', methods=['GET'])
def search_recipes_route():
    query = request.args.get('query', '')
    if not query:
        return jsonify({"error": "No search query provided"}), 400
    
    # Get optional parameters
    cuisine = request.args.get('cuisine', '')
    diet = request.args.get('diet', '')
    intolerances = request.args.get('intolerances', '')
    
    try:
        limit = int(request.args.get('limit', 10))
        if limit < 1 or limit > 100:
            limit = 10
    except (ValueError, TypeError):
        limit = 10
    
    # Log the request
    app.logger.info(f"Searching for recipes with query: {query}")
    app.logger.info(f"Parameters: cuisine={cuisine}, diet={diet}, intolerances={intolerances}, limit={limit}")
    
    try:
        # Get recipes from Edamam
        recipes = search_recipes(query, cuisine, diet, intolerances, limit)
        return jsonify(recipes)
    except Exception as e:
        app.logger.error(f"Error in search_recipes_route: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/recipes/random', methods=['GET'])
def random_recipes():
    tags = request.args.get('tags', '')
    
    try:
        recipes = get_random_recipes(tags)
        return jsonify(recipes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/recipes/<path:recipe_id>', methods=['GET'])
def recipe_details(recipe_id):
    try:
        recipe = get_recipe_details(recipe_id)
        return jsonify(recipe)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# User endpoints
@app.route('/api/users/<user_id>', methods=['GET'])
def get_user_route(user_id):
    try:
        user = get_user(user_id)
        return jsonify(user.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/<user_id>/favorites', methods=['GET'])
def get_favorites_route(user_id):
    limit = request.args.get('limit', type=int)
    sort_by = request.args.get('sort_by', 'added_at')
    reverse = request.args.get('reverse', 'true').lower() == 'true'
    
    try:
        favorites = get_user_favorites(user_id, limit, sort_by, reverse)
        return jsonify(favorites)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/<user_id>/favorites', methods=['POST'])
def add_favorite_route(user_id):
    recipe = request.json
    if not recipe:
        return jsonify({"error": "No recipe provided"}), 400
    
    try:
        add_favorite(user_id, recipe)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/<user_id>/favorites/<path:recipe_id>', methods=['DELETE'])
def remove_favorite_route(user_id, recipe_id):
    try:
        remove_favorite(user_id, recipe_id)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/<user_id>/preferences', methods=['PUT'])
def update_preferences_route(user_id):
    preferences = request.json
    if not preferences:
        return jsonify({"error": "No preferences provided"}), 400
    
    try:
        update_user_preferences(user_id, preferences)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Start Recipe Instructions Service automatically
def start_recipe_instructions_service():
    import subprocess
    import threading
    import sys
    
    def run_service():
        try:
            print("Starting Recipe Instructions Service...")
            # Using uvicorn to run the FastAPI app
            cmd = [sys.executable, "-m", "uvicorn", "recipe_instructions_service:app", "--host", "0.0.0.0", "--port", "8003"]
            subprocess.Popen(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
            print("Recipe Instructions Service started successfully on http://localhost:8003")
        except Exception as e:
            print(f"Error starting Recipe Instructions Service: {str(e)}")
    
    # Start in a separate thread so it doesn't block the Flask app
    try:
        service_thread = threading.Thread(target=run_service)
        service_thread.daemon = True  # This ensures the thread will be killed when the main process exits
        service_thread.start()
    except Exception as e:
        print(f"Warning: Could not start Recipe Instructions Service: {str(e)}")
        print("The main API will continue to run but recipe instructions may not be available.")

# Start AllRecipes API automatically
def start_allrecipes_api():
    import subprocess
    import threading
    import sys
    
    def run_service():
        try:
            print("Starting AllRecipes API...")
            # Using uvicorn to run the FastAPI app
            cmd = [sys.executable, "-m", "uvicorn", "allrecipes_api:app", "--host", "0.0.0.0", "--port", "8002"]
            subprocess.Popen(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
            print("AllRecipes API started successfully on http://localhost:8002")
        except Exception as e:
            print(f"Error starting AllRecipes API: {str(e)}")
    
    # Start in a separate thread so it doesn't block the Flask app
    try:
        service_thread = threading.Thread(target=run_service)
        service_thread.daemon = True  # This ensures the thread will be killed when the main process exits
        service_thread.start()
    except Exception as e:
        print(f"Warning: Could not start AllRecipes API: {str(e)}")
        print("The main API will continue to run but AllRecipes parsing may not be available.")

# Exception handlers
@app.errorhandler(Exception)
def global_exception_handler(exc):
    """Global exception handler for unhandled exceptions"""
    error_traceback = traceback.format_exc()
    
    # Log detailed error information
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(f"Exception type: {type(exc).__name__}")
    logger.error(f"Traceback: {error_traceback}")
    
    # Return a more detailed error response in development
    if os.environ.get("ENVIRONMENT") != "production":
        return jsonify({
            "detail": str(exc),
            "type": type(exc).__name__,
            "traceback": error_traceback.split("\n")
        }), 500
    else:
        # In production, return a generic error message
        return jsonify({"detail": "Internal server error"}), 500

# Add a health endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify the API is running."""
    try:
        # Check if required services are initialized
        # This could check database connections or other dependencies
        return jsonify({
            "status": "healthy", 
            "service": "recipe-api", 
            "timestamp": datetime.datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "service": "recipe-api",
            "error": str(e),
            "timestamp": datetime.datetime.now().isoformat()
        }), 500

@app.route('/api/recipe-instructions', methods=['GET'])
def recipe_instructions():
    url = request.args.get('url')
    recipe_id = request.args.get('recipe_id')
    
    if not url:
        return jsonify({"error": "URL parameter is required"}), 400
    
    try:
        instructions_data = get_recipe_instructions(url, recipe_id)
        return jsonify(instructions_data)
    except Exception as e:
        logger.error(f"Error getting recipe instructions: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": "Failed to get recipe instructions",
            "message": str(e),
            "instructions": "We couldn't retrieve the instructions for this recipe. Try visiting the original recipe website."
        }), 500

if __name__ == '__main__':
    # Start recipe instructions service before starting the Flask app
    try:
        start_recipe_instructions_service()
        start_allrecipes_api()
        
        # Give the services a moment to start up
        import time
        time.sleep(2)
    except Exception as e:
        print(f"Warning: Error starting backend services: {str(e)}")
        print("The main API will continue to run but some features may not be available.")
    
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 