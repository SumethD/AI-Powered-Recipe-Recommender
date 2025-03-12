"""
Standalone API for recipe instructions
"""
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Tuple
import logging
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class RecipeInstructionsRequest(BaseModel):
    recipe_name: str
    ingredients: List[str]
    recipe_id: Optional[str] = None
    source_url: Optional[str] = None
    servings: Optional[int] = None
    diets: Optional[List[str]] = None
    cuisine: Optional[str] = None

class RecipeInstructionsResponse(BaseModel):
    instructions: str

@app.post("/api/recipe-instructions", response_model=RecipeInstructionsResponse)
async def get_recipe_instructions(request: RecipeInstructionsRequest):
    """Get recipe instructions from a URL or generate basic instructions"""
    logger.info(f"Received request for recipe: {request.recipe_name}")
    logger.info(f"Source URL: {request.source_url}")
    
    try:
        # If URL is provided and valid, try to scrape instructions first
        if request.source_url and request.source_url.startswith(("http://", "https://")):
            try:
                # Use a timeout of 10 seconds for scraping
                logger.info(f"Attempting to scrape instructions from: {request.source_url}")
                instructions, result_type = await asyncio.wait_for(
                    scrape_instructions(request.source_url), 
                    timeout=15.0  # Increased timeout for testing
                )
                
                logger.info(f"Scraping result type: {result_type}")
                logger.info(f"Instructions length: {len(instructions) if instructions else 0} characters")
                
                if instructions and result_type == "success":
                    logger.info(f"Successfully scraped instructions for: {request.recipe_name}")
                    logger.info(f"First 100 chars: {instructions[:100]}...")
                    return RecipeInstructionsResponse(instructions=instructions)
                else:
                    logger.warning(f"Scraping failed with result type: {result_type}. Falling back to basic instructions")
            except asyncio.TimeoutError:
                logger.warning(f"Scraping timed out after 15 seconds for URL: {request.source_url}")
            except Exception as e:
                logger.warning(f"Error scraping instructions: {str(e)}")
                import traceback
                logger.warning(f"Traceback: {traceback.format_exc()}")
        
        # Generate basic instructions as fallback
        logger.info(f"Generating basic instructions for: {request.recipe_name}")
        instructions = generate_basic_instructions(request)
        return RecipeInstructionsResponse(instructions=instructions)
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

