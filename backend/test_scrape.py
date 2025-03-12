import asyncio
import logging
import aiohttp
from bs4 import BeautifulSoup
import json
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("test-scraper")

async def test_scrape(url):
    logger.info(f"Testing scraping for URL: {url}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            logger.info("Sending HTTP request...")
            async with session.get(url, headers=headers, timeout=30) as response:
                logger.info(f"Status: {response.status}")
                
                if response.status != 200:
                    logger.error(f"Failed to fetch {url}: HTTP {response.status}")
                    return
                
                logger.info("Reading response content...")
                html = await response.text()
                logger.info(f"Response length: {len(html)} bytes")
                
                # Parse HTML
                logger.info("Parsing HTML...")
                soup = BeautifulSoup(html, "html.parser")
                
                # Try various selectors for recipes
                selectors = [
                    ".directions-container .directions__container ol li",
                    ".recipe-directions__list--item",
                    "[data-testid=\"recipe-instructions\"] li",
                    ".mntl-sc-block-group--LI",
                    ".component--instructions li"
                ]
                
                for selector in selectors:
                    logger.info(f"Trying selector: {selector}")
                    elements = soup.select(selector)
                    logger.info(f"Found {len(elements)} elements with selector: {selector}")
                    
                    if elements:
                        for i, element in enumerate(elements[:3]):
                            logger.info(f"Element {i+1}: {element.get_text(strip=True)}")
                
                # Try to find JSON-LD data
                logger.info("Looking for JSON-LD data...")
                script_tags = soup.find_all("script", {"type": "application/ld+json"})
                logger.info(f"Found {len(script_tags)} JSON-LD script tags")
                
                for i, script in enumerate(script_tags):
                    try:
                        data = json.loads(script.string)
                        logger.info(f"Script tag {i+1} contains valid JSON")
                        
                        # Check if it's a recipe
                        if isinstance(data, list):
                            data = data[0]
                        
                        if "@type" in data:
                            logger.info(f"@type: {data['@type']}")
                            
                            if data["@type"] in ["Recipe", "recipe"]:
                                logger.info("Found Recipe JSON-LD data")
                                
                                if "recipeInstructions" in data:
                                    instructions = data["recipeInstructions"]
                                    logger.info(f"recipeInstructions type: {type(instructions)}")
                                    
                                    if isinstance(instructions, list):
                                        logger.info(f"Found {len(instructions)} instructions")
                                        for i, step in enumerate(instructions[:3]):
                                            if isinstance(step, str):
                                                logger.info(f"Step {i+1}: {step}")
                                            elif isinstance(step, dict) and "text" in step:
                                                logger.info(f"Step {i+1}: {step['text']}")
                    except json.JSONDecodeError:
                        logger.warning(f"Script tag {i+1} does not contain valid JSON")
                    except Exception as e:
                        logger.error(f"Error parsing script tag {i+1}: {str(e)}")
    
    except asyncio.TimeoutError:
        logger.error("Request timed out")
    except Exception as e:
        logger.error(f"Error: {str(e)}")

if __name__ == "__main__":
    url = "https://www.allrecipes.com/recipe/142500/menas-baked-macaroni-and-cheese-with-caramelized-onion"
    asyncio.run(test_scrape(url))
    logger.info("Done") 