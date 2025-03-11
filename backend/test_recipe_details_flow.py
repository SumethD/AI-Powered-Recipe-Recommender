import os
import sys
import logging
import requests
import json
import time
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

def test_direct_api_flow(query, recipe_index=0):
    """
    Test the complete flow directly with the Edamam API:
    1. Search for recipes
    2. Get a specific recipe from the search results
    3. Get the details of that recipe
    
    Args:
        query (str): The search query
        recipe_index (int): Index of the recipe to select from search results
    """
    logger.info(f"Testing direct API flow with query: {query}")
    
    # Step 1: Search for recipes
    search_params = {
        "type": "public",
        "app_id": EDAMAM_APP_ID,
        "app_key": EDAMAM_API_KEY,
        "q": query,
    }
    
    logger.info(f"Making search request to Edamam API: {BASE_URL}")
    search_response = requests.get(BASE_URL, params=search_params)
    
    if search_response.status_code != 200:
        logger.error(f"Search request failed: {search_response.status_code}")
        return
    
    search_data = search_response.json()
    hits = search_data.get("hits", [])
    
    if not hits:
        logger.error("No recipes found in search results")
        return
    
    # Step 2: Select a recipe from the search results
    selected_hit = hits[min(recipe_index, len(hits) - 1)]
    selected_recipe = selected_hit.get("recipe", {})
    recipe_id = selected_recipe.get("uri", "").split("_")[-1]
    recipe_title = selected_recipe.get("label", "")
    
    logger.info(f"Selected recipe: ID={recipe_id}, Title={recipe_title}")
    
    # Step 3: Get the details of the selected recipe
    details_url = f"{BASE_URL}/{recipe_id}"
    details_params = {
        "type": "public",
        "app_id": EDAMAM_APP_ID,
        "app_key": EDAMAM_API_KEY,
    }
    
    logger.info(f"Making details request to: {details_url}")
    details_response = requests.get(details_url, params=details_params)
    
    if details_response.status_code != 200:
        logger.error(f"Details request failed: {details_response.status_code}")
        return
    
    details_data = details_response.json()
    details_recipe = details_data.get("recipe", {})
    details_title = details_recipe.get("label", "")
    
    logger.info(f"Retrieved recipe details: Title={details_title}")
    
    # Verify that the recipe details match the selected recipe
    if recipe_title == details_title:
        logger.info("SUCCESS: Recipe titles match between search and details")
    else:
        logger.error(f"ERROR: Recipe titles don't match: Search={recipe_title}, Details={details_title}")
    
    return {
        "search_recipe": selected_recipe,
        "details_recipe": details_recipe,
        "recipe_id": recipe_id
    }

def test_backend_api_flow(query, recipe_index=0):
    """
    Test the complete flow using our backend API:
    1. Search for recipes
    2. Get a specific recipe from the search results
    3. Get the details of that recipe
    
    Args:
        query (str): The search query
        recipe_index (int): Index of the recipe to select from search results
    """
    logger.info(f"Testing backend API flow with query: {query}")
    
    # Step 1: Search for recipes
    search_url = "http://localhost:5000/api/recipes/search"
    search_params = {
        "query": query,
        "apiProvider": "edamam"
    }
    
    logger.info(f"Making search request to backend API: {search_url}")
    search_response = requests.get(search_url, params=search_params)
    
    if search_response.status_code != 200:
        logger.error(f"Search request failed: {search_response.status_code}")
        return
    
    search_data = search_response.json()
    recipes = search_data.get("recipes", [])
    
    if not recipes:
        logger.error("No recipes found in search results")
        return
    
    # Step 2: Select a recipe from the search results
    selected_recipe = recipes[min(recipe_index, len(recipes) - 1)]
    recipe_id = selected_recipe.get("id", "")
    recipe_title = selected_recipe.get("title", "")
    
    logger.info(f"Selected recipe: ID={recipe_id}, Title={recipe_title}")
    
    # Step 3: Get the details of the selected recipe
    details_url = f"http://localhost:5000/api/recipes/{recipe_id}"
    
    logger.info(f"Making details request to: {details_url}")
    details_response = requests.get(details_url)
    
    if details_response.status_code != 200:
        logger.error(f"Details request failed: {details_response.status_code}")
        return
    
    details_data = details_response.json()
    details_recipe = details_data.get("recipe", {})
    details_title = details_recipe.get("title", "")
    
    logger.info(f"Retrieved recipe details: Title={details_title}")
    
    # Verify that the recipe details match the selected recipe
    if recipe_title == details_title:
        logger.info("SUCCESS: Recipe titles match between search and details")
    else:
        logger.error(f"ERROR: Recipe titles don't match: Search={recipe_title}, Details={details_title}")
    
    return {
        "search_recipe": selected_recipe,
        "details_recipe": details_recipe,
        "recipe_id": recipe_id
    }

def test_multiple_queries():
    """Test multiple search queries to verify consistency"""
    queries = [
        "Chicken Seekh Kebabs",
        "Pasta Carbonara",
        "Vegetable Curry",
        "Chocolate Cake",
        "Beef Stew"
    ]
    
    results = {}
    
    for query in queries:
        logger.info(f"\n{'='*50}\nTesting query: {query}\n{'='*50}")
        
        # Test direct API flow
        logger.info("\nTesting direct Edamam API flow:")
        direct_result = test_direct_api_flow(query)
        
        # Wait a bit to avoid rate limiting
        time.sleep(1)
        
        # Test backend API flow
        logger.info("\nTesting backend API flow:")
        backend_result = test_backend_api_flow(query)
        
        results[query] = {
            "direct": direct_result,
            "backend": backend_result
        }
        
        # Wait a bit between queries
        time.sleep(2)
    
    return results

if __name__ == "__main__":
    # Test the complete flow with multiple queries
    test_results = test_multiple_queries()
    
    # Print a summary of the results
    logger.info("\n\n" + "="*80)
    logger.info("SUMMARY OF TEST RESULTS")
    logger.info("="*80)
    
    for query, result in test_results.items():
        direct_result = result.get("direct")
        backend_result = result.get("backend")
        
        logger.info(f"\nQuery: {query}")
        
        if direct_result:
            direct_id = direct_result.get("recipe_id")
            direct_title = direct_result.get("details_recipe", {}).get("label", "")
            logger.info(f"Direct API: ID={direct_id}, Title={direct_title}")
        else:
            logger.info("Direct API: Failed")
        
        if backend_result:
            backend_id = backend_result.get("recipe_id")
            backend_title = backend_result.get("details_recipe", {}).get("title", "")
            logger.info(f"Backend API: ID={backend_id}, Title={backend_title}")
        else:
            logger.info("Backend API: Failed")
        
        # Check if the backend and direct API results match
        if direct_result and backend_result:
            direct_id = direct_result.get("recipe_id")
            backend_id = backend_result.get("recipe_id")
            
            if direct_id == backend_id:
                logger.info("MATCH: Recipe IDs match between direct and backend APIs")
            else:
                logger.info(f"MISMATCH: Recipe IDs don't match: Direct={direct_id}, Backend={backend_id}") 