async def scrape_instructions(url: str) -> Tuple[str, str]:
    """
    Scrape recipe instructions from a URL.
    Returns a tuple of (instructions, result_type) where result_type is one of:
    - "success": Successfully scraped instructions
    - "timeout": Request timed out
    - "connection_error": Could not connect to the website
    - "parsing_error": Connected but failed to parse content
    - "not_found": Connected but could not find instructions
    """
    logger.info(f"Attempting to scrape instructions from {url}")
    
    try:
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
        
        # Use both connect and read timeouts to ensure responsive scraping
        timeout = aiohttp.ClientTimeout(total=15, connect=5)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            logger.info(f"Sending HTTP request to {url}")
            async with session.get(url, headers=headers, allow_redirects=True) as response:
                logger.info(f"Received response from {url} with status code {response.status}")
                
                if response.status != 200:
                    logger.warning(f"Failed to retrieve page: HTTP {response.status}")
                    return "", "connection_error"
                
                # Read the HTML content
                html_content = await response.text()
                logger.info(f"Retrieved HTML content ({len(html_content)} bytes)")
                
                if not html_content or len(html_content) < 100:
                    logger.warning("Retrieved empty or very small HTML content")
                    return "", "parsing_error"
                
                # Create a BeautifulSoup object
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Try AllRecipes specific extraction first
                if "allrecipes.com" in url:
                    logger.info("Detected AllRecipes.com URL, using specialized extraction")
                    instructions = extract_allrecipes_instructions(soup, html_content)
                    if instructions:
                        logger.info(f"Successfully extracted AllRecipes instructions: {len(instructions)} characters")
                        return instructions, "success"
                    else:
                        logger.warning("Failed to extract AllRecipes instructions")
                
                # Try to extract structured data (JSON-LD)
                try:
                    logger.info("Attempting to extract instructions from structured data")
                    instructions = extract_structured_data_instructions(soup)
                    if instructions:
                        logger.info("Successfully extracted instructions from structured data")
                        return instructions, "success"
                except Exception as e:
                    logger.warning(f"Failed to extract structured data: {str(e)}")
                
                # Try to find recipe instructions using common selectors
                logger.info("Attempting to extract instructions using CSS selectors")
                selectors = [
                    ".recipe-directions__list--item",  # AllRecipes
                    ".instructions-section .section-body",  # Epicurious
                    ".preparation-steps li",  # BBC Good Food
                    ".recipe-method-list li",  # Various sites
                    ".recipe-instructions li",  # Various sites
                    ".recipe__instructions li",  # Several recipe sites
                    ".instruction-item",  # Some cooking sites
                    ".step",  # Step-based instructions
                    ".recipe-steps li",  # Various sites
                    ".recipe__list--steps li",  # Some food blogs
                    ".recipe-instructions ol li",  # Generic
                    ".directions ol li",  # Generic
                    ".method ol li",  # Generic
                    ".instructions ol li",  # Generic
                    "[itemprop='recipeInstructions'] li",  # Schema.org
                    ".recipe-procedure-text",  # NYT Cooking
                ]
                
                for selector in selectors:
                    elements = soup.select(selector)
                    if elements:
                        logger.info(f"Found {len(elements)} instruction elements with selector: {selector}")
                        instructions = "\n".join([f"{i+1}. {element.get_text().strip()}" for i, element in enumerate(elements)])
                        if instructions:
                            return instructions, "success"
                
                # If no selectors match, try to find the section by heading text
                logger.info("Attempting to find instruction section by heading text")
                for heading in soup.find_all(['h2', 'h3', 'h4']):
                    heading_text = heading.get_text().lower()
                    if "instructions" in heading_text or "directions" in heading_text or "method" in heading_text or "preparation" in heading_text:
                        logger.info(f"Found heading: {heading_text}")
                        
                        # Try to find instructions in the next sibling elements
                        instructions_container = None
                        
                        # Check if next element is a list
                        next_element = heading.find_next_sibling()
                        if next_element and next_element.name in ['ol', 'ul']:
                            logger.info("Found list after heading")
                            instructions_container = next_element
                        elif next_element and next_element.name == 'div':
                            # Check for lists inside div
                            lists = next_element.find_all(['ol', 'ul'])
                            if lists:
                                logger.info("Found list inside div after heading")
                                instructions_container = lists[0]
                        
                        if instructions_container:
                            items = instructions_container.find_all('li')
                            if items:
                                instructions = "\n".join([f"{i+1}. {item.get_text().strip()}" for i, item in enumerate(items)])
                                return instructions, "success"
                
                # Last resort: Look for paragraphs that might contain instructions
                logger.info("Checking paragraphs for instructions as last resort")
                paragraphs = soup.find_all('p')
                instruction_paragraphs = []
                
                for p in paragraphs:
                    text = p.get_text().strip()
                    # Look for paragraphs that look like instructions
                    if len(text) > 20 and (
                        text.startswith("1.") or 
                        text.lower().startswith("first") or 
                        re.match(r'^step\s+\d+', text.lower())
                    ):
                        instruction_paragraphs.append(text)
                
                if instruction_paragraphs:
                    logger.info(f"Found {len(instruction_paragraphs)} paragraphs that might contain instructions")
                    instructions = "\n\n".join(instruction_paragraphs)
                    return instructions, "success"
                
                # If we get here, we couldn't extract the instructions
                logger.warning(f"Could not extract instructions from {url}")
                return "", "not_found"
                
    except asyncio.TimeoutError:
        logger.error(f"Timeout while scraping {url}")
        return "", "timeout"
    except aiohttp.ClientConnectorError as e:
        logger.error(f"Connection error while scraping {url}: {str(e)}")
        return "", "connection_error"
    except Exception as e:
        logger.error(f"Error while scraping {url}: {str(e)}")
        return "", "parsing_error"

