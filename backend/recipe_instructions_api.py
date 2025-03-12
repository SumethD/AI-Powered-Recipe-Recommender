import os
import re
import json
import time
import logging
from typing import Dict, List, Optional, Union, Any
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException, Request, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import openai
import aiohttp
import asyncio
from recipe_instructions_service import (
    scrape_instructions, 
    generate_instructions_with_ai,
    generate_basic_instructions
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("recipe_instructions_api")

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    logger.warning("OPENAI_API_KEY not set. AI generation will not work.")

# Configuration
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
    recipe_id: Optional[str] = "temp_id"
    recipe_name: str
    source_url: Optional[str] = None
    ingredients: List[str]
    servings: Optional[int] = None
    diets: Optional[List[str]] = []
    cuisine: Optional[str] = None

class RecipeInstructionsResponse(BaseModel):
    recipe_id: str
    instructions: str
    source: str = Field(..., description="Source of instructions: 'scraped' or 'ai-generated'")
    cached: bool = False

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

# OpenAI client provider
def get_openai_client():
    # Get API key from environment variable
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        logger.warning("OPENAI_API_KEY not found in environment variables")
        return None
    
    # For older OpenAI API versions (0.x.x)
    openai.api_key = api_key
    return None

# Main function to get recipe instructions using hybrid approach
@app.post("/api/recipe-instructions", response_model=RecipeInstructionsResponse)
async def get_recipe_instructions(
    request: RecipeInstructionsRequest,
    background_tasks: BackgroundTasks,
) -> RecipeInstructionsResponse:
    """Get recipe instructions from a URL or generate them with AI."""
    # Log the request
    logger.info(f"Received request for recipe instructions: {request.recipe_name}")
    
    # Initialize response
    api_response = RecipeInstructionsResponse(
        recipe_id=request.recipe_id,
        instructions="",
        source="basic",
        cached=False
    )
    
    scrape_result_type = "not_attempted"
    
    try:
        # If URL is provided and valid, try to scrape instructions first
        if request.source_url and request.source_url.startswith(("http://", "https://")):
            try:
                # Use an increased timeout of 10 seconds for scraping
                logger.info(f"Attempting to scrape instructions from: {request.source_url}")
                instructions, scrape_result_type = await asyncio.wait_for(
                    scrape_instructions(request.source_url), 
                    timeout=10.0
                )
                
                if instructions and scrape_result_type == "success":
                    logger.info(f"Successfully scraped instructions for: {request.recipe_name}")
                    api_response.instructions = instructions
                    api_response.source = "scraped"
                    return api_response
                else:
                    logger.warning(f"Scraping failed with result type: {scrape_result_type}. Falling back to AI generation")
            except asyncio.TimeoutError:
                logger.warning(f"Scraping timed out after 10 seconds for URL: {request.source_url}")
                scrape_result_type = "timeout"
            except Exception as e:
                logger.warning(f"Error scraping instructions: {str(e)}")
                scrape_result_type = "error"
        elif request.source_url:
            logger.warning(f"Invalid URL provided: {request.source_url}")
            scrape_result_type = "invalid_url"
        else:
            logger.info("No URL provided, skipping scraping step")
            scrape_result_type = "no_url"
        
        # If we get here, either no URL was provided, or scraping failed, or the timeout occurred
        # Try to generate instructions with AI as a fallback
        logger.info(f"Generating instructions with AI for: {request.recipe_name}")
        
        # Check if OpenAI API key is available
        if not openai.api_key:
            logger.warning("No OpenAI API key available, using basic instructions generator")
            api_response.instructions = generate_basic_instructions(request)
            api_response.source = "basic"
            return api_response
        
        try:
            # Use a higher timeout for AI generation (25 seconds)
            instructions = await asyncio.wait_for(
                generate_instructions_with_ai(request), 
                timeout=25.0
            )
            
            if instructions:
                logger.info(f"Successfully generated AI instructions for: {request.recipe_name}")
                api_response.instructions = instructions
                api_response.source = "ai-generated"
                return api_response
            else:
                logger.warning("AI generated empty instructions")
                # If AI generated empty instructions, use basic fallback
                api_response.instructions = generate_basic_instructions(request)
                api_response.source = "basic"
                return api_response
                
        except asyncio.TimeoutError:
            logger.error("AI generation timed out after 25 seconds")
            # If AI generation times out, use basic fallback
            api_response.instructions = generate_basic_instructions(request)
            api_response.source = "basic"
            return api_response
        except Exception as e:
            logger.error(f"Error generating instructions with AI: {str(e)}")
            # If AI generation fails, use basic fallback
            api_response.instructions = generate_basic_instructions(request)
            api_response.source = "basic"
            return api_response
            
    except Exception as e:
        # This is the final fallback to ensure the API always returns a response
        logger.error(f"Unhandled error in get_recipe_instructions: {str(e)}")
        try:
            # Try to generate basic instructions as a last resort
            api_response.instructions = generate_basic_instructions(request)
            api_response.source = "basic"
        except Exception as inner_e:
            # If even that fails, return a simple message
            logger.error(f"Failed to generate basic instructions: {str(inner_e)}")
            api_response.instructions = f"1. Gather all ingredients for {request.recipe_name}.\n2. Prepare and cook according to standard practices for this type of dish.\n3. Serve and enjoy!"
            api_response.source = "basic"
        
        return api_response 

# Health endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint to verify the API is running."""
    return {"status": "healthy", "service": "recipe-instructions-api"}

if __name__ == "__main__":
    import uvicorn
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Recipe Instructions API")
    parser.add_argument("--port", type=int, default=8003, help="Port to run the server on")
    args = parser.parse_args()
    
    # Use the port from command line or default to 8003
    port = args.port
    logger.info(f"Starting recipe instructions API on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port) 