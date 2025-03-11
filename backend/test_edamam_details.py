import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure API key
EDAMAM_APP_ID = os.getenv("EDAMAM_APP_ID")
EDAMAM_API_KEY = os.getenv("EDAMAM_API_KEY")
print(f"Using Edamam API key: {EDAMAM_API_KEY}")
print(f"Using Edamam APP ID: {EDAMAM_APP_ID}")
BASE_URL = "https://api.edamam.com/api/recipes/v2"

def test_edamam_api():
    """
    Test the Edamam API directly
    """
    print("Testing Edamam API...")
    
    # First, get a random recipe
    params = {
        "type": "public",
        "app_id": EDAMAM_APP_ID,
        "app_key": EDAMAM_API_KEY,
        "q": "random",
        "random": "true",
    }
    
    # Make the API request
    print(f"Making request to Edamam API: {BASE_URL}")
    response = requests.get(BASE_URL, params=params)
    
    # Log the response status code
    print(f"Response status code: {response.status_code}")
    
    # If the response is not successful, log the response content
    if response.status_code != 200:
        print(f"Error response: {response.text}")
        return
    
    # Parse and return the results
    data = response.json()
    hits = data.get("hits", [])
    
    print(f"Retrieved {len(hits)} recipes")
    
    # Get the first recipe
    if hits:
        recipe = hits[0].get("recipe", {})
        recipe_uri = recipe.get("uri", "")
        recipe_id = recipe_uri.split("_")[-1]
        print(f"First recipe: {recipe.get('label', '')}")
        print(f"Recipe URI: {recipe_uri}")
        print(f"Recipe ID: {recipe_id}")
        
        # Now try to get the recipe details
        print("\nTesting recipe details...")
        params = {
            "type": "public",
            "app_id": EDAMAM_APP_ID,
            "app_key": EDAMAM_API_KEY,
            "uri": recipe_uri,
        }
        
        # Make the API request
        print(f"Making request to Edamam API: {BASE_URL}")
        print(f"Request parameters: {params}")
        response = requests.get(BASE_URL, params=params)
        
        # Log the response status code
        print(f"Response status code: {response.status_code}")
        
        # If the response is not successful, log the response content
        if response.status_code != 200:
            print(f"Error response: {response.text}")
            return
        
        # Parse and return the results
        data = response.json()
        hits = data.get("hits", [])
        
        print(f"Retrieved {len(hits)} recipes")
        
        # Print the first recipe
        if hits:
            recipe = hits[0].get("recipe", {})
            print(f"Recipe details: {recipe.get('label', '')}")
            print(f"Source: {recipe.get('source', '')}")
            print(f"URL: {recipe.get('url', '')}")
            print(f"Ingredients: {recipe.get('ingredientLines', [])}")
        else:
            print("No recipe details found")
    
if __name__ == "__main__":
    test_edamam_api() 