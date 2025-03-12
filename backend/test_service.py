#!/usr/bin/env python3
"""
Test script for the Recipe Instructions Service.
This script sends a test request to the service and prints the response.
"""

import json
import sys
import requests
from pprint import pprint

# Configuration
API_URL = "http://localhost:8000/api/recipe-instructions"
HEALTH_URL = "http://localhost:8000/api/health"

# Test recipe data
test_recipe = {
    "recipe_id": "test-recipe-001",
    "recipe_name": "Simple Pasta with Tomato Sauce",
    "source_url": "https://www.allrecipes.com/recipe/11691/tomato-sauce/",
    "ingredients": [
        "1 pound spaghetti",
        "2 tablespoons olive oil",
        "1 onion, finely chopped",
        "3 cloves garlic, minced",
        "1 (28 ounce) can crushed tomatoes",
        "1 teaspoon dried basil",
        "1 teaspoon dried oregano",
        "1/2 teaspoon salt",
        "1/4 teaspoon black pepper",
        "1/4 teaspoon red pepper flakes (optional)",
        "2 tablespoons fresh parsley, chopped",
        "Grated Parmesan cheese for serving"
    ],
    "servings": 4,
    "cuisine": "Italian",
    "diets": ["vegetarian"]
}

def check_health():
    """Check if the service is running."""
    try:
        response = requests.get(HEALTH_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Service is healthy!")
            return True
        else:
            print(f"❌ Service returned status code {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Could not connect to the service: {e}")
        return False

def test_recipe_instructions():
    """Test the recipe instructions endpoint."""
    print("\n🧪 Testing recipe instructions endpoint...")
    try:
        response = requests.post(API_URL, json=test_recipe, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Successfully received recipe instructions!")
            print("\nResponse Summary:")
            print(f"Recipe ID: {data['recipe_id']}")
            print(f"Source: {data['source']}")
            print(f"Cached: {data['cached']}")
            
            print("\nInstructions Preview (first 200 chars):")
            instructions = data['instructions']
            print(f"{instructions[:200]}...")
            
            print(f"\nTotal Instructions Length: {len(instructions)} characters")
            
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def main():
    """Main function."""
    print("🔍 Recipe Instructions Service Test")
    print("==================================")
    
    if not check_health():
        print("\n❌ Service health check failed. Make sure the service is running.")
        sys.exit(1)
    
    if test_recipe_instructions():
        print("\n🎉 All tests passed successfully!")
    else:
        print("\n❌ Tests failed.")
        sys.exit(1)

if __name__ == "__main__":
    main() 