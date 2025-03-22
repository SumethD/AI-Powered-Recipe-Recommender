"""
Test script for the standalone AllRecipes API
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

def test_allrecipes_api():
    """Test the standalone AllRecipes API"""
    url = "http://localhost:8002/api/allrecipes"
    
    # Create a request with an AllRecipes URL
    request = {
        "url": "https://www.allrecipes.com/recipe/228122/herbed-scalloped-potatoes-and-onions/"
    }
    
    # Make the API call
    logger.info(f"Sending request to API: {url}")
    try:
        response = requests.post(
            url,
            json=request,
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
    test_allrecipes_api() 