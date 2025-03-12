"""
Minimal test script for the recipe instructions API
"""
import requests
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def test_api():
    """Test the API with a minimal recipe"""
    # Create a minimal recipe
    recipe = {
        "recipe_name": "Simple Test Recipe",
        "recipe_id": "test_recipe_1",
        "ingredients": ["flour", "sugar", "eggs", "milk"],
        "diets": [],
        "cuisine": "Simple",
        "servings": 2
    }
    
    # Make the API call
    logger.info("Sending request to API")
    try:
        response = requests.post(
            "http://localhost:8001/api/recipe-instructions",
            json=recipe,
            timeout=30
        )
        
        # Check the response
        logger.info(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            instructions = result.get("instructions", "")
            
            logger.info(f"Instructions length: {len(instructions)} characters")
            logger.info("Instructions preview:")
            logger.info(instructions[:150] + "..." if len(instructions) > 150 else instructions)
        else:
            logger.error(f"Error response: {response.text}")
            
    except Exception as e:
        logger.error(f"Error making API call: {str(e)}")

if __name__ == "__main__":
    test_api() 