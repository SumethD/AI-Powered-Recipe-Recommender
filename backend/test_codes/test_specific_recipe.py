import os
import sys
import logging
import requests
import json
from dotenv import load_dotenv

# Add the parent directory to the path to fix imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Edamam API credentials
EDAMAM_APP_ID = os.getenv('EDAMAM_APP_ID')
EDAMAM_API_KEY = os.getenv('EDAMAM_API_KEY')
BASE_URL = "https://api.edamam.com/api/recipes/v2"

def test_recipe_details(recipe_id):
    """
    Test function to retrieve recipe details directly from Edamam API.
    
    Args:
        recipe_id (str): The ID of the recipe to retrieve
    """
    logger.info(f"Testing recipe details retrieval for ID: {recipe_id}")
    
    # Check if API key is available
    if not EDAMAM_API_KEY or not EDAMAM_APP_ID:
        logger.error("Edamam API key or App ID not found")
        return
    
    # Method 1: Try to get the recipe directly using the ID
    direct_url = f"{BASE_URL}/{recipe_id}"
    params = {
        "type": "public",
        "app_id": EDAMAM_APP_ID,
        "app_key": EDAMAM_API_KEY,
    }
    
    logger.info(f"Making direct request to: {direct_url}")
    response = requests.get(direct_url, params=params)
    
    logger.info(f"Direct request status code: {response.status_code}")
    
    if response.status_code == 200:
        recipe_data = response.json()
        recipe = recipe_data.get('recipe', {})
        logger.info(f"Successfully retrieved recipe directly: {recipe.get('label', 'Unknown')}")
        logger.info(f"Recipe URI: {recipe.get('uri', 'Unknown')}")
        logger.info(f"Recipe ID from URI: {recipe.get('uri', '').split('_')[-1] if recipe.get('uri') else 'Unknown'}")
        
        # Print some recipe details
        logger.info(f"Recipe Source: {recipe.get('source', 'Unknown')}")
        logger.info(f"Recipe URL: {recipe.get('url', 'Unknown')}")
        logger.info(f"Recipe Image: {recipe.get('image', 'Unknown')}")
        
        # Print ingredients
        logger.info("Ingredients:")
        for ingredient in recipe.get('ingredients', []):
            logger.info(f"- {ingredient.get('text', 'Unknown')}")
        
        return recipe
    else:
        logger.error(f"Failed to retrieve recipe: {response.text}")
    
    # Method 2: Try searching for the recipe using the ID as a query
    search_params = {
        "type": "public",
        "app_id": EDAMAM_APP_ID,
        "app_key": EDAMAM_API_KEY,
        "q": recipe_id,
    }
    
    logger.info(f"Making search request to: {BASE_URL}")
    search_response = requests.get(BASE_URL, params=search_params)
    
    logger.info(f"Search request status code: {search_response.status_code}")
    
    if search_response.status_code == 200:
        data = search_response.json()
        hits = data.get("hits", [])
        
        logger.info(f"Found {len(hits)} recipes in search results")
        
        # Check if any of the recipes match the ID
        for hit in hits:
            recipe = hit.get("recipe", {})
            current_id = recipe.get("uri", "").split("_")[-1]
            
            logger.info(f"Recipe ID in results: {current_id}")
            logger.info(f"Recipe Title: {recipe.get('label', 'Unknown')}")
            
            if current_id == recipe_id:
                logger.info(f"Found exact match: {recipe.get('label', 'Unknown')}")
                return recipe
        
        logger.info("No exact match found in search results")
    
    return None

def test_local_api(recipe_id):
    """
    Test the local API endpoint for recipe details.
    
    Args:
        recipe_id (str): The ID of the recipe to retrieve
    """
    url = f"http://localhost:5000/api/recipes/{recipe_id}"
    logger.info(f"Testing local API endpoint: {url}")
    
    try:
        response = requests.get(url)
        logger.info(f"Local API status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Local API response: {json.dumps(data, indent=2)}")
            return data
        else:
            logger.error(f"Local API error: {response.text}")
    except Exception as e:
        logger.error(f"Error calling local API: {str(e)}")
    
    return None

def test_search_api(query):
    """
    Test the search API to find recipes matching a query.
    
    Args:
        query (str): The search query
    """
    url = "http://localhost:5000/api/recipes/search"
    logger.info(f"Testing search API with query: {query}")
    
    try:
        response = requests.get(url, params={"query": query, "apiProvider": "edamam"})
        logger.info(f"Search API status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Found {len(data.get('recipes', []))} recipes")
            
            # Print recipe titles and IDs
            for i, recipe in enumerate(data.get('recipes', [])):
                logger.info(f"Recipe {i+1}: {recipe.get('title')} (ID: {recipe.get('id')})")
            
            return data
        else:
            logger.error(f"Search API error: {response.text}")
    except Exception as e:
        logger.error(f"Error calling search API: {str(e)}")
    
    return None

if __name__ == "__main__":
    # Test with the problematic recipe ID
    recipe_id = "074f7a86525bd7598a5922825d1772b4"
    
    # Test direct Edamam API
    logger.info("Testing direct Edamam API...")
    edamam_recipe = test_recipe_details(recipe_id)
    
    # Test local API
    logger.info("\nTesting local API...")
    local_recipe = test_local_api(recipe_id)
    
    # Test search API with "Chicken Seekh Kebabs"
    logger.info("\nTesting search API with 'Chicken Seekh Kebabs'...")
    search_results = test_search_api("Chicken Seekh Kebabs") 