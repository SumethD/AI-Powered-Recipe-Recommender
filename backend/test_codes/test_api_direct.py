"""
Direct test of the API with the AllRecipes URL
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

def test_api_direct():
    """Test the API directly with the AllRecipes URL"""
    url = "http://localhost:8001/api/recipe-instructions"
    
    # Create a recipe with an AllRecipes URL
    recipe = {
        "recipe_name": "Herbed Scalloped Potatoes and Onions",
        "recipe_id": "test_allrecipes",
        "source_url": "https://www.allrecipes.com/recipe/228122/herbed-scalloped-potatoes-and-onions/",
        "ingredients": [
            "2 tablespoons butter",
            "3 medium potatoes, thinly sliced",
            "1 large onion, thinly sliced",
            "2 tablespoons all-purpose flour",
            "1 teaspoon salt",
            "1/4 teaspoon dried thyme",
            "1/4 teaspoon dried rosemary, crushed",
            "1/8 teaspoon pepper",
            "1 cup milk"
        ],
        "diets": ["vegetarian"],
        "cuisine": "American",
        "servings": 4
    }
    
    # Make the API call
    logger.info(f"Sending direct request to API: {url}")
    try:
        response = requests.post(
            url,
            json=recipe,
            timeout=30
        )
        
        # Check the response
        logger.info(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            instructions = result.get("instructions", "")
            
            logger.info(f"Instructions length: {len(instructions)} characters")
            logger.info("Instructions:")
            logger.info(instructions)
            
            # Count the number of steps
            step_count = instructions.count("\n") + 1
            logger.info(f"Number of steps: {step_count}")
            
            # Check if these are the basic instructions
            if "Gather all the ingredients for" in instructions:
                logger.warning("Received basic instructions (fallback)")
            else:
                logger.info("Received scraped instructions")
        else:
            logger.error(f"Error response: {response.text}")
            
    except Exception as e:
        logger.error(f"Error making API call: {str(e)}")

if __name__ == "__main__":
    test_api_direct() 