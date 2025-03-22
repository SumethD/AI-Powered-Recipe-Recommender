#!/usr/bin/env python3
"""
Test script specifically for the recipe instructions web scraper functionality.
This script tests the scraper with a variety of recipe URLs to verify if instructions are extracted correctly.
"""

import asyncio
import sys
from typing import List, Tuple, Dict
import time

# Import the scraping function from recipe_instructions_api.py
try:
    from recipe_instructions_api import scrape_instructions
    print("Successfully imported scrape_instructions function")
except ImportError:
    print("Failed to import scrape_instructions, trying to import from recipe_instructions_service")
    try:
        from recipe_instructions_service import scrape_instructions
        print("Successfully imported scrape_instructions function from recipe_instructions_service")
    except ImportError:
        print("ERROR: Could not import scrape_instructions function from either module")
        sys.exit(1)

# Test URLs for popular recipe websites
TEST_URLS = [
    # Remaining user-provided recipes to test
    "https://www.allrecipes.com/recipe/142500/menas-baked-macaroni-and-cheese-with-caramelized-onion",
    "http://picturetherecipe.com/index.php/recipes/grilled-honey-chipotle-chicken-drumsticks/",
    
    # Known working sites with different patterns
    "https://www.bbcgoodfood.com/recipes/ultimate-spaghetti-carbonara-recipe",
    "https://www.kingarthurbaking.com/recipes/chocolate-chip-cookies-recipe",
    "https://www.bonappetit.com/recipe/bas-best-chocolate-chip-cookies",
    "https://www.inspiredtaste.net/24412/cocoa-brownies-recipe/",
    "https://sallysbakingaddiction.com/best-banana-bread-recipe/",
    
    # Sites that worked in previous test
    "https://kitchendivas.com/slow-cooker-sweet-chili-thai-pork/",
    "https://www.womensweeklyfood.com.au/recipes/chinese-style-crispy-skin-chicken-19112"
]

async def test_url(url: str) -> Tuple[str, bool, str]:
    """Test a single URL and return the result."""
    print(f"\nTesting URL: {url}")
    start_time = time.time()
    try:
        # Set a maximum timeout of 10 seconds as requested by user
        timeout_seconds = 10
        
        # Use asyncio.wait_for to enforce the timeout
        instructions = await asyncio.wait_for(
            scrape_instructions(url), 
            timeout=timeout_seconds
        )
        
        duration = time.time() - start_time
        if instructions:
            print(f"✅ Successfully scraped instructions ({len(instructions)} chars) in {duration:.2f}s")
            # Format a better preview of the instructions
            preview_lines = instructions.split('\n')[:3]  # Get first 3 lines
            preview = ' '.join([line.strip() for line in preview_lines])
            if len(preview) > 150:
                preview = preview[:147] + "..."
            return url, True, preview
        else:
            print(f"❌ Failed to scrape instructions in {duration:.2f}s")
            return url, False, "No instructions found"
    except asyncio.TimeoutError:
        duration = time.time() - start_time
        print(f"❌ Timed out after {duration:.2f}s (exceeded {timeout_seconds}s limit)")
        return url, False, f"Timed out (exceeded {timeout_seconds}s limit)"
    except Exception as e:
        duration = time.time() - start_time
        print(f"❌ Error occurred during scraping in {duration:.2f}s: {str(e)}")
        return url, False, str(e)

async def test_all_urls() -> Dict[str, Dict]:
    """Test all URLs and collect results."""
    results = {}
    for url in TEST_URLS:
        url, success, message = await test_url(url)
        results[url] = {
            "success": success,
            "message": message
        }
    return results

def print_summary(results: Dict[str, Dict]) -> None:
    """Print a summary of the test results."""
    successful = sum(1 for r in results.values() if r["success"])
    total = len(results)
    
    print("\n" + "="*80)
    print(f"SUMMARY: Successfully scraped {successful}/{total} recipe URLs")
    print("="*80)
    
    print("\nDETAILED RESULTS:")
    for url, result in results.items():
        status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
        print(f"\n{status}: {url}")
        print(f"  {result['message']}")

async def print_full_instructions(url: str) -> None:
    """Print the full instructions for a URL."""
    try:
        instructions = await scrape_instructions(url)
        if instructions:
            # Format the instructions for better readability
            formatted = instructions.replace("\n\n", "\n").strip()
            print(f"\n{formatted[:1000]}")
            if len(instructions) > 1000:
                print("\n... (truncated for brevity) ...")
    except Exception as e:
        print(f"Error retrieving full instructions: {str(e)}")

async def main():
    """Main function."""
    print("🔍 Recipe Instructions Web Scraper Test")
    print("======================================")
    
    results = await test_all_urls()
    print_summary(results)
    
    # Print full instructions for the first successful URL
    if any(r["success"] for r in results.values()):
        success_url = next(url for url, result in results.items() if result["success"])
        print("\n" + "="*80)
        print(f"SAMPLE FULL INSTRUCTIONS FROM: {success_url}")
        print("="*80)
        
        # Get and print the full instructions
        await print_full_instructions(success_url)
    
    # Return success if at least one URL was successfully scraped
    return any(r["success"] for r in results.values())

if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        print("\n❌ All tests failed. The web scraper is not working properly.")
        sys.exit(1)
    else:
        print("\n🎉 Test completed successfully!") 