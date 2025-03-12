import os
import re
import json
import time
import logging
import asyncio
from typing import Dict, List, Optional, Union, Any
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import openai
import aiohttp
import hashlib

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("recipe-instructions-service")

# Initialize FastAPI app
app = FastAPI(title="Recipe Instructions Service")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    logger.warning("OPENAI_API_KEY not set. AI generation will not work.")

# Configuration
PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "0.0.0.0")
CACHE_TTL = int(os.getenv("CACHE_TTL", "86400"))  # 24 hours in seconds
SCRAPING_RATE_LIMIT = int(os.getenv("SCRAPING_RATE_LIMIT", "100"))  # requests per hour
OPENAI_RATE_LIMIT = int(os.getenv("OPENAI_RATE_LIMIT", "20"))  # requests per minute

# In-memory cache
cache: Dict[str, Dict[str, Any]] = {}

# Rate limiting
scraping_requests = []
openai_requests = []


# Models
class RecipeInstructionsRequest(BaseModel):
    recipe_id: str
    recipe_name: str
    source_url: Optional[str] = None
    ingredients: List[str]
    servings: Optional[int] = None
    cuisine: Optional[str] = None
    diets: Optional[List[str]] = None


class RecipeInstructionsResponse(BaseModel):
    recipe_id: str
    instructions: str
    source: str = Field(..., description="Source of instructions: 'scraped' or 'ai-generated'")
    cached: bool = False


# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    path = request.url.path
    
    # Only apply rate limiting to specific endpoints
    if path == "/api/recipe-instructions":
        # Clean up old requests
        current_time = time.time()
        global scraping_requests, openai_requests
        scraping_requests = [t for t in scraping_requests if current_time - t < 3600]  # 1 hour
        openai_requests = [t for t in openai_requests if current_time - t < 60]  # 1 minute
        
        # Check rate limits
        if len(scraping_requests) >= SCRAPING_RATE_LIMIT:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded for scraping. Try again later."},
            )
        
        if len(openai_requests) >= OPENAI_RATE_LIMIT:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded for AI generation. Try again later."},
            )
        
        # Add current request timestamp
        scraping_requests.append(current_time)
        openai_requests.append(current_time)
    
    response = await call_next(request)
    return response


# Cache management
def get_from_cache(recipe_id: str) -> Optional[Dict[str, Any]]:
    """Get recipe instructions from cache if available and not expired."""
    if recipe_id in cache:
        entry = cache[recipe_id]
        if time.time() - entry["timestamp"] < CACHE_TTL:
            return entry
        else:
            # Remove expired entry
            del cache[recipe_id]
    return None


def add_to_cache(recipe_id: str, instructions: str, source: str) -> None:
    """Add recipe instructions to cache."""
    cache[recipe_id] = {
        "instructions": instructions,
        "source": source,
        "timestamp": time.time(),
    }


