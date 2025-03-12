"""
Standalone API for AllRecipes instructions
"""
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging
import aiohttp
from bs4 import BeautifulSoup
import re
import json
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("allrecipes_api")

# Create FastAPI app
app = FastAPI(title="AllRecipes API", description="API for extracting recipe instructions from AllRecipes.com")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class RecipeRequest(BaseModel):
    url: str

class RecipeResponse(BaseModel):
    instructions: str

@app.get("/api/health")
async def health_check():
    """Health check endpoint to verify the API is running."""
    return {"status": "healthy", "service": "allrecipes-api"}

@app.post("/api/allrecipes", response_model=RecipeResponse)
async def get_allrecipes_instructions(request: RecipeRequest):
    """
    Extract recipe instructions from an AllRecipes.com URL.
    
    Args:
        request: The request containing the AllRecipes URL
        
    Returns:
        A response containing the extracted instructions
    """
    url = request.url
    
    if not url or not url.startswith("https://www.allrecipes.com/recipe/"):
        logger.error(f"Invalid URL provided: {url}")
        raise HTTPException(status_code=400, detail="Invalid URL. Must be an AllRecipes recipe URL.")
    
    logger.info(f"Processing AllRecipes URL: {url}")
    
    try:
        # Set up headers to mimic a browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0"
        }
        
        # Fetch the page with a timeout
        async with aiohttp.ClientSession() as session:
            logger.info(f"Sending HTTP request to {url}")
            async with session.get(url, headers=headers, timeout=15) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch URL: {url}, status code: {response.status}")
                    raise HTTPException(status_code=502, detail=f"Failed to fetch URL: HTTP {response.status}")
                
                logger.info(f"Successfully fetched URL with status code {response.status}")
                html_content = await response.text()
                
                # Extract instructions using various selectors
                instructions = await extract_instructions(html_content, url)
                
                if not instructions:
                    logger.error(f"Failed to extract instructions from {url}")
                    raise HTTPException(status_code=404, detail="Could not extract instructions from the provided URL")
                
                logger.info(f"Successfully extracted instructions ({len(instructions)} characters)")
                return RecipeResponse(instructions=instructions)
                
    except aiohttp.ClientError as e:
        logger.error(f"Connection error for URL {url}: {str(e)}")
        raise HTTPException(status_code=502, detail=f"Connection error: {str(e)}")
    except asyncio.TimeoutError:
        logger.error(f"Request timed out for URL {url}")
        raise HTTPException(status_code=504, detail="Request timed out")
    except Exception as e:
        logger.error(f"Unexpected error processing {url}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

async def extract_instructions(html_content: str, url: str) -> Optional[str]:
    """
    Extract recipe instructions from HTML content.
    
    Args:
        html_content: The HTML content of the page
        url: The URL of the page (for logging)
        
    Returns:
        The extracted instructions as a string, or None if extraction failed
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    instructions = ""
    
    # Try multiple selectors for instructions
    selectors = [
        ".mntl-sc-block-group--LI",
        ".directions-container .directions__container ol li",
        ".recipe-directions__list--item",
        "[data-testid='recipe-instructions'] li",
        ".component--instructions"
    ]
    
    # Try to extract instructions using various selectors
    for selector in selectors:
        logger.info(f"Trying selector: {selector}")
        elements = soup.select(selector)
        if elements:
            logger.info(f"Found {len(elements)} elements with selector {selector}")
            instructions_list = []
            for i, element in enumerate(elements, 1):
                step_text = element.get_text(strip=True)
                if step_text:
                    instructions_list.append(f"{i}. {step_text}")
            
            if instructions_list:
                instructions = "\n".join(instructions_list)
                logger.info(f"Successfully extracted {len(instructions_list)} steps using selector {selector}")
                break
    
    # If no instructions found with selectors, try to extract from JSON-LD
    if not instructions:
        logger.info("Trying to extract instructions from JSON-LD")
        instructions = extract_from_json_ld(soup)
    
    # If still no instructions, try to find a directions section
    if not instructions:
        logger.info("Trying to find directions section by heading")
        instructions = find_directions_section(soup)
    
    return instructions

def extract_from_json_ld(soup: BeautifulSoup) -> Optional[str]:
    """Extract recipe instructions from JSON-LD structured data."""
    try:
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                
                # Handle both single recipe and array of recipes
                recipes = data if isinstance(data, list) else [data]
                
                for item in recipes:
                    if '@type' in item and item['@type'] in ['Recipe', 'schema:Recipe']:
                        if 'recipeInstructions' in item:
                            instructions = item['recipeInstructions']
                            
                            # Handle different formats of recipeInstructions
                            if isinstance(instructions, list):
                                # Check if it's a list of objects with text property
                                if all(isinstance(step, dict) for step in instructions):
                                    steps = []
                                    for i, step in enumerate(instructions, 1):
                                        if 'text' in step:
                                            steps.append(f"{i}. {step['text']}")
                                    return "\n".join(steps) if steps else None
                                # Check if it's a list of strings
                                elif all(isinstance(step, str) for step in instructions):
                                    return "\n".join(f"{i}. {step}" for i, step in enumerate(instructions, 1))
                            # Handle string format
                            elif isinstance(instructions, str):
                                # Split by newlines or periods followed by space
                                steps = re.split(r'(?:\.\s+|\n+)', instructions)
                                steps = [step.strip() for step in steps if step.strip()]
                                return "\n".join(f"{i}. {step}" for i, step in enumerate(steps, 1))
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON-LD data")
                continue
    except Exception as e:
        logger.warning(f"Error extracting from JSON-LD: {str(e)}")
    
    return None

def find_directions_section(soup: BeautifulSoup) -> Optional[str]:
    """Find directions section by looking for headings like 'Directions' or 'Instructions'."""
    direction_headings = ['directions', 'instructions', 'preparation', 'method', 'steps']
    
    # Look for headings
    for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        heading_text = heading.get_text(strip=True).lower()
        
        if any(dh in heading_text for dh in direction_headings):
            logger.info(f"Found directions heading: {heading_text}")
            
            # Look for ordered list after the heading
            ol = heading.find_next('ol')
            if ol:
                steps = []
                for i, li in enumerate(ol.find_all('li'), 1):
                    step_text = li.get_text(strip=True)
                    if step_text:
                        steps.append(f"{i}. {step_text}")
                
                if steps:
                    return "\n".join(steps)
            
            # If no ordered list, look for paragraphs or divs
            steps = []
            next_elem = heading.find_next_sibling()
            while next_elem and next_elem.name not in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                if next_elem.name in ['p', 'div']:
                    step_text = next_elem.get_text(strip=True)
                    if step_text:
                        steps.append(step_text)
                next_elem = next_elem.find_next_sibling()
            
            if steps:
                return "\n".join(f"{i}. {step}" for i, step in enumerate(steps, 1))
    
    logger.warning("Could not find directions section")
    return None

if __name__ == "__main__":
    import asyncio
    
    uvicorn.run(app, host="0.0.0.0", port=8002) 