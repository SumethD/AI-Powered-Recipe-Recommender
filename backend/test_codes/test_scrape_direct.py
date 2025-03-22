"""
Direct test of the scraping function
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import logging
import json
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

async def extract_allrecipes_instructions(soup, html_content) -> str:
    """Extract recipe instructions specifically from AllRecipes.com"""
    try:
        logger.info("Attempting specialized extraction for AllRecipes.com")
        
        # Try the modern AllRecipes selectors first (they frequently update their HTML structure)
        selectors = [
            ".mntl-sc-block-group--LI",  # Current AllRecipes structure
            ".directions-container .directions__container ol li",  # Previous structure
            ".recipe-directions__list--item",  # Older structure
            "[data-testid='recipe-instructions'] li",  # Alternative structure
        ]
        
        for selector in selectors:
            instruction_elements = soup.select(selector)
            if instruction_elements and len(instruction_elements) > 0:
                logger.info(f"Found {len(instruction_elements)} instructions using selector: {selector}")
                steps = []
                for i, step in enumerate(instruction_elements, 1):
                    text = step.get_text().strip()
                    if text and not text.lower() in ["advertisement", "watch now", "see how it's made"]:
                        # Ensure we're not capturing ads or media prompts
                        steps.append(f"{i}. {text}")
                        logger.info(f"Step {i}: {text[:50]}...")
                
                if steps:
                    return "\n".join(steps)
        
        # If the above didn't work, try a more general approach
        logger.info("Trying fallback component extraction for AllRecipes")
        component = soup.select_one(".component--instructions")
        if component:
            ol_elements = component.find_all("ol")
            if ol_elements:
                steps = []
                for ol in ol_elements:
                    li_elements = ol.find_all("li")
                    for i, li in enumerate(li_elements, 1):
                        steps.append(f"{i}. {li.get_text().strip()}")
                if steps:
                    return "\n".join(steps)
        
        # Try looking for JSON-LD data
        logger.info("Searching for structured data in AllRecipes.com")
        try:
            # Find all script tags with type application/ld+json
            script_tags = soup.find_all('script', type='application/ld+json')
            logger.info(f"Found {len(script_tags)} JSON-LD script tags")
            
            for script in script_tags:
                try:
                    json_data = json.loads(script.string)
                    logger.info(f"Found valid JSON-LD data")
                    
                    # Handle the case when it's a list
                    if isinstance(json_data, list):
                        for item in json_data:
                            if isinstance(item, dict) and '@type' in item and item['@type'] in ['Recipe', 'recipe']:
                                if 'recipeInstructions' in item:
                                    instructions = item['recipeInstructions']
                                    logger.info(f"Found recipeInstructions in JSON-LD: {type(instructions)}")
                                    
                                    # Format the instructions
                                    formatted_instructions = []
                                    
                                    if isinstance(instructions, list):
                                        for i, instruction in enumerate(instructions, 1):
                                            if isinstance(instruction, dict) and 'text' in instruction:
                                                formatted_instructions.append(f"{i}. {instruction['text']}")
                                                logger.info(f"Step {i}: {instruction['text'][:50]}...")
                                            elif isinstance(instruction, str):
                                                formatted_instructions.append(f"{i}. {instruction}")
                                                logger.info(f"Step {i}: {instruction[:50]}...")
                                    
                                    if formatted_instructions:
                                        return "\n".join(formatted_instructions)
                    
                    # Handle single recipe object
                    elif isinstance(json_data, dict):
                        # Check if it's a Recipe type
                        if '@type' in json_data and json_data['@type'] in ['Recipe', 'recipe']:
                            if 'recipeInstructions' in json_data:
                                instructions = json_data['recipeInstructions']
                                logger.info(f"Found recipeInstructions in JSON-LD: {type(instructions)}")
                                
                                # Format the instructions
                                formatted_instructions = []
                                
                                if isinstance(instructions, list):
                                    for i, instruction in enumerate(instructions, 1):
                                        if isinstance(instruction, dict) and 'text' in instruction:
                                            formatted_instructions.append(f"{i}. {instruction['text']}")
                                            logger.info(f"Step {i}: {instruction['text'][:50]}...")
                                        elif isinstance(instruction, str):
                                            formatted_instructions.append(f"{i}. {instruction}")
                                            logger.info(f"Step {i}: {instruction[:50]}...")
                                
                                if formatted_instructions:
                                    return "\n".join(formatted_instructions)
                except Exception as e:
                    logger.warning(f"Error parsing JSON-LD: {str(e)}")
        except Exception as e:
            logger.warning(f"Error extracting JSON-LD data from AllRecipes: {str(e)}")
        
        # Try a more general approach - find a directions section
        logger.info("Trying to find directions section by heading text")
        for heading in soup.find_all(['h2', 'h3', 'h4']):
            heading_text = heading.get_text().lower()
            if "directions" in heading_text or "instructions" in heading_text:
                logger.info(f"Found heading: {heading_text}")
                # Look for ordered lists after the heading
                heading_parent = heading.parent
                ordered_lists = heading_parent.find_all('ol')
                if ordered_lists:
                    steps = []
                    for ol in ordered_lists:
                        items = ol.find_all('li')
                        for i, item in enumerate(items, 1):
                            steps.append(f"{i}. {item.get_text().strip()}")
                    if steps:
                        return "\n".join(steps)
        
        logger.warning("Could not extract instructions from AllRecipes")
        return ""
        
    except Exception as e:
        logger.error(f"Error extracting AllRecipes instructions: {str(e)}")
        return ""

async def test_scrape_allrecipes():
    """Test scraping AllRecipes.com"""
    url = "https://www.allrecipes.com/recipe/228122/herbed-scalloped-potatoes-and-onions/"
    
    logger.info(f"Testing scraping for: {url}")
    
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
                
                # Extract instructions
                instructions = await extract_allrecipes_instructions(soup, html_content)
                
                if instructions:
                    logger.info(f"Successfully extracted instructions ({len(instructions)} characters)")
                    logger.info("Instructions:")
                    logger.info(instructions)
                else:
                    logger.warning("Failed to extract instructions")
                
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_scrape_allrecipes()) 