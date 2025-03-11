import os
import sys
import json
import logging
from dotenv import load_dotenv

# Add the parent directory to the path to fix imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the services
from services.edamam_service import get_recipe_details, transform_edamam_recipe

def test_recipe_details(recipe_id):
    """
    Test the recipe details functionality.
    
    Args:
        recipe_id (str): The ID of the recipe to test
    """
    logger.info(f"Testing recipe details for ID: {recipe_id}")
    
    try:
        # Get the recipe details
        recipe = get_recipe_details(recipe_id)
        
        # Print the recipe details
        logger.info(f"Recipe details retrieved successfully:")
        logger.info(f"  ID: {recipe.get('id')}")
        logger.info(f"  Title: {recipe.get('title')}")
        logger.info(f"  Image: {recipe.get('image')}")
        logger.info(f"  Source: {recipe.get('sourceName')}")
        logger.info(f"  Source URL: {recipe.get('sourceUrl')}")
        logger.info(f"  Servings: {recipe.get('servings')}")
        logger.info(f"  Ready in minutes: {recipe.get('readyInMinutes')}")
        logger.info(f"  Ingredients: {len(recipe.get('extendedIngredients', []))}")
        
        # Print the full recipe as JSON
        logger.info("Full recipe JSON:")
        print(json.dumps(recipe, indent=2))
        
        return True
    except Exception as e:
        logger.error(f"Error testing recipe details: {str(e)}")
        return False

def main():
    """
    Main function to run the test.
    """
    # Test with a specific recipe ID
    recipe_id = "853f906a1334033a5192b8d4c4bdac12"  # The ID from the error message
    
    logger.info(f"Starting recipe details test with ID: {recipe_id}")
    
    success = test_recipe_details(recipe_id)
    
    if success:
        logger.info("Test completed successfully!")
    else:
        logger.error("Test failed!")

if __name__ == "__main__":
    main() 