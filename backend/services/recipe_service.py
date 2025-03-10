import os
import logging
import sys
from dotenv import load_dotenv

# Add the parent directory to the path to fix imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Print debug information
print("Importing services in recipe_service.py")
try:
    import services.spoonacular_service as spoonacular_service
    print("Successfully imported spoonacular_service")
except Exception as e:
    print(f"Error importing spoonacular_service: {str(e)}")

try:
    import services.edamam_service as edamam_service
    print("Successfully imported edamam_service")
except Exception as e:
    print(f"Error importing edamam_service: {str(e)}")

# Determine which API to use
API_PROVIDER = os.getenv("API_PROVIDER", "spoonacular").lower()  # Default to spoonacular if not set
logger.info(f"Recipe Service initialized with API_PROVIDER: {API_PROVIDER}")
print(f"Recipe Service initialized with API_PROVIDER: {API_PROVIDER}")

def get_recipes_by_ingredients(ingredients, number=10, ranking=1, ignore_pantry=False):
    """
    Get recipes based on a list of ingredients, using the configured API provider.
    
    Args:
        ingredients (list): List of ingredients
        number (int, optional): Number of results to return. Defaults to 10.
        ranking (int, optional): Ranking parameter (1 or 2). Defaults to 1.
        ignore_pantry (bool, optional): Whether to ignore pantry ingredients. Defaults to False.
    
    Returns:
        list: List of recipe objects
    """
    logger.info(f"Using {API_PROVIDER} API for get_recipes_by_ingredients")
    
    try:
        if API_PROVIDER == "edamam":
            logger.info("Calling edamam_service.get_recipes_by_ingredients")
            return edamam_service.get_recipes_by_ingredients(ingredients, number)
        else:
            logger.info("Calling spoonacular_service.get_recipes_by_ingredients")
            return spoonacular_service.get_recipes_by_ingredients(ingredients, number, ranking, ignore_pantry)
    except Exception as e:
        logger.error(f"Error in get_recipes_by_ingredients with {API_PROVIDER}: {str(e)}")
        
        # Try fallback to the other API if the primary one fails
        try:
            fallback_api = "spoonacular" if API_PROVIDER == "edamam" else "edamam"
            logger.info(f"Attempting fallback to {fallback_api} API")
            
            if fallback_api == "edamam":
                return edamam_service.get_recipes_by_ingredients(ingredients, number)
            else:
                return spoonacular_service.get_recipes_by_ingredients(ingredients, number, ranking, ignore_pantry)
        except Exception as fallback_error:
            logger.error(f"Fallback to {fallback_api} also failed: {str(fallback_error)}")
            raise Exception(f"Failed to get recipes by ingredients: {str(e)}")

def get_recipe_details(recipe_id):
    """
    Get detailed information about a specific recipe, using the configured API provider.
    
    Args:
        recipe_id (int/str): The ID of the recipe
    
    Returns:
        dict: Recipe details
    """
    logger.info(f"Using {API_PROVIDER} API for get_recipe_details")
    
    try:
        if API_PROVIDER == "edamam":
            return edamam_service.get_recipe_details(recipe_id)
        else:
            return spoonacular_service.get_recipe_details(recipe_id)
    except Exception as e:
        logger.error(f"Error in get_recipe_details with {API_PROVIDER}: {str(e)}")
        
        # Try fallback to the other API if the primary one fails
        try:
            fallback_api = "spoonacular" if API_PROVIDER == "edamam" else "edamam"
            logger.info(f"Attempting fallback to {fallback_api} API")
            
            if fallback_api == "edamam":
                return edamam_service.get_recipe_details(recipe_id)
            else:
                return spoonacular_service.get_recipe_details(recipe_id)
        except Exception as fallback_error:
            logger.error(f"Fallback to {fallback_api} also failed: {str(fallback_error)}")
            raise Exception(f"Failed to get recipe details: {str(e)}")

def search_recipes(query, cuisine="", diet="", intolerances="", number=10):
    """
    Search for recipes by query with optional filters, using the configured API provider.
    
    Args:
        query (str): Search query
        cuisine (str, optional): Cuisine type. Defaults to "".
        diet (str, optional): Diet restriction. Defaults to "".
        intolerances (str, optional): Food intolerances. Defaults to "".
        number (int, optional): Number of results to return. Defaults to 10.
    
    Returns:
        list: List of recipe objects
    """
    logger.info(f"Using {API_PROVIDER} API for search_recipes")
    
    try:
        if API_PROVIDER == "edamam":
            return edamam_service.search_recipes(query, cuisine, diet, intolerances, number)
        else:
            return spoonacular_service.search_recipes(query, cuisine, diet, intolerances, number)
    except Exception as e:
        logger.error(f"Error in search_recipes with {API_PROVIDER}: {str(e)}")
        
        # Try fallback to the other API if the primary one fails
        try:
            fallback_api = "spoonacular" if API_PROVIDER == "edamam" else "edamam"
            logger.info(f"Attempting fallback to {fallback_api} API")
            
            if fallback_api == "edamam":
                return edamam_service.search_recipes(query, cuisine, diet, intolerances, number)
            else:
                return spoonacular_service.search_recipes(query, cuisine, diet, intolerances, number)
        except Exception as fallback_error:
            logger.error(f"Fallback to {fallback_api} also failed: {str(fallback_error)}")
            raise Exception(f"Failed to search recipes: {str(e)}")

def get_random_recipes(tags="", number=5):
    """
    Get random recipes, optionally filtered by tags, using the configured API provider.
    
    Args:
        tags (str, optional): Comma-separated list of tags. Defaults to "".
        number (int, optional): Number of results to return. Defaults to 5.
    
    Returns:
        list: List of recipe objects
    """
    logger.info(f"Using {API_PROVIDER} API for get_random_recipes")
    
    try:
        if API_PROVIDER == "edamam":
            logger.info("Calling edamam_service.get_random_recipes")
            return edamam_service.get_random_recipes(tags, number)
        else:
            logger.info("Calling spoonacular_service.get_random_recipes")
            return spoonacular_service.get_random_recipes(tags, number)
    except Exception as e:
        logger.error(f"Error in get_random_recipes with {API_PROVIDER}: {str(e)}")
        
        # Try fallback to the other API if the primary one fails
        try:
            fallback_api = "spoonacular" if API_PROVIDER == "edamam" else "edamam"
            logger.info(f"Attempting fallback to {fallback_api} API")
            
            if fallback_api == "edamam":
                return edamam_service.get_random_recipes(tags, number)
            else:
                return spoonacular_service.get_random_recipes(tags, number)
        except Exception as fallback_error:
            logger.error(f"Fallback to {fallback_api} also failed: {str(fallback_error)}")
            raise Exception(f"Failed to get random recipes: {str(e)}")

def get_cuisines():
    """
    Get a list of supported cuisines from the configured API provider.
    
    Returns:
        list: List of cuisine names
    """
    if API_PROVIDER == "edamam":
        return edamam_service.get_cuisines()
    else:
        return spoonacular_service.get_cuisines()

def get_diets():
    """
    Get a list of supported diets from the configured API provider.
    
    Returns:
        list: List of diet names
    """
    if API_PROVIDER == "edamam":
        return edamam_service.get_diets()
    else:
        return spoonacular_service.get_diets()

def get_intolerances():
    """
    Get a list of supported intolerances from the configured API provider.
    
    Returns:
        list: List of intolerance names
    """
    if API_PROVIDER == "edamam":
        return edamam_service.get_intolerances()
    else:
        return spoonacular_service.get_intolerances() 