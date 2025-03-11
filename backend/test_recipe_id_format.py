import os
import sys
import logging
import requests
import json
from dotenv import load_dotenv

# Add the parent directory to the path to fix imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_recipe_id_formats():
    """
    Test different recipe ID formats to see if there's any issue with the specific format.
    """
    # The problematic recipe ID
    original_id = "a869165803465378553c1a8792af3eb3"
    
    # Test different formats of the same ID
    test_ids = [
        original_id,  # Original format
        original_id.upper(),  # Uppercase
        original_id.replace("a", "A"),  # Mixed case
        original_id.replace("a", ""),  # Remove first character
        original_id + "extra",  # Add extra characters
        original_id[:-1],  # Remove last character
    ]
    
    for test_id in test_ids:
        logger.info(f"Testing recipe ID format: {test_id}")
        
        # Test with local API
        url = f"http://localhost:5000/api/recipes/{test_id}"
        try:
            response = requests.get(url)
            logger.info(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if "recipe" in data and data.get("success", False):
                    logger.info(f"Success! Recipe title: {data['recipe'].get('title', 'Unknown')}")
                else:
                    logger.error(f"API returned success=False or no recipe: {json.dumps(data, indent=2)}")
            else:
                logger.error(f"API returned error: {response.text}")
        except Exception as e:
            logger.error(f"Error calling API: {str(e)}")
        
        logger.info("-" * 50)

if __name__ == "__main__":
    test_recipe_id_formats() 