def extract_structured_data_instructions(soup) -> str:
    """Extract recipe instructions from JSON-LD structured data"""
    # Find all script tags with type application/ld+json
    script_tags = soup.find_all('script', type='application/ld+json')
    
    for script in script_tags:
        try:
            json_data = json.loads(script.string)
            
            # Handle the case when it's a list
            if isinstance(json_data, list):
                for item in json_data:
                    if isinstance(item, dict) and '@type' in item and item['@type'] in ['Recipe', 'recipe']:
                        instructions = extract_instructions_from_json_ld(item)
                        if instructions:
                            return instructions
            
            # Handle single recipe object
            elif isinstance(json_data, dict):
                # Check if it's a Recipe type
                if '@type' in json_data and json_data['@type'] in ['Recipe', 'recipe']:
                    instructions = extract_instructions_from_json_ld(json_data)
                    if instructions:
                        return instructions
                
                # Sometimes recipes are nested in a Graph
                if '@graph' in json_data and isinstance(json_data['@graph'], list):
                    for item in json_data['@graph']:
                        if isinstance(item, dict) and '@type' in item and item['@type'] in ['Recipe', 'recipe']:
                            instructions = extract_instructions_from_json_ld(item)
                            if instructions:
                                return instructions
        except Exception as e:
            logger.warning(f"Error parsing JSON-LD: {str(e)}")
    
    return ""

def extract_instructions_from_json_ld(recipe_json) -> str:
    """Extract instructions from a JSON-LD recipe object"""
    instructions_field = None
    
    # Check for various possible field names
    for field in ['recipeInstructions', 'instructions']:
        if field in recipe_json:
            instructions_field = recipe_json[field]
            break
    
    if not instructions_field:
        return ""
    
    # Handle different formats of recipe instructions
    formatted_instructions = []
    
    # Case 1: Array of objects with text property
    if isinstance(instructions_field, list):
        for i, instruction in enumerate(instructions_field):
            if isinstance(instruction, dict) and 'text' in instruction:
                formatted_instructions.append(f"{i+1}. {instruction['text']}")
            elif isinstance(instruction, str):
                formatted_instructions.append(f"{i+1}. {instruction}")
    
    # Case 2: String with instructions
    elif isinstance(instructions_field, str):
        # Try to split by newlines or numbers
        if '\n' in instructions_field:
            steps = instructions_field.split('\n')
            for i, step in enumerate(steps):
                if step.strip():
                    # Remove existing numbers if present
                    step = re.sub(r'^\d+[\.\)]\s*', '', step.strip())
                    formatted_instructions.append(f"{i+1}. {step}")
        else:
            # If it's a single string, return it as one instruction
            formatted_instructions.append(f"1. {instructions_field}")
    
    return "\n".join(formatted_instructions)

def extract_allrecipes_instructions(soup, html_content) -> str:
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

def generate_basic_instructions(recipe: RecipeInstructionsRequest) -> str:
    """Generate basic cooking instructions based on recipe data"""
    recipe_name = recipe.recipe_name
    
    # Create a basic instructions template
    instructions = f"""
1. Gather all the ingredients for {recipe_name}:
"""
    
    # Add all ingredients
    for i, ingredient in enumerate(recipe.ingredients, 1):
        instructions += f"\n   - {ingredient}"
    
    # Add generic preparation steps
    instructions += f"""

2. Prepare your ingredients by washing, chopping, and measuring as needed.

3. Cook the main ingredients using an appropriate method (baking, frying, boiling, etc.) based on the dish type.

4. Combine ingredients in the order that makes sense for {recipe_name}.

5. Season to taste with salt, pepper, and any herbs or spices that complement the dish.

6. Cook until all ingredients reach a safe internal temperature and desired doneness.

7. Serve and enjoy your {recipe_name}!

Note: These are generic instructions generated as a fallback. For detailed instructions, please check the recipe source or try again later.
"""
    
    return instructions.strip()

if __name__ == "__main__":
    logger.info("Starting standalone recipe instructions API")
    uvicorn.run(app, host="0.0.0.0", port=8001) 