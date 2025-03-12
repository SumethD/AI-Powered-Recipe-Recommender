"""
Test script to validate the basic instructions generator
"""
import sys
import os
import logging
from pydantic import BaseModel
from typing import List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Add the parent directory to sys.path so we can import the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Define the request model locally to avoid circular imports
class RecipeInstructionsRequest(BaseModel):
    recipe_id: Optional[str] = None
    recipe_name: str
    source_url: Optional[str] = None
    ingredients: List[str]
    servings: Optional[int] = None
    diets: Optional[List[str]] = None
    cuisine: Optional[str] = None

# Import the function to test
from backend.recipe_instructions_service import generate_basic_instructions

def test_basic_instructions():
    """Test the basic instructions generator"""
    # Create a test recipe
    test_recipe = RecipeInstructionsRequest(
        recipe_name="Simple Test Recipe",
        recipe_id="test_recipe_1",
        ingredients=[
            "2 cups flour",
            "1 cup sugar",
            "3 eggs",
            "1/2 cup milk",
            "1 tsp vanilla extract",
            "1/2 tsp salt",
            "2 tsp baking powder"
        ],
        diets=["vegetarian"],
        cuisine="Dessert",
        servings=4
    )
    
    # Generate basic instructions
    logger.info("Generating basic instructions for test recipe")
    instructions = generate_basic_instructions(test_recipe)
    
    # Print the results
    logger.info(f"Generated {len(instructions)} characters of instructions")
    logger.info("Instructions:")
    logger.info(instructions)
    
    return instructions

if __name__ == "__main__":
    test_basic_instructions() 