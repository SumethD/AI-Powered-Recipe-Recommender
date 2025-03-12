import asyncio
import aiohttp
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("test-scraping-priority")

async def test_scraping_priority():
    """Test if the API attempts to scrape first before falling back to AI generation."""
    logger.info("Testing if recipe instructions API prioritizes scraping over AI generation")
    
    # Test with a real AllRecipes URL that should be scrapable
    test_url = "https://www.allrecipes.com/recipe/228122/herbed-scalloped-potatoes-and-onions/"
    
    # Prepare the test request
    request_body = {
        "recipe_id": "test123",
        "recipe_name": "Herbed Scalloped Potatoes and Onions",
        "source_url": test_url,
        "ingredients": [
            "2 tablespoons butter",
            "3 medium potatoes, thinly sliced",
            "1 large onion, thinly sliced"
        ]
    }
    
    try:
        # Make a request to the recipe instructions API
        async with aiohttp.ClientSession() as session:
            logger.info(f"Sending request to API with URL: {test_url}")
            async with session.post(
                "http://localhost:8005/api/recipe-instructions",
                json=request_body,
                headers={"Content-Type": "application/json"},
                timeout=30
            ) as response:
                logger.info(f"Response status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Source of instructions: {data.get('source', 'unknown')}")
                    logger.info(f"Instructions length: {len(data.get('instructions', ''))}")
                    logger.info(f"First 150 chars: {data.get('instructions', '')[:150]}...")
                    
                    # Check if instructions were scraped or AI-generated
                    if data.get('source') == 'scraped':
                        logger.info("SUCCESS: Instructions were scraped first as expected")
                    else:
                        logger.warning(f"UNEXPECTED: Instructions were not scraped, but {data.get('source')}")
                else:
                    error_text = await response.text()
                    logger.error(f"API request failed with status {response.status}: {error_text}")
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")

    # Test with a non-existent URL to verify fallback to AI generation
    fake_url = "https://example.com/nonexistent-recipe"
    
    # Prepare the test request
    request_body = {
        "recipe_id": "test456",
        "recipe_name": "Fake Recipe",
        "source_url": fake_url,
        "ingredients": [
            "1 cup ingredient 1",
            "2 cups ingredient 2",
            "3 tablespoons ingredient 3"
        ]
    }
    
    try:
        # Make a request to the recipe instructions API
        async with aiohttp.ClientSession() as session:
            logger.info(f"Sending request to API with fake URL: {fake_url}")
            async with session.post(
                "http://localhost:8005/api/recipe-instructions",
                json=request_body,
                headers={"Content-Type": "application/json"},
                timeout=30
            ) as response:
                logger.info(f"Response status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Source of instructions: {data.get('source', 'unknown')}")
                    logger.info(f"Instructions length: {len(data.get('instructions', ''))}")
                    logger.info(f"First 150 chars: {data.get('instructions', '')[:150]}...")
                    
                    # Check if instructions were AI-generated after scraping failed
                    if data.get('source') == 'ai-generated':
                        logger.info("SUCCESS: Fallback to AI generation worked as expected")
                    else:
                        logger.warning(f"UNEXPECTED: Instructions were not AI-generated, but {data.get('source')}")
                else:
                    error_text = await response.text()
                    logger.error(f"API request failed with status {response.status}: {error_text}")
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_scraping_priority()) 