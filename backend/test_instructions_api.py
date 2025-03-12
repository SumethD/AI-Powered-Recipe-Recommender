"""
Test script to validate the recipe instructions API
"""
import asyncio
import json
import logging
import sys
import os
import httpx
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

# Create a model for our test cases
class RecipeTest(BaseModel):
    """Test case for recipe instructions"""
    name: str
    url: str
    ingredients: List[str]
    diets: Optional[List[str]] = None
    cuisine: Optional[str] = None
    servings: Optional[int] = None


async def test_recipe_instructions():
    """Test recipe instructions API with various test cases"""
    # Test cases with URLs that might be problematic
    test_cases = [
        RecipeTest(
            name="Problematic AllRecipes Link",
            url="https://www.allrecipes.com/recipe/228122/herbed-scalloped-potatoes-and-onions/",
            ingredients=[
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
            diets=["vegetarian"],
            cuisine="American",
            servings=4
        ),
        RecipeTest(
            name="Recipe with Non-Existent URL",
            url="https://nonexistent-recipe-site.com/fake-recipe/12345",
            ingredients=[
                "1 cup flour",
                "1/2 cup sugar",
                "2 eggs",
                "1 cup milk",
                "1 tsp vanilla extract"
            ],
            cuisine="Dessert",
            servings=2
        ),
        RecipeTest(
            name="Recipe with No URL",
            url="",
            ingredients=[
                "Chicken breast",
                "Salt",
                "Pepper",
                "Olive oil",
                "Garlic powder"
            ],
            cuisine="Simple",
            servings=1
        )
    ]

    for test_case in test_cases:
        logger.info(f"Testing: {test_case.name}")
        
        # Create request JSON payload
        request_data = {
            "recipe_name": test_case.name,
            "recipe_id": f"test_{test_case.name.lower().replace(' ', '_')}",
            "source_url": test_case.url,
            "ingredients": test_case.ingredients,
            "diets": test_case.diets or [],
            "cuisine": test_case.cuisine,
            "servings": test_case.servings
        }
        
        try:
            # Test the API endpoint directly
            start_time = asyncio.get_event_loop().time()
            
            async with httpx.AsyncClient() as client:
                logger.info(f"Sending request to API for {test_case.name}")
                response = await client.post(
                    "http://localhost:8000/api/recipe-instructions",
                    json=request_data,
                    timeout=60  # Give it plenty of time for testing
                )
                
                elapsed = asyncio.get_event_loop().time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    instructions = result.get("instructions", "")
                    
                    logger.info(f"✅ Received response in {elapsed:.2f} seconds")
                    logger.info(f"Instructions length: {len(instructions)} characters")
                    
                    # Print first 150 chars of the instructions
                    preview = instructions[:150] + "..." if len(instructions) > 150 else instructions
                    logger.info(f"Preview: {preview}")
                else:
                    logger.error(f"❌ API returned status code {response.status_code}")
                    logger.error(f"Error: {response.text}")
            
        except Exception as e:
            logger.error(f"❌ Error testing {test_case.name}: {str(e)}")
        
        logger.info("-" * 50)


if __name__ == "__main__":
    asyncio.run(test_recipe_instructions()) 