# Web scraping functions
async def scrape_instructions(url: str) -> tuple[str, str]:
    """
    Scrape recipe instructions from a URL.
    Returns a tuple of (instructions, result_type) where result_type is one of:
    - "success": Successfully scraped instructions
    - "timeout": Request timed out
    - "connection_error": Could not connect to the website
    - "parsing_error": Connected but failed to parse content
    - "not_found": Connected but could not find instructions
    """
    logger.info(f"=== SCRAPE DEBUG === Attempting to scrape instructions from {url}")
    
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
        timeout = aiohttp.ClientTimeout(total=15, connect=5)  # Increased timeouts
        
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                logger.info(f"=== SCRAPE DEBUG === Sending HTTP request to {url}")
                async with session.get(url, headers=headers, allow_redirects=True) as response:
                    logger.info(f"=== SCRAPE DEBUG === Received response from {url} with status code {response.status}")
                    
                    if response.status != 200:
                        logger.warning(f"=== SCRAPE DEBUG === Failed to retrieve page: HTTP {response.status}")
                        return "", "connection_error"
                    
                    # Read the HTML content
                    html_content = await response.text()
                    logger.info(f"=== SCRAPE DEBUG === Retrieved HTML content ({len(html_content)} bytes)")
                    
                    if not html_content or len(html_content) < 100:
                        logger.warning("=== SCRAPE DEBUG === Retrieved empty or very small HTML content")
                        return "", "parsing_error"
                    
                    # Try to extract the recipe instructions
                    # First, try to extract using the specialized AllRecipes function if it's an AllRecipes URL
                    if "allrecipes.com" in url:
                        logger.info(f"=== SCRAPE DEBUG === URL is from AllRecipes, using specialized extractor")
                        try:
                            soup = BeautifulSoup(html_content, "html.parser")
                            instructions = extract_allrecipes_instructions(soup, html_content)
                            if instructions:
                                logger.info(f"=== SCRAPE DEBUG === Successfully extracted AllRecipes instructions ({len(instructions)} chars)")
                                return instructions, "success"
                            else:
                                logger.warning(f"=== SCRAPE DEBUG === Failed to extract AllRecipes instructions")
                        except Exception as e:
                            logger.error(f"=== SCRAPE DEBUG === Error extracting AllRecipes instructions: {str(e)}")
                    
                    # If we get here, either it's not an AllRecipes URL or the AllRecipes extractor failed
                    # Try to extract structured data (JSON-LD)
                    try:
                        logger.info("=== SCRAPE DEBUG === Attempting to extract instructions from structured data")
                        soup = BeautifulSoup(html_content, "html.parser")
                        instructions = extract_structured_data_instructions(soup)
                        if instructions:
                            logger.info(f"=== SCRAPE DEBUG === Successfully extracted instructions from structured data ({len(instructions)} chars)")
                            return instructions, "success"
                        else:
                            logger.warning("=== SCRAPE DEBUG === No instructions found in structured data")
                    except Exception as e:
                        logger.warning(f"=== SCRAPE DEBUG === Failed to extract structured data: {str(e)}")
                    
                    # Try generic selectors
                    logger.info("=== SCRAPE DEBUG === Attempting generic CSS selectors")
                    if not soup:
                        soup = BeautifulSoup(html_content, "html.parser")
                    
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
                        try:
                            logger.info(f"=== SCRAPE DEBUG === Trying selector: {selector}")
                            elements = soup.select(selector)
                            if elements:
                                steps = [el.get_text().strip() for el in elements if el.get_text().strip()]
                                if steps:
                                    logger.info(f"=== SCRAPE DEBUG === Found {len(steps)} steps with selector '{selector}'")
                                    # Format steps nicely
                                    instructions_text = "\n\n".join([f"{i+1}. {step}" for i, step in enumerate(steps)])
                                    if len(instructions_text) > 50:  # Reasonable minimum length
                                        return instructions_text, "success"
                                else:
                                    logger.info(f"=== SCRAPE DEBUG === Selector '{selector}' found elements but no text content")
                            else:
                                logger.info(f"=== SCRAPE DEBUG === Selector '{selector}' found no elements")
                        except Exception as e:
                            logger.warning(f"=== SCRAPE DEBUG === Error with selector '{selector}': {str(e)}")
                    
                    # If we get here, we failed to extract instructions using all methods
                    logger.warning("=== SCRAPE DEBUG === Failed to extract instructions using all methods")
                    return "", "not_found"
        except asyncio.TimeoutError:
            logger.warning(f"=== SCRAPE DEBUG === Request to {url} timed out")
            return "", "timeout"
        except aiohttp.ClientError as e:
            logger.warning(f"=== SCRAPE DEBUG === Connection error for {url}: {str(e)}")
            return "", "connection_error"
    except Exception as e:
        logger.error(f"=== SCRAPE DEBUG === Unexpected error scraping {url}: {str(e)}")
        import traceback
        logger.error(f"=== SCRAPE DEBUG === Traceback: {traceback.format_exc()}")
        return "", "error"


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


def extract_allrecipes_instructions(soup: BeautifulSoup, html_content: str) -> Optional[str]:
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
            # AllRecipes often has recipe data in a JSON-LD format
            structured_instructions = extract_structured_data_instructions(soup)
            if structured_instructions:
                logger.info("Successfully extracted instructions from JSON-LD data")
                return structured_instructions
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
        return None
        
    except Exception as e:
        logger.error(f"Error extracting AllRecipes instructions: {str(e)}")
        return None


