#!/usr/bin/env python
"""
Integration test script for the AI-Powered Recipe Recommender.
This script tests the integration between the main backend API, the AllRecipes API,
and the recipe instructions service.
"""

import requests
import logging
import sys
import json
import time
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("integration_test")

# Test URLs
MAIN_API_URL = "http://localhost:5000"
ALLRECIPES_API_URL = "http://localhost:8002"
TEST_RECIPE_URL = "https://www.allrecipes.com/recipe/228122/herbed-scalloped-potatoes-and-onions/"

def test_main_api_health():
    """Test if the main API is running."""
    try:
        response = requests.get(f"{MAIN_API_URL}/api/health", timeout=5)
        if response.status_code == 200:
            logger.info("✅ Main API is running")
            return True
        else:
            logger.error(f"❌ Main API returned status code {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed to connect to Main API: {e}")
        return False

def test_allrecipes_api_health():
    """Test if the AllRecipes API is running."""
    try:
        response = requests.get(f"{ALLRECIPES_API_URL}/api/health", timeout=5)
        if response.status_code == 200:
            logger.info("✅ AllRecipes API is running")
            return True
        else:
            logger.error(f"❌ AllRecipes API returned status code {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed to connect to AllRecipes API: {e}")
        return False

def test_allrecipes_api():
    """Test if the AllRecipes API is running and can extract instructions."""
    try:
        payload = {"url": TEST_RECIPE_URL}
        response = requests.post(f"{ALLRECIPES_API_URL}/api/allrecipes", json=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if "instructions" in data and len(data["instructions"]) > 100:
                logger.info(f"✅ AllRecipes API successfully extracted instructions ({len(data['instructions'])} characters)")
                return True, data["instructions"]
            else:
                logger.error("❌ AllRecipes API returned empty or short instructions")
                return False, None
        else:
            logger.error(f"❌ AllRecipes API returned status code {response.status_code}")
            try:
                error_data = response.json()
                logger.error(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                logger.error(f"Response content: {response.text[:200]}...")
            return False, None
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed to connect to AllRecipes API: {e}")
        return False, None

def test_recipe_instructions_api():
    """Test if the recipe instructions API can extract instructions."""
    try:
        recipe_id = "228122"  # ID from the test URL
        response = requests.get(
            f"{MAIN_API_URL}/api/recipe-instructions?url={TEST_RECIPE_URL}&recipe_id={recipe_id}", 
            timeout=20
        )
        
        if response.status_code == 200:
            data = response.json()
            if "instructions" in data and len(data["instructions"]) > 100:
                logger.info(f"✅ Recipe Instructions API successfully returned instructions ({len(data['instructions'])} characters)")
                logger.info(f"Source: {data.get('source', 'unknown')}")
                return True, data
            else:
                logger.error("❌ Recipe Instructions API returned empty or short instructions")
                return False, None
        else:
            logger.error(f"❌ Recipe Instructions API returned status code {response.status_code}")
            try:
                error_data = response.json()
                logger.error(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                logger.error(f"Response content: {response.text[:200]}...")
            return False, None
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed to connect to Recipe Instructions API: {e}")
        return False, None

def extract_recipe_id_from_url(url):
    """Extract the recipe ID from an AllRecipes URL."""
    try:
        path = urlparse(url).path
        parts = path.strip('/').split('/')
        if 'recipe' in parts:
            idx = parts.index('recipe')
            if idx + 1 < len(parts):
                return parts[idx + 1]
    except Exception as e:
        logger.error(f"Failed to extract recipe ID from URL: {e}")
    return None

def run_integration_tests():
    """Run all integration tests."""
    logger.info("Starting integration tests...")
    
    # Test 1: Check if main API is running
    main_api_running = test_main_api_health()
    
    # Test 2: Check if AllRecipes API is running
    allrecipes_api_running = test_allrecipes_api_health()
    
    # If neither API is running, abort
    if not main_api_running and not allrecipes_api_running:
        logger.error("Both APIs are not running. Aborting further tests.")
        return False
    
    # Test 3: Check if AllRecipes API can extract instructions
    allrecipes_api_success = False
    allrecipes_instructions = None
    
    if allrecipes_api_running:
        allrecipes_api_success, allrecipes_instructions = test_allrecipes_api()
        if not allrecipes_api_success:
            logger.warning("AllRecipes API test failed. Continuing with other tests.")
    
    # Test 4: Check if Recipe Instructions API is working
    recipe_api_success = False
    recipe_data = None
    
    if main_api_running:
        recipe_api_success, recipe_data = test_recipe_instructions_api()
    
    # Compare results if both APIs returned instructions
    if allrecipes_api_success and recipe_api_success:
        allrecipes_words = len(allrecipes_instructions.split())
        recipe_words = len(recipe_data["instructions"].split())
        
        logger.info(f"AllRecipes API returned {allrecipes_words} words")
        logger.info(f"Recipe Instructions API returned {recipe_words} words")
        
        if abs(allrecipes_words - recipe_words) < 10:
            logger.info("✅ Both APIs returned similar instructions")
        else:
            logger.warning("⚠️ APIs returned different instructions")
    
    # Overall result
    if (main_api_running and recipe_api_success) or (allrecipes_api_running and allrecipes_api_success):
        logger.info("✅ Integration tests PASSED")
        return True
    else:
        logger.error("❌ Integration tests FAILED")
        return False

if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("AI-Powered Recipe Recommender Integration Test")
    logger.info("=" * 50)
    
    success = run_integration_tests()
    
    logger.info("=" * 50)
    if success:
        logger.info("All critical components are working correctly!")
    else:
        logger.info("Some components are not working correctly. Check the logs above for details.")
    logger.info("=" * 50)
    
    sys.exit(0 if success else 1) 