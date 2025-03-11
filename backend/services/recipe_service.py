import os
import logging
import sys
from dotenv import load_dotenv
from services import edamam_service

# Add the parent directory to the path to fix imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Print debug information
print("Importing services in recipe_service.py")
try:
    import services.edamam_service as edamam_service
    print("Successfully imported edamam_service")
except Exception as e:
    print(f"Error importing edamam_service: {str(e)}")

# Force using Edamam API
API_PROVIDER = 'edamam'
logger.info(f"Recipe Service initialized with API_PROVIDER: {API_PROVIDER}")
print(f"Recipe Service initialized with API_PROVIDER: {API_PROVIDER}")

def get_recipes_by_ingredients(ingredients, number=5, ranking=1, ignore_pantry=False, api_provider=None):
    """
    Get recipes by ingredients using Edamam API.
    
    Args:
        ingredients (list): List of ingredients
        number (int): Number of recipes to return
        ranking (int): Ranking parameter (not used by Edamam)
        ignore_pantry (bool): Whether to ignore pantry ingredients (not used by Edamam)
        api_provider (str): API provider to use (currently only 'edamam' is supported)
        
    Returns:
        list: List of recipes
    """
    # Log the API provider parameter
    logger.info(f"get_recipes_by_ingredients called with api_provider: {api_provider}")
    
    # Always use Edamam API for now
    logger.info(f"Using Edamam API for get_recipes_by_ingredients with ingredients: {ingredients}")
    
    try:
        # Validate ingredients
        if not ingredients or not isinstance(ingredients, list) or len(ingredients) == 0:
            logger.error("Invalid ingredients parameter: empty or not a list")
            raise ValueError("Ingredients must be a non-empty list")
        
        # Clean ingredients
        clean_ingredients = [i.strip().lower() for i in ingredients if isinstance(i, str) and i.strip()]
        if not clean_ingredients:
            logger.error("No valid ingredients after cleaning")
            raise ValueError("No valid ingredients provided")
            
        logger.info(f"Calling edamam_service.get_recipes_by_ingredients with ingredients: {clean_ingredients}")
        return edamam_service.get_recipes_by_ingredients(clean_ingredients, number)
    except Exception as e:
        logger.error(f"Error in get_recipes_by_ingredients: {str(e)}")
        raise Exception(f"Failed to get recipes by ingredients: {str(e)}")

def get_recipe_details(recipe_id, api_provider=None):
    """
    Get detailed information about a specific recipe using Edamam API.
    
    Args:
        recipe_id (str or int): The ID of the recipe
        api_provider (str): Not used, always uses Edamam
        
    Returns:
        dict: Recipe details
    """
    # Always use Edamam API
    logger.info(f"Using Edamam API for get_recipe_details with ID: {recipe_id}")
    
    try:
        logger.info("Calling edamam_service.get_recipe_details")
        return edamam_service.get_recipe_details(recipe_id)
    except Exception as e:
        logger.error(f"Error using Edamam API: {str(e)}")
        raise Exception(f"Failed to get recipe details: {str(e)}")

def search_recipes(query, cuisine=None, diet=None, intolerances=None, number=10, api_provider=None):
    """
    Search for recipes by query and filters using Edamam API.
    
    Args:
        query (str): Search query
        cuisine (str): Cuisine filter
        diet (str): Diet filter
        intolerances (str): Intolerances filter
        number (int): Number of results to return
        api_provider (str): Not used, always uses Edamam
        
    Returns:
        list: List of recipes
    """
    # Always use Edamam API
    logger.info(f"Using Edamam API for search_recipes with query: {query}")
    
    try:
        logger.info("Calling edamam_service.search_recipes")
        return edamam_service.search_recipes(query, cuisine, diet, intolerances, number)
    except Exception as e:
        logger.error(f"Error using Edamam API: {str(e)}")
        raise Exception(f"Failed to search recipes: {str(e)}")

def get_random_recipes(tags="", number=5, api_provider=None):
    """
    Get random recipes using Edamam API.
    
    Args:
        tags (str): Tags to filter recipes (not used by Edamam)
        number (int): Number of recipes to return
        api_provider (str): Not used, always uses Edamam
        
    Returns:
        list: List of random recipes
    """
    # Always use Edamam API
    logger.info(f"Using Edamam API for get_random_recipes")
    
    try:
        logger.info("Calling edamam_service.get_random_recipes")
        return edamam_service.get_random_recipes(tags, number)
    except Exception as e:
        logger.error(f"Error using Edamam API: {str(e)}")
        raise Exception(f"Failed to get random recipes: {str(e)}")

def get_cuisines():
    """
    Get supported cuisines from Edamam API.
    
    Returns:
        list: List of supported cuisines
    """
    return edamam_service.get_cuisines()

def get_diets():
    """
    Get supported diets from Edamam API.
    
    Returns:
        list: List of supported diets
    """
    return edamam_service.get_diets()

def get_intolerances():
    """
    Get supported intolerances from Edamam API.
    
    Returns:
        list: List of supported intolerances
    """
    return edamam_service.get_intolerances() 