async def generate_instructions_with_ai(recipe_data: RecipeInstructionsRequest) -> str:
    """Generate cooking instructions using OpenAI API."""
    try:
        logger.info("=== AI DEBUG === Starting OpenAI instructions generation")
        if not openai.api_key:
            logger.error("=== AI DEBUG === OpenAI API key not configured")
            return generate_basic_instructions(recipe_data)
        
        # Prepare the prompt with rich context
        ingredients_text = "\n".join([f"- {ingredient}" for ingredient in recipe_data.ingredients])
        
        diets_text = ""
        if recipe_data.diets and len(recipe_data.diets) > 0:
            diets_text = f"This recipe should be suitable for the following dietary preferences: {', '.join(recipe_data.diets)}."
        
        servings_text = ""
        if recipe_data.servings:
            servings_text = f"This recipe serves {recipe_data.servings} people."
        
        cuisine_text = ""
        if recipe_data.cuisine:
            cuisine_text = f"This is a {recipe_data.cuisine} recipe."
        
        # Enhanced prompt for better instructions
        prompt = f"""
        Create detailed cooking instructions for "{recipe_data.recipe_name}".
        
        INGREDIENTS:
        {ingredients_text}
        
        {servings_text}
        {cuisine_text}
        {diets_text}
        
        Please provide comprehensive, step-by-step numbered instructions for preparing this dish. Include:
        
        1. Preparation steps (chopping, measuring, marinating, etc.)
        2. Cooking steps with precise times and temperatures
        3. Special techniques or tips for best results
        4. Final presentation and serving suggestions
        
        Format each step as a clear instruction, and ensure the steps flow logically from start to finish.
        Number each step for clarity.
        """
        
        logger.info("=== AI DEBUG === Prepared OpenAI prompt")
        
        # Limit rate of OpenAI requests by checking recent request timestamps
        now = datetime.now()
        clean_old_requests(openai_requests, 60)  # Clean requests older than 60 seconds
        
        # Count requests in the last minute
        recent_count = len(openai_requests)
        if recent_count >= OPENAI_RATE_LIMIT:
            logger.warning(f"=== AI DEBUG === OpenAI rate limit reached ({recent_count} requests in the last minute)")
            oldest_request = openai_requests[0]
            seconds_to_wait = 60 - (now - oldest_request).total_seconds()
            if seconds_to_wait > 0:
                logger.info(f"=== AI DEBUG === Waiting {seconds_to_wait:.1f} seconds before next OpenAI request")
                await asyncio.sleep(seconds_to_wait)
        
        # Add this request to the list
        openai_requests.append(now)
        
        # Try different models in order of preference
        models = ["gpt-3.5-turbo", "text-davinci-003"]
        logger.info(f"=== AI DEBUG === Will try models in order: {', '.join(models)}")
        
        for model in models:
            try:
                logger.info(f"=== AI DEBUG === Attempting to use model: {model}")
                
                instructions = ""
                
                if model == "gpt-3.5-turbo" or model.startswith("gpt-4"):
                    # Use the chat completions endpoint for GPT-3.5 and GPT-4
                    logger.info(f"=== AI DEBUG === Using chat completions for {model}")
                    response = await asyncio.wait_for(
                        aiohttp.post(
                            "https://api.openai.com/v1/chat/completions",
                            headers={
                                "Authorization": f"Bearer {openai.api_key}",
                                "Content-Type": "application/json"
                            },
                            json={
                                "model": model,
                                "messages": [
                                    {"role": "system", "content": "You are a professional chef who creates clear, detailed cooking instructions."},
                                    {"role": "user", "content": prompt}
                                ],
                                "temperature": 0.7,
                                "max_tokens": 1000
                            }
                        ),
                        timeout=25.0
                    )
                    
                    if response.status == 200:
                        response_data = await response.json()
                        logger.info(f"=== AI DEBUG === Received response from OpenAI chat API")
                        if response_data.get("choices") and len(response_data["choices"]) > 0:
                            content = response_data["choices"][0]["message"]["content"].strip()
                            if content:
                                instructions = content
                    else:
                        error_text = await response.text()
                        logger.error(f"=== AI DEBUG === OpenAI API error: {response.status}, {error_text}")
                        
                else:
                    # Use the completions endpoint for older models
                    logger.info(f"=== AI DEBUG === Using completions for {model}")
                    response = await asyncio.wait_for(
                        aiohttp.post(
                            "https://api.openai.com/v1/completions",
                            headers={
                                "Authorization": f"Bearer {openai.api_key}",
                                "Content-Type": "application/json"
                            },
                            json={
                                "model": model,
                                "prompt": prompt,
                                "temperature": 0.7,
                                "max_tokens": 1000
                            }
                        ),
                        timeout=25.0
                    )
                    
                    if response.status == 200:
                        response_data = await response.json()
                        logger.info(f"=== AI DEBUG === Received response from OpenAI completions API")
                        if response_data.get("choices") and len(response_data["choices"]) > 0:
                            content = response_data["choices"][0]["text"].strip()
                            if content:
                                instructions = content
                    else:
                        error_text = await response.text()
                        logger.error(f"=== AI DEBUG === OpenAI API error: {response.status}, {error_text}")
                
                if instructions:
                    # Ensure instructions are properly formatted with numbers
                    if not re.search(r'^\d+\.', instructions.split('\n')[0].strip()):
                        # If AI didn't number the steps, let's format them
                        logger.info(f"=== AI DEBUG === Formatting unnumbered steps from OpenAI response")
                        steps = re.split(r'\n\s*\n', instructions)
                        formatted_steps = []
                        step_num = 1
                        for step in steps:
                            if step.strip():
                                # Remove any existing numbers and add our own
                                step = re.sub(r'^\d+\.\s*', '', step.strip())
                                formatted_steps.append(f"{step_num}. {step}")
                                step_num += 1
                        instructions = "\n\n".join(formatted_steps)
                    
                    logger.info(f"=== AI DEBUG === Successfully generated instructions with OpenAI model: {model}")
                    return instructions
                else:
                    logger.warning(f"=== AI DEBUG === Empty response from OpenAI model: {model}")
                
            except Exception as model_error:
                logger.warning(f"=== AI DEBUG === Failed to use model {model}: {str(model_error)}")
                # Continue to the next model
        
        # If we've tried all models and none worked, use basic instructions
        logger.warning("=== AI DEBUG === All OpenAI model attempts failed, falling back to basic instructions")
        return generate_basic_instructions(recipe_data)
        
    except asyncio.TimeoutError:
        logger.error("=== AI DEBUG === OpenAI API request timed out after 25 seconds")
        # Provide fallback basic instructions based on recipe name and ingredients
        return generate_basic_instructions(recipe_data)
    except Exception as e:
        logger.error(f"=== AI DEBUG === Error generating instructions with AI: {str(e)}")
        import traceback
        logger.error(f"=== AI DEBUG === Traceback: {traceback.format_exc()}")
        return generate_basic_instructions(recipe_data)


def generate_basic_instructions(recipe_data: RecipeInstructionsRequest) -> str:
    """
    Generate basic cooking instructions when AI generation fails.
    This is a last-resort fallback to ensure users always get some instructions.
    """
    logger.info("Generating basic instructions as fallback")
    recipe_name = recipe_data.recipe_name
    
    # Create a basic instructions template
    instructions = f"""
1. Gather all the ingredients for {recipe_name}:
"""
    
    # Add all ingredients
    for i, ingredient in enumerate(recipe_data.ingredients, 1):
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


# Main function to get recipe instructions using hybrid approach
async def get_recipe_instructions(recipe_data: RecipeInstructionsRequest) -> RecipeInstructionsResponse:
    """
    Get cooking instructions for a recipe using a hybrid approach with priority:
    1. FIRST TRY: Scrape instructions from the provided URL
    2. IF SCRAPING FAILS: Use OpenAI API to generate instructions
    3. LAST RESORT: Use basic instructions generator if both scraping and AI generation fail
    """
    try:
        # Log start of request
        logger.info(f"Processing recipe instruction request for: {recipe_data.recipe_name} (ID: {recipe_data.recipe_id})")
        if recipe_data.source_url:
            logger.info(f"Source URL provided: {recipe_data.source_url}")
        
        # Check cache first
        cached_data = get_from_cache(recipe_data.recipe_id)
        if cached_data:
            logger.info(f"Cache hit for recipe ID: {recipe_data.recipe_id}")
            return RecipeInstructionsResponse(
                recipe_id=recipe_data.recipe_id,
                instructions=cached_data["instructions"],
                source=cached_data["source"],
                cached=True,
            )
        
        # Try to scrape instructions if source URL is provided
        instructions = None
        source = "ai-generated"
        
        # PRIORITY #1: Try to scrape instructions from the URL
        if recipe_data.source_url:
            try:
                # Try scraping with better error handling
                logger.info(f"PRIORITY #1: Attempting to scrape instructions from: {recipe_data.source_url}")
                
                # Use our updated scraping function with error types
                instructions, result_type = await scrape_instructions(recipe_data.source_url)
                
                if instructions:
                    source = "scraped"
                    logger.info(f"SUCCESS: Scraped instructions for {recipe_data.recipe_name} from {recipe_data.source_url}")
                else:
                    logger.warning(f"SCRAPING FAILED with result: {result_type}")
                    logger.warning(f"Falling back to AI generation for {recipe_data.recipe_name}")
            except Exception as e:
                logger.error(f"SCRAPING ERROR for {recipe_data.source_url}: {str(e)}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                # Continue to AI generation
        else:
            logger.info("No source URL provided, will use AI generation directly")
        
        # PRIORITY #2: Fall back to AI generation if scraping failed or no URL provided
        if not instructions:
            logger.info(f"PRIORITY #2: Generating AI instructions for {recipe_data.recipe_name}")
            try:
                instructions = await generate_instructions_with_ai(recipe_data)
                if instructions:
                    logger.info("SUCCESS: Generated instructions with AI")
                else:
                    logger.error("AI generated empty instructions, falling back to basic instructions")
                    instructions = generate_basic_instructions(recipe_data)
                    source = "basic"
            except Exception as e:
                logger.error(f"AI GENERATION ERROR: {str(e)}")
                # PRIORITY #3: Generate basic instructions as a final fallback
                logger.info("PRIORITY #3: Generating basic instructions as final fallback")
                instructions = generate_basic_instructions(recipe_data)
                source = "basic"
                logger.info("Generated basic instructions as fallback")
        
        # Cache the result
        add_to_cache(recipe_data.recipe_id, instructions, source)
        
        # Return the response
        return RecipeInstructionsResponse(
            recipe_id=recipe_data.recipe_id,
            instructions=instructions,
            source=source,
            cached=False,
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_recipe_instructions: {str(e)}")
        # If anything unexpected happens, return basic instructions
        return RecipeInstructionsResponse(
            recipe_id=recipe_data.recipe_id,
            instructions=generate_basic_instructions(recipe_data),
            source="basic",
            cached=False,
        )


# API endpoints
@app.post("/api/recipe-instructions", response_model=RecipeInstructionsResponse)
async def get_recipe_instructions_handler(recipe_data: RecipeInstructionsRequest):
    """Get cooking instructions for a recipe."""
    try:
        # Call the actual implementation function
        return await get_recipe_instructions(recipe_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )


def extract_recipe_name_from_url(url: str) -> str:
    """
    Extract a recipe name from a URL.
    
    Args:
        url: URL of the recipe
        
    Returns:
        A readable recipe name extracted from the URL
    """
    try:
        # Remove protocol and domain
        path = url.split('//')[1].split('/')[1:]
        
        # Look for keywords in the path that might indicate a recipe name
        recipe_segments = []
        for segment in path:
            # Skip common non-recipe segments
            if segment.lower() in ['recipe', 'recipes', 'food', 'cooking', 'www.allrecipes.com']:
                continue
                
            # Extract potential recipe name from segments
            if segment and not segment.isdigit() and len(segment) > 3:
                # Replace hyphens and underscores with spaces
                cleaned = segment.replace('-', ' ').replace('_', ' ')
                recipe_segments.append(cleaned)
        
        if recipe_segments:
            # Use the last meaningful segment as the recipe name
            recipe_name = recipe_segments[-1].title()
            return recipe_name
        else:
            # If no meaningful segments found, use a generic name
            return "Recipe"
            
    except Exception as e:
        logger.error(f"Error extracting recipe name from URL: {str(e)}")
        return "Recipe"


# Only run the app directly if this script is executed directly (not imported)
if __name__ == "__main__":
    import uvicorn
    print(f"Starting Recipe Instructions Service on http://{HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT) 