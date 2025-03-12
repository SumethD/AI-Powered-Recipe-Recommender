from flask import Blueprint, request, jsonify, current_app
from services.recipe_service import (
    get_recipes_by_ingredients, get_recipe_details, 
    search_recipes, get_random_recipes,
    get_cuisines, get_diets, get_intolerances
)
from services.user_service import (
    get_user_favorites, add_favorite, remove_favorite, 
    is_favorite, update_user_preferences, get_user_preferences
)
from models.recipe import Recipe
import asyncio
from recipe_instructions_api import get_recipe_instructions, RecipeInstructionsRequest

recipe_bp = Blueprint('recipes', __name__)

@recipe_bp.route('/ingredients', methods=['GET', 'POST'])
def find_recipes_by_ingredients_endpoint():
    """
    Find recipes based on available ingredients
    
    Expects a JSON with:
    - 'ingredients': list of ingredient names (required)
    - 'limit': number of recipes to return (optional, default: 10)
    - 'ranking': ranking strategy (optional, default: 1)
      1 = maximize used ingredients, 2 = minimize missing ingredients
    - 'ignore_pantry': whether to ignore pantry items (optional, default: false)
    - 'apiProvider': API provider to use (optional, default: from environment)
    
    Returns:
    - List of recipes matching the ingredients
    - Each recipe includes: id, title, image, used ingredients, missed ingredients, likes
    """
    current_app.logger.info("Recipe search by ingredients endpoint accessed")
    
    # Get and validate request data
    if request.method == 'POST':
        data = request.get_json()
        
        if not data or 'ingredients' not in data:
            current_app.logger.warning("No ingredients provided in request")
            return jsonify({"error": "No ingredients provided"}), 400
        
        ingredients = data['ingredients']
        limit = data.get('limit', 10)
        ranking = data.get('ranking', 1)
        ignore_pantry = data.get('ignore_pantry', False)
        
        # Check for apiProvider in camelCase (frontend convention) or api_provider in snake_case (backend convention)
        api_provider = data.get('apiProvider', data.get('api_provider', None))
        current_app.logger.info(f"API Provider from request: {api_provider}")
    else:  # GET method
        ingredients_str = request.args.get('ingredients', '')
        if not ingredients_str:
            current_app.logger.warning("No ingredients provided in request")
            return jsonify({"error": "No ingredients provided"}), 400
            
        ingredients = ingredients_str.split(',')
        limit = request.args.get('limit', 10, type=int)
        ranking = request.args.get('ranking', 1, type=int)
        ignore_pantry = request.args.get('ignorePantry', 'false').lower() == 'true'
        
        # Check for apiProvider in camelCase (frontend convention) or api_provider in snake_case (backend convention)
        api_provider = request.args.get('apiProvider', request.args.get('api_provider', None))
        current_app.logger.info(f"API Provider from request: {api_provider}")
    
    # Validate ingredients
    if not ingredients or not isinstance(ingredients, list):
        current_app.logger.warning("Invalid ingredients format provided")
        return jsonify({"error": "Ingredients must be a non-empty list"}), 400
    
    # Clean ingredients (trim whitespace, convert to lowercase)
    ingredients = [ingredient.strip().lower() for ingredient in ingredients if isinstance(ingredient, str) and ingredient.strip()]
    
    if not ingredients:
        current_app.logger.warning("No valid ingredients provided after cleaning")
        return jsonify({"error": "No valid ingredients provided"}), 400
    
    # Log the parameters
    current_app.logger.info(f"Searching for recipes with ingredients: {ingredients}")
    current_app.logger.info(f"Parameters: limit={limit}, ranking={ranking}, ignore_pantry={ignore_pantry}, api_provider={api_provider}")
    
    try:
        # Get recipes from the recipe service
        recipes = get_recipes_by_ingredients(
            ingredients=ingredients,
            number=limit,
            ranking=ranking,
            ignore_pantry=ignore_pantry,
            api_provider=api_provider
        )
        
        current_app.logger.info(f"Found {len(recipes)} recipes")
        
        # Return the response
        return jsonify({
            "success": True,
            "count": len(recipes),
            "recipes": recipes
        })
    except Exception as e:
        current_app.logger.error(f"Error in recipe search by ingredients: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@recipe_bp.route('/<path:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    """
    Get detailed information about a specific recipe
    
    Path parameters:
    - recipe_id: ID of the recipe (can be a string for Edamam recipes)
    
    Query parameters:
    - user_id: User ID for checking if the recipe is in favorites (optional)
    - apiProvider: API provider to use (optional, default: edamam)
    
    Returns:
    - Detailed recipe information including ingredients, instructions, and nutrition
    """
    current_app.logger.info(f"Recipe details endpoint accessed for ID: {recipe_id}")
    
    # Get user ID from query parameter (if provided)
    user_id = request.args.get('user_id')
    
    # Always use Edamam API
    api_provider = 'edamam'
    current_app.logger.info(f"Using API Provider: {api_provider}")
    
    try:
        recipe = get_recipe_details(recipe_id, api_provider)
        current_app.logger.info(f"Successfully retrieved recipe: {recipe.get('title', 'Unknown')}")
        
        # Check if the recipe is in the user's favorites
        is_favorited = False
        if user_id:
            try:
                is_favorited = is_favorite(user_id, recipe_id)
            except Exception as e:
                current_app.logger.warning(f"Error checking favorite status: {str(e)}")
        
        return jsonify({
            "success": True,
            "recipe": recipe,
            "is_favorite": is_favorited
        })
    except Exception as e:
        current_app.logger.error(f"Error retrieving recipe {recipe_id}: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@recipe_bp.route('/search', methods=['GET'])
def search_recipes_endpoint():
    """
    Search for recipes by query with optional filters
    
    Query parameters:
    - query: Search query (required)
    - cuisine: Cuisine type (optional)
    - diet: Diet type (optional)
    - intolerances: Comma-separated list of intolerances (optional)
    - limit: Number of results to return (optional, default: 10)
    - apiProvider: API provider to use (optional, default: from environment)
    
    Returns:
    - List of recipes matching the search criteria
    """
    current_app.logger.info("Recipe search endpoint accessed")
    
    # Get query parameters
    query = request.args.get('query')
    cuisine = request.args.get('cuisine')
    diet = request.args.get('diet')
    intolerances = request.args.get('intolerances')
    limit = request.args.get('limit', 10)
    
    # Check for apiProvider in camelCase (frontend convention) or api_provider in snake_case (backend convention)
    api_provider = request.args.get('apiProvider', request.args.get('api_provider', None))
    current_app.logger.info(f"API Provider from request: {api_provider}")
    
    # Validate query
    if not query:
        current_app.logger.warning("No query provided in request")
        return jsonify({"error": "No query provided"}), 400
    
    # Validate limit
    try:
        limit = int(limit)
        if limit < 1 or limit > 100:
            limit = 10
    except (ValueError, TypeError):
        limit = 10
    
    # Log the search parameters
    current_app.logger.info(f"Searching for recipes with query: {query}")
    current_app.logger.info(f"Parameters: cuisine={cuisine}, diet={diet}, intolerances={intolerances}, limit={limit}, api_provider={api_provider}")
    
    try:
        # Get recipes from the recipe service
        recipes = search_recipes(
            query=query,
            cuisine=cuisine,
            diet=diet,
            intolerances=intolerances,
            number=limit,
            api_provider=api_provider
        )
        
        current_app.logger.info(f"Successfully found {len(recipes)} recipes")
        
        # Return the response
        return jsonify({
            "success": True,
            "count": len(recipes),
            "recipes": recipes
        })
    except Exception as e:
        current_app.logger.error(f"Error in recipe search: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@recipe_bp.route('/random', methods=['GET'])
def get_random_recipes_endpoint():
    """
    Get random recipes with optional tags
    
    Query parameters:
    - tags: Comma-separated list of tags (optional)
    - limit: Number of results to return (optional, default: 10)
    - apiProvider: API provider to use (optional, default: from environment)
    
    Returns:
    - List of random recipes
    """
    current_app.logger.info("Random recipes endpoint accessed")
    
    # Get query parameters
    tags = request.args.get('tags')
    limit = request.args.get('limit', 10)
    
    # Check for apiProvider in camelCase (frontend convention) or api_provider in snake_case (backend convention)
    api_provider = request.args.get('apiProvider', request.args.get('api_provider', None))
    current_app.logger.info(f"API Provider from request: {api_provider}")
    
    # Validate limit
    try:
        limit = int(limit)
        if limit < 1 or limit > 100:
            limit = 10
    except (ValueError, TypeError):
        limit = 10
    
    # Log the parameters
    current_app.logger.info(f"Getting random recipes with tags: {tags}")
    current_app.logger.info(f"Parameters: limit={limit}, api_provider={api_provider}")
    
    try:
        # Get recipes from the recipe service
        recipes = get_random_recipes(
            tags=tags,
            number=limit,
            api_provider=api_provider
        )
        
        current_app.logger.info(f"Successfully retrieved {len(recipes)} random recipes")
        
        # Return the response
        return jsonify({
            "success": True,
            "count": len(recipes),
            "recipes": recipes
        })
    except Exception as e:
        current_app.logger.error(f"Error getting random recipes: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@recipe_bp.route('/cuisines', methods=['GET'])
def get_cuisines_endpoint():
    """
    Get a list of supported cuisines
    
    Returns:
    - List of cuisine types
    """
    current_app.logger.info("Cuisines endpoint accessed")
    
    try:
        cuisines = get_cuisines()
        
        current_app.logger.info(f"Successfully retrieved {len(cuisines)} cuisines")
        
        # Return the response
        return jsonify({
            "success": True,
            "count": len(cuisines),
            "cuisines": cuisines
        })
    except Exception as e:
        current_app.logger.error(f"Error getting cuisines: {str(e)}")
        return jsonify({"error": str(e)}), getattr(e, 'status_code', 500)

@recipe_bp.route('/diets', methods=['GET'])
def get_diets_endpoint():
    """
    Get a list of supported diets
    
    Returns:
    - List of diet types
    """
    current_app.logger.info("Diets endpoint accessed")
    
    try:
        diets = get_diets()
        
        current_app.logger.info(f"Successfully retrieved {len(diets)} diets")
        
        # Return the response
        return jsonify({
            "success": True,
            "count": len(diets),
            "diets": diets
        })
    except Exception as e:
        current_app.logger.error(f"Error getting diets: {str(e)}")
        return jsonify({"error": str(e)}), getattr(e, 'status_code', 500)

@recipe_bp.route('/intolerances', methods=['GET'])
def get_intolerances_endpoint():
    """
    Get a list of supported intolerances
    
    Returns:
    - List of intolerances
    """
    current_app.logger.info("Intolerances endpoint accessed")
    
    try:
        intolerances = get_intolerances()
        
        current_app.logger.info(f"Successfully retrieved {len(intolerances)} intolerances")
        
        # Return the response
        return jsonify({
            "success": True,
            "count": len(intolerances),
            "intolerances": intolerances
        })
    except Exception as e:
        current_app.logger.error(f"Error getting intolerances: {str(e)}")
        return jsonify({"error": str(e)}), getattr(e, 'status_code', 500)

@recipe_bp.route('/favorites', methods=['GET'])
def get_favorites_endpoint():
    """
    Get a user's favorite recipes
    
    Query parameters:
    - user_id: User ID (required)
    - limit: Maximum number of favorites to return (optional)
    - sort_by: Field to sort by (optional, default: 'added_at')
    - reverse: Whether to reverse the sort order (optional, default: true)
    
    Returns:
    - List of favorite recipes
    """
    current_app.logger.info("Favorites endpoint accessed")
    
    # Get query parameters
    user_id = request.args.get('user_id')
    limit = request.args.get('limit')
    sort_by = request.args.get('sort_by', 'added_at')
    reverse = request.args.get('reverse', 'true').lower() == 'true'
    
    # Validate user_id
    if not user_id:
        current_app.logger.warning("No user ID provided in request")
        return jsonify({"error": "No user ID provided"}), 400
    
    # Validate limit
    if limit:
        try:
            limit = int(limit)
            if limit < 1:
                limit = None
        except (ValueError, TypeError):
            limit = None
    
    # Log the parameters
    current_app.logger.info(f"Getting favorites for user: {user_id}")
    current_app.logger.info(f"Parameters: limit={limit}, sort_by={sort_by}, reverse={reverse}")
    
    try:
        # Get favorites from user service
        favorites = get_user_favorites(
            user_id=user_id,
            limit=limit,
            sort_by=sort_by,
            reverse=reverse
        )
        
        current_app.logger.info(f"Successfully retrieved {len(favorites)} favorites")
        
        # Return the response
        return jsonify({
            "success": True,
            "count": len(favorites),
            "favorites": favorites
        })
    except Exception as e:
        current_app.logger.error(f"Error getting favorites: {str(e)}")
        return jsonify({"error": str(e)}), 500

@recipe_bp.route('/favorites', methods=['POST'])
def add_favorite_endpoint():
    """
    Add a recipe to a user's favorites
    
    Expects a JSON with:
    - 'user_id': User ID (required)
    - 'recipe': Recipe data (required)
    
    Returns:
    - Success message
    """
    current_app.logger.info("Add favorite endpoint accessed")
    
    # Get request data
    data = request.get_json()
    
    # Validate data
    if not data:
        current_app.logger.warning("No data provided in request")
        return jsonify({"error": "No data provided"}), 400
    
    # Validate user_id
    user_id = data.get('user_id')
    if not user_id:
        current_app.logger.warning("No user ID provided in request")
        return jsonify({"error": "No user ID provided"}), 400
    
    # Validate recipe
    recipe = data.get('recipe')
    if not recipe:
        current_app.logger.warning("No recipe provided in request")
        return jsonify({"error": "No recipe provided"}), 400
    
    # Log the parameters
    current_app.logger.info(f"Adding recipe to favorites for user: {user_id}")
    
    try:
        # Add favorite
        success = add_favorite(user_id, recipe)
        
        if success:
            current_app.logger.info(f"Successfully added recipe to favorites")
            return jsonify({
                "success": True,
                "message": "Recipe added to favorites"
            })
        else:
            current_app.logger.warning(f"Recipe already in favorites")
            return jsonify({
                "success": False,
                "message": "Recipe already in favorites"
            })
    except Exception as e:
        current_app.logger.error(f"Error adding favorite: {str(e)}")
        return jsonify({"error": str(e)}), 500

@recipe_bp.route('/favorites/<int:recipe_id>', methods=['DELETE'])
def remove_favorite_endpoint(recipe_id):
    """
    Remove a recipe from a user's favorites
    
    Query parameters:
    - user_id: User ID (required)
    
    Returns:
    - Success message
    """
    current_app.logger.info(f"Remove favorite endpoint accessed for recipe ID: {recipe_id}")
    
    # Get query parameters
    user_id = request.args.get('user_id')
    
    # Validate user_id
    if not user_id:
        current_app.logger.warning("No user ID provided in request")
        return jsonify({"error": "No user ID provided"}), 400
    
    # Log the parameters
    current_app.logger.info(f"Removing recipe from favorites for user: {user_id}")
    
    try:
        # Remove favorite
        success = remove_favorite(user_id, recipe_id)
        
        if success:
            current_app.logger.info(f"Successfully removed recipe from favorites")
            return jsonify({
                "success": True,
                "message": "Recipe removed from favorites"
            })
        else:
            current_app.logger.warning(f"Recipe not found in favorites")
            return jsonify({
                "success": False,
                "message": "Recipe not found in favorites"
            })
    except Exception as e:
        current_app.logger.error(f"Error removing favorite: {str(e)}")
        return jsonify({"error": str(e)}), 500

@recipe_bp.route('/preferences', methods=['GET'])
def get_preferences_endpoint():
    """
    Get a user's preferences
    
    Query parameters:
    - user_id: User ID (required)
    
    Returns:
    - User preferences
    """
    current_app.logger.info("Get preferences endpoint accessed")
    
    # Get query parameters
    user_id = request.args.get('user_id')
    
    # Validate user_id
    if not user_id:
        current_app.logger.warning("No user ID provided in request")
        return jsonify({"error": "No user ID provided"}), 400
    
    # Log the parameters
    current_app.logger.info(f"Getting preferences for user: {user_id}")
    
    try:
        # Get preferences
        preferences = get_user_preferences(user_id)
        
        current_app.logger.info(f"Successfully retrieved preferences")
        
        # Return the response
        return jsonify({
            "success": True,
            "preferences": preferences
        })
    except Exception as e:
        current_app.logger.error(f"Error getting preferences: {str(e)}")
        return jsonify({"error": str(e)}), 500

@recipe_bp.route('/preferences', methods=['POST'])
def update_preferences_endpoint():
    """
    Update a user's preferences
    
    Expects a JSON with:
    - 'user_id': User ID (required)
    - 'preferences': New preferences (required)
    
    Returns:
    - Updated preferences
    """
    current_app.logger.info("Update preferences endpoint accessed")
    
    # Get request data
    data = request.get_json()
    
    # Validate data
    if not data:
        current_app.logger.warning("No data provided in request")
        return jsonify({"error": "No data provided"}), 400
    
    # Validate user_id
    user_id = data.get('user_id')
    if not user_id:
        current_app.logger.warning("No user ID provided in request")
        return jsonify({"error": "No user ID provided"}), 400
    
    # Validate preferences
    preferences = data.get('preferences')
    if not preferences or not isinstance(preferences, dict):
        current_app.logger.warning("Invalid preferences provided in request")
        return jsonify({"error": "Invalid preferences provided"}), 400
    
    # Log the parameters
    current_app.logger.info(f"Updating preferences for user: {user_id}")
    
    try:
        # Update preferences
        updated_preferences = update_user_preferences(user_id, preferences)
        
        current_app.logger.info(f"Successfully updated preferences")
        
        # Return the response
        return jsonify({
            "success": True,
            "preferences": updated_preferences
        })
    except Exception as e:
        current_app.logger.error(f"Error updating preferences: {str(e)}")
        return jsonify({"error": str(e)}), 500

@recipe_bp.route('/instructions', methods=['POST'])
def recipe_instructions_endpoint():
    """
    Get cooking instructions for a recipe using a hybrid approach of web scraping and AI generation.
    
    Expects a JSON with:
    - 'recipe_id': ID of the recipe (required)
    - 'recipe_name': Name of the recipe (required)
    - 'source_url': URL of the recipe source (optional)
    - 'ingredients': List of ingredients (required)
    - 'servings': Number of servings (optional)
    - 'cuisine': Cuisine type (optional)
    - 'diets': List of dietary preferences (optional)
    
    Returns:
    - Recipe instructions as HTML-formatted text
    - Source of the instructions ('scraped' or 'ai-generated')
    - Whether the result was from cache
    """
    current_app.logger.info("Recipe instructions endpoint accessed")
    
    try:
        # Get request data
        data = request.json
        
        if not data:
            current_app.logger.error("No JSON data in request")
            return jsonify({"error": "No data provided"}), 400
        
        # Validate required fields
        required_fields = ['recipe_id', 'recipe_name', 'ingredients']
        for field in required_fields:
            if field not in data:
                current_app.logger.error(f"Missing required field: {field}")
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create request object
        recipe_data = RecipeInstructionsRequest(
            recipe_id=str(data['recipe_id']),
            recipe_name=data['recipe_name'],
            source_url=data.get('source_url'),
            ingredients=data['ingredients'],
            servings=data.get('servings'),
            cuisine=data.get('cuisine'),
            diets=data.get('diets', [])
        )
        
        # Use asyncio to run the async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(get_recipe_instructions(recipe_data))
        loop.close()
        
        # Return the response
        return jsonify({
            "recipe_id": response.recipe_id,
            "instructions": response.instructions,
            "source": response.source,
            "cached": response.cached
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in recipe_instructions_endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500 