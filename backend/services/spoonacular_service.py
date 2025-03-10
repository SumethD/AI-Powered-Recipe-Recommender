import os
import logging
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure API key
# SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY")
SPOONACULAR_API_KEY = "4e9a7620187941ff8a32167a0dd8ed23"  # Hardcoded for testing
print(f"Using Spoonacular API key: {SPOONACULAR_API_KEY}")
BASE_URL = "https://api.spoonacular.com"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_recipes_by_ingredients(ingredients, number=10, ranking=1, ignore_pantry=False):
    """
    Get recipes based on a list of ingredients.
    
    Args:
        ingredients (list): List of ingredients
        number (int, optional): Number of results to return. Defaults to 10.
        ranking (int, optional): Ranking parameter (1 or 2). Defaults to 1.
        ignore_pantry (bool, optional): Whether to ignore pantry ingredients. Defaults to False.
    
    Returns:
        list: List of recipe objects
    """
    try:
        logger.info(f"Searching for recipes with ingredients: {ingredients}")
        
        # Check if API key is available
        if not SPOONACULAR_API_KEY:
            logger.error("Spoonacular API key not found")
            raise Exception("Spoonacular API key not configured")
        
        # Prepare the API endpoint and parameters
        endpoint = f"{BASE_URL}/recipes/findByIngredients"
        params = {
            "apiKey": SPOONACULAR_API_KEY,
            "ingredients": ",".join(ingredients),
            "number": number,
            "ranking": ranking,
            "ignorePantry": str(ignore_pantry).lower()
        }
        
        # Make the API request
        logger.info(f"Making request to Spoonacular API: {endpoint}")
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        
        # Parse and return the results
        recipes = response.json()
        logger.info(f"Found {len(recipes)} recipes")
        return recipes
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error in get_recipes_by_ingredients: {str(e)}")
        if e.response.status_code == 401:
            raise Exception("Invalid Spoonacular API key")
        elif e.response.status_code == 402:
            raise Exception("Spoonacular API quota exceeded")
        else:
            raise Exception(f"Spoonacular API error: {str(e)}")
    except Exception as e:
        logger.error(f"Error in get_recipes_by_ingredients: {str(e)}")
        raise Exception(f"Failed to get recipes by ingredients: {str(e)}")

def get_recipe_details(recipe_id):
    """
    Get detailed information about a specific recipe.
    
    Args:
        recipe_id (int): The ID of the recipe
    
    Returns:
        dict: Recipe details
    """
    try:
        logger.info(f"Getting details for recipe ID: {recipe_id}")
        
        # Prepare the API endpoint and parameters
        endpoint = f"{BASE_URL}/recipes/{recipe_id}/information"
        params = {
            "apiKey": SPOONACULAR_API_KEY,
            "includeNutrition": "true"
        }
        
        # Make the API request
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        
        # Parse and return the results
        recipe = response.json()
        logger.info(f"Successfully retrieved details for recipe: {recipe.get('title', 'Unknown')}")
        return recipe
        
    except Exception as e:
        logger.error(f"Error in get_recipe_details: {str(e)}")
        raise Exception(f"Failed to get recipe details: {str(e)}")

def search_recipes(query, cuisine="", diet="", intolerances="", number=10):
    """
    Search for recipes by query with optional filters.
    
    Args:
        query (str): Search query
        cuisine (str, optional): Cuisine type. Defaults to "".
        diet (str, optional): Diet restriction. Defaults to "".
        intolerances (str, optional): Food intolerances. Defaults to "".
        number (int, optional): Number of results to return. Defaults to 10.
    
    Returns:
        list: List of recipe objects
    """
    try:
        logger.info(f"Searching for recipes with query: {query}")
        
        # Check if API key is available
        if not SPOONACULAR_API_KEY:
            logger.error("Spoonacular API key not found")
            raise Exception("Spoonacular API key not configured")
        
        # Prepare the API endpoint and parameters
        endpoint = f"{BASE_URL}/recipes/complexSearch"
        params = {
            "apiKey": SPOONACULAR_API_KEY,
            "query": query,
            "number": number,
            "addRecipeInformation": "true",
            "fillIngredients": "true",
        }
        
        # Add optional filters if provided
        if cuisine:
            params["cuisine"] = cuisine
        if diet:
            params["diet"] = diet
        if intolerances:
            params["intolerances"] = intolerances
        
        # Make the API request
        logger.info(f"Making request to Spoonacular API: {endpoint}")
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        
        # Parse and return the results
        data = response.json()
        recipes = data.get("results", [])
        logger.info(f"Found {len(recipes)} recipes")
        return recipes
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error in search_recipes: {str(e)}")
        if e.response.status_code == 401:
            raise Exception("Invalid Spoonacular API key")
        elif e.response.status_code == 402:
            raise Exception("Spoonacular API quota exceeded")
        else:
            raise Exception(f"Spoonacular API error: {str(e)}")
    except Exception as e:
        logger.error(f"Error in search_recipes: {str(e)}")
        raise Exception(f"Failed to search recipes: {str(e)}")

def get_random_recipes(tags="", number=5):
    """
    Get random recipes, optionally filtered by tags.
    
    Args:
        tags (str, optional): Comma-separated list of tags. Defaults to "".
        number (int, optional): Number of results to return. Defaults to 5.
    
    Returns:
        list: List of recipe objects
    """
    try:
        logger.info(f"Getting random recipes with tags: {tags}")
        
        # Prepare the API endpoint and parameters
        endpoint = f"{BASE_URL}/recipes/random"
        params = {
            "apiKey": SPOONACULAR_API_KEY,
            "number": number
        }
        
        # Add tags if provided
        if tags:
            params["tags"] = tags
        
        # Make the API request
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        
        # Parse and return the results
        result = response.json()
        recipes = result.get("recipes", [])
        logger.info(f"Retrieved {len(recipes)} random recipes")
        return recipes
        
    except Exception as e:
        logger.error(f"Error in get_random_recipes: {str(e)}")
        raise Exception(f"Failed to get random recipes: {str(e)}")

def get_cuisines():
    """
    Get a list of supported cuisines.
    
    Returns:
        list: List of cuisine names
    """
    return [
        "African", "American", "British", "Cajun", "Caribbean", "Chinese", 
        "Eastern European", "European", "French", "German", "Greek", "Indian", 
        "Irish", "Italian", "Japanese", "Jewish", "Korean", "Latin American", 
        "Mediterranean", "Mexican", "Middle Eastern", "Nordic", "Southern", 
        "Spanish", "Thai", "Vietnamese"
    ]

def get_diets():
    """
    Get a list of supported diets.
    
    Returns:
        list: List of diet names
    """
    return [
        "Gluten Free", "Ketogenic", "Vegetarian", "Lacto-Vegetarian", 
        "Ovo-Vegetarian", "Vegan", "Pescetarian", "Paleo", "Primal", "Low FODMAP", 
        "Whole30"
    ]

def get_intolerances():
    """
    Get a list of supported intolerances.
    
    Returns:
        list: List of intolerance names
    """
    return [
        "Dairy", "Egg", "Gluten", "Grain", "Peanut", "Seafood", "Sesame", 
        "Shellfish", "Soy", "Sulfite", "Tree Nut", "Wheat"
    ] 