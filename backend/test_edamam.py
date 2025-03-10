import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure API key
EDAMAM_APP_ID = os.getenv("EDAMAM_APP_ID", "test_app_id")
EDAMAM_API_KEY = os.getenv("EDAMAM_API_KEY", "0122383f3fdc2f5e06169fcc935c550a")  # Use the provided key as default
print(f"Using Edamam API key: {EDAMAM_API_KEY}")
print(f"Using Edamam APP ID: {EDAMAM_APP_ID}")
BASE_URL = "https://api.edamam.com/api/recipes/v2"

def test_edamam_api():
    """
    Test the Edamam API directly
    """
    print("Testing Edamam API...")
    
    # Prepare the API endpoint and parameters
    params = {
        "type": "public",
        "app_id": EDAMAM_APP_ID,
        "app_key": EDAMAM_API_KEY,
        "q": "chicken",  # Simple query
    }
    
    # Log the request parameters
    print(f"Request parameters: {params}")
    
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
    
    # Print the first recipe
    if hits:
        recipe = hits[0].get("recipe", {})
        print(f"First recipe: {recipe.get('label', '')}")
        print(f"Source: {recipe.get('source', '')}")
        print(f"URL: {recipe.get('url', '')}")
        print(f"Ingredients: {recipe.get('ingredientLines', [])}")
    
if __name__ == "__main__":
    test_edamam_api() 