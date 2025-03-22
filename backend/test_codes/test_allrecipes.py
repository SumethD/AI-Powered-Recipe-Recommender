"""
Test script to validate the AllRecipes scraping functionality
"""
import requests
import json
import logging
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

async def test_direct_scraping():
    """Test scraping the AllRecipes URL directly"""
    url = "https://www.allrecipes.com/recipe/228122/herbed-scalloped-potatoes-and-onions/"
    
    logger.info(f"Directly scraping: {url}")
    
    # Set various timeouts and configure headers to avoid blocking
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    try:
        # Use both connect and read timeouts to ensure responsive scraping
        timeout = aiohttp.ClientTimeout(total=15, connect=5)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            logger.info(f"Sending HTTP request to {url}")
            async with session.get(url, headers=headers, allow_redirects=True) as response:
                logger.info(f"Received response from {url} with status code {response.status}")
                
                if response.status != 200:
                    logger.warning(f"Failed to retrieve page: HTTP {response.status}")
                    return
                
                # Read the HTML content
                html_content = await response.text()
                logger.info(f"Retrieved HTML content ({len(html_content)} bytes)")
                
                # Create a BeautifulSoup object
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Try the modern AllRecipes selectors
                selectors = [
                    ".mntl-sc-block-group--LI",
                    ".directions-container .directions__container ol li",
                    ".recipe-directions__list--item",
                    "[data-testid='recipe-instructions'] li",
                ]
                
                for selector in selectors:
                    elements = soup.select(selector)
                    if elements:
                        logger.info(f"Found {len(elements)} elements with selector: {selector}")
                        for i, element in enumerate(elements):
                            logger.info(f"  Step {i+1}: {element.get_text().strip()[:50]}...")
                    else:
                        logger.info(f"No elements found with selector: {selector}")
                
                # Check for JSON-LD data
                script_tags = soup.find_all('script', type='application/ld+json')
                logger.info(f"Found {len(script_tags)} JSON-LD script tags")
                
                for i, script in enumerate(script_tags):
                    try:
                        data = json.loads(script.string)
                        logger.info(f"  Script {i+1} contains valid JSON")
                        
                        # Check if it's a Recipe
                        if isinstance(data, dict) and '@type' in data:
                            logger.info(f"  Script {i+1} has @type: {data['@type']}")
                            
                            if 'recipeInstructions' in data:
                                instructions = data['recipeInstructions']
                                logger.info(f"  Script {i+1} has recipeInstructions: {type(instructions)}")
                                
                                if isinstance(instructions, list):
                                    logger.info(f"  Found {len(instructions)} instruction steps")
                    except Exception as e:
                        logger.warning(f"  Error parsing script {i+1}: {str(e)}")
                
    except Exception as e:
        logger.error(f"Error during direct scraping: {str(e)}")

def test_api_with_allrecipes():
    """Test the API with an AllRecipes URL"""
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
    logger.info("Sending request to API with AllRecipes URL")
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
            logger.info("Instructions:")
            logger.info(instructions)
            
            # Count the number of steps
            step_count = instructions.count("\n") + 1
            logger.info(f"Number of steps: {step_count}")
        else:
            logger.error(f"Error response: {response.text}")
            
    except Exception as e:
        logger.error(f"Error making API call: {str(e)}")

if __name__ == "__main__":
    # First test direct scraping
    asyncio.run(test_direct_scraping())
    
    # Then test the API
    test_api_with_allrecipes() 