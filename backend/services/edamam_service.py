import os
import logging
import requests
import json
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure API key
EDAMAM_APP_ID = os.getenv("EDAMAM_APP_ID", "test_app_id")
EDAMAM_API_KEY = os.getenv("EDAMAM_API_KEY", "0122383f3fdc2f5e06169fcc935c550a")  # Use the provided key as default
print(f"Using Edamam API key: {EDAMAM_API_KEY}")
print(f"Using Edamam APP ID: {EDAMAM_APP_ID}")
BASE_URL = "https://api.edamam.com/api/recipes/v2"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample recipes for fallback
SAMPLE_RECIPES = [
    {
        "id": "sample1",
        "title": "Simple Pasta with Tomato Sauce",
        "image": "https://www.edamam.com/web-img/a29/a293566f53abc01f4715925c5ada6e7a.jpg",
        "sourceUrl": "https://www.example.com/pasta-recipe",
        "sourceName": "Sample Recipes",
        "readyInMinutes": 30,
        "servings": 4,
        "healthScore": 80,
        "spoonacularScore": 90,
        "pricePerServing": 2.5,
        "diets": ["balanced"],
        "cuisines": ["Italian"],
        "dishTypes": ["main course"],
        "extendedIngredients": [
            {
                "id": 1,
                "name": "pasta",
                "amount": 400,
                "unit": "g",
                "original": "400g pasta"
            },
            {
                "id": 2,
                "name": "tomato sauce",
                "amount": 500,
                "unit": "ml",
                "original": "500ml tomato sauce"
            },
            {
                "id": 3,
                "name": "olive oil",
                "amount": 2,
                "unit": "tbsp",
                "original": "2 tbsp olive oil"
            },
            {
                "id": 4,
                "name": "garlic",
                "amount": 2,
                "unit": "cloves",
                "original": "2 cloves garlic, minced"
            },
            {
                "id": 5,
                "name": "basil",
                "amount": 1,
                "unit": "handful",
                "original": "1 handful fresh basil leaves"
            },
            {
                "id": 6,
                "name": "parmesan",
                "amount": 50,
                "unit": "g",
                "original": "50g grated parmesan"
            }
        ],
        "summary": "A simple and delicious pasta dish with tomato sauce, garlic, and fresh basil.",
        "instructions": "1. Cook pasta according to package instructions. 2. In a pan, heat olive oil and sauté garlic until fragrant. 3. Add tomato sauce and simmer for 10 minutes. 4. Drain pasta and mix with sauce. 5. Garnish with fresh basil and grated parmesan.",
        "nutrition": {
            "nutrients": [
                {
                    "name": "Calories",
                    "amount": 450,
                    "unit": "kcal",
                    "percentOfDailyNeeds": 22.5
                }
            ]
        }
    },
    {
        "id": "sample2",
        "title": "Chicken Stir Fry",
        "image": "https://www.edamam.com/web-img/5f5/5f51c89f832d50da2df035478d5b7d0c.jpg",
        "sourceUrl": "https://www.example.com/chicken-stir-fry",
        "sourceName": "Sample Recipes",
        "readyInMinutes": 25,
        "servings": 4,
        "healthScore": 85,
        "spoonacularScore": 92,
        "pricePerServing": 3.0,
        "diets": ["high-protein"],
        "cuisines": ["Asian"],
        "dishTypes": ["main course"],
        "extendedIngredients": [
            {
                "id": 1,
                "name": "chicken breast",
                "amount": 500,
                "unit": "g",
                "original": "500g chicken breast, sliced"
            },
            {
                "id": 2,
                "name": "bell peppers",
                "amount": 2,
                "unit": "",
                "original": "2 bell peppers, sliced"
            },
            {
                "id": 3,
                "name": "broccoli",
                "amount": 1,
                "unit": "head",
                "original": "1 head broccoli, cut into florets"
            },
            {
                "id": 4,
                "name": "soy sauce",
                "amount": 3,
                "unit": "tbsp",
                "original": "3 tbsp soy sauce"
            },
            {
                "id": 5,
                "name": "garlic",
                "amount": 3,
                "unit": "cloves",
                "original": "3 cloves garlic, minced"
            },
            {
                "id": 6,
                "name": "ginger",
                "amount": 1,
                "unit": "tbsp",
                "original": "1 tbsp grated ginger"
            },
            {
                "id": 7,
                "name": "vegetable oil",
                "amount": 2,
                "unit": "tbsp",
                "original": "2 tbsp vegetable oil"
            }
        ],
        "summary": "A quick and healthy chicken stir fry with colorful vegetables and a savory sauce.",
        "instructions": "1. Heat oil in a wok or large frying pan. 2. Add chicken and cook until browned. 3. Add garlic and ginger, stir for 30 seconds. 4. Add vegetables and stir fry for 5 minutes. 5. Add soy sauce and cook for another 2 minutes. 6. Serve hot with rice.",
        "nutrition": {
            "nutrients": [
                {
                    "name": "Calories",
                    "amount": 320,
                    "unit": "kcal",
                    "percentOfDailyNeeds": 16
                }
            ]
        }
    }
]

def get_recipes_by_ingredients(ingredients, number=10):
    """
    Get recipes based on a list of ingredients.
    
    Args:
        ingredients (list): List of ingredients
        number (int, optional): Number of results to return. Defaults to 10.
    
    Returns:
        list: List of recipe objects
    """
    try:
        logger.info(f"Searching for recipes with ingredients: {ingredients}")
        
        # Check if API key is available
        if not EDAMAM_API_KEY:
            logger.error("Edamam API key not found")
            logger.info("Using sample recipes as fallback")
            return random.sample(SAMPLE_RECIPES, min(number, len(SAMPLE_RECIPES)))
        
        # Prepare the API endpoint and parameters
        params = {
            "type": "public",
            "app_id": EDAMAM_APP_ID,
            "app_key": EDAMAM_API_KEY,
            "q": " ".join(ingredients),
            "random": "true",
        }
        
        # Make the API request
        logger.info(f"Making request to Edamam API: {BASE_URL}")
        response = requests.get(BASE_URL, params=params)
        
        # Log the response status code
        logger.info(f"Response status code: {response.status_code}")
        
        # If the response is not successful, log the response content
        if response.status_code != 200:
            logger.error(f"Error response: {response.text}")
            logger.info("Using sample recipes as fallback")
            return random.sample(SAMPLE_RECIPES, min(number, len(SAMPLE_RECIPES)))
        
        # Parse and return the results
        data = response.json()
        hits = data.get("hits", [])
        recipes = []
        
        for hit in hits[:number]:  # Limit to requested number
            recipe = hit.get("recipe", {})
            
            # Transform to match our expected format
            transformed_recipe = {
                "id": recipe.get("uri", "").split("_")[-1],  # Extract ID from URI
                "title": recipe.get("label", ""),
                "image": recipe.get("image", ""),
                "sourceUrl": recipe.get("url", ""),
                "sourceName": recipe.get("source", ""),
                "readyInMinutes": recipe.get("totalTime", 0),
                "servings": recipe.get("yield", 0),
                "healthScore": 0,  # Not directly available
                "spoonacularScore": 0,  # Not available
                "pricePerServing": 0,  # Not available
                "diets": recipe.get("dietLabels", []),
                "cuisines": recipe.get("cuisineType", []),
                "dishTypes": recipe.get("dishType", []),
                "extendedIngredients": [
                    {
                        "id": i,
                        "name": ingredient.get("food", ""),
                        "amount": ingredient.get("quantity", 0),
                        "unit": ingredient.get("measure", ""),
                        "original": ingredient.get("text", "")
                    }
                    for i, ingredient in enumerate(recipe.get("ingredients", []))
                ],
                "summary": ", ".join(recipe.get("ingredientLines", [])),
                "instructions": "",  # Not directly available in basic response
                "nutrition": {
                    "nutrients": [
                        {
                            "name": "Calories",
                            "amount": recipe.get("calories", 0),
                            "unit": "kcal",
                            "percentOfDailyNeeds": 0
                        }
                    ]
                }
            }
            
            recipes.append(transformed_recipe)
        
        logger.info(f"Found {len(recipes)} recipes")
        return recipes
        
    except Exception as e:
        logger.error(f"Error in get_recipes_by_ingredients: {str(e)}")
        logger.info("Using sample recipes as fallback due to error")
        return random.sample(SAMPLE_RECIPES, min(number, len(SAMPLE_RECIPES)))

def get_recipe_details(recipe_id):
    """
    Get detailed information about a specific recipe.
    
    Args:
        recipe_id (str): The ID of the recipe
    
    Returns:
        dict: Recipe details
    """
    try:
        logger.info(f"Getting details for recipe ID: {recipe_id}")
        
        # Check if it's a sample recipe
        for recipe in SAMPLE_RECIPES:
            if recipe["id"] == recipe_id:
                logger.info(f"Found sample recipe with ID: {recipe_id}")
                return recipe
        
        # Prepare the API endpoint and parameters
        uri = f"http://www.edamam.com/ontologies/edamam.owl#recipe_{recipe_id}"
        params = {
            "type": "public",
            "app_id": EDAMAM_APP_ID,
            "app_key": EDAMAM_API_KEY,
            "uri": uri,
        }
        
        # Make the API request
        response = requests.get(BASE_URL, params=params)
        
        # Log the response status code
        logger.info(f"Response status code: {response.status_code}")
        
        # If the response is not successful, log the response content
        if response.status_code != 200:
            logger.error(f"Error response: {response.text}")
            logger.info("Using sample recipe as fallback")
            return SAMPLE_RECIPES[0]  # Return the first sample recipe as fallback
        
        # Parse and return the results
        data = response.json()
        hits = data.get("hits", [])
        
        if not hits:
            logger.error(f"Recipe with ID {recipe_id} not found")
            logger.info("Using sample recipe as fallback")
            return SAMPLE_RECIPES[0]  # Return the first sample recipe as fallback
        
        recipe = hits[0].get("recipe", {})
        
        # Transform to match our expected format
        transformed_recipe = {
            "id": recipe_id,
            "title": recipe.get("label", ""),
            "image": recipe.get("image", ""),
            "sourceUrl": recipe.get("url", ""),
            "sourceName": recipe.get("source", ""),
            "readyInMinutes": recipe.get("totalTime", 0),
            "servings": recipe.get("yield", 0),
            "healthScore": 0,  # Not directly available
            "spoonacularScore": 0,  # Not available
            "pricePerServing": 0,  # Not available
            "diets": recipe.get("dietLabels", []),
            "cuisines": recipe.get("cuisineType", []),
            "dishTypes": recipe.get("dishType", []),
            "extendedIngredients": [
                {
                    "id": i,
                    "name": ingredient.get("food", ""),
                    "amount": ingredient.get("quantity", 0),
                    "unit": ingredient.get("measure", ""),
                    "original": ingredient.get("text", "")
                }
                for i, ingredient in enumerate(recipe.get("ingredients", []))
            ],
            "summary": ", ".join(recipe.get("ingredientLines", [])),
            "instructions": "",  # Not directly available in basic response
            "nutrition": {
                "nutrients": [
                    {
                        "name": "Calories",
                        "amount": recipe.get("calories", 0),
                        "unit": "kcal",
                        "percentOfDailyNeeds": 0
                    }
                ]
            }
        }
        
        logger.info(f"Successfully retrieved details for recipe: {transformed_recipe.get('title', 'Unknown')}")
        return transformed_recipe
        
    except Exception as e:
        logger.error(f"Error in get_recipe_details: {str(e)}")
        logger.info("Using sample recipe as fallback due to error")
        return SAMPLE_RECIPES[0]  # Return the first sample recipe as fallback

def search_recipes(query, cuisine="", diet="", intolerances="", number=10):
    """
    Search for recipes by query with optional filters.
    
    Args:
        query (str): Search query
        cuisine (str, optional): Cuisine type. Defaults to "".
        diet (str, optional): Diet restriction. Defaults to "".
        intolerances (str, optional): Food intolerances. Defaults to "".
        number (int, optional): Number of results to return. Defaults to 10.
    
    Returns:
        list: List of recipe objects
    """
    try:
        logger.info(f"Searching for recipes with query: {query}")
        
        # Check if API key is available
        if not EDAMAM_API_KEY:
            logger.error("Edamam API key not found")
            logger.info("Using sample recipes as fallback")
            return random.sample(SAMPLE_RECIPES, min(number, len(SAMPLE_RECIPES)))
        
        # Prepare the API endpoint and parameters
        params = {
            "type": "public",
            "app_id": EDAMAM_APP_ID,
            "app_key": EDAMAM_API_KEY,
            "q": query,
            "random": "true",
        }
        
        # Add optional filters if provided
        if cuisine:
            params["cuisineType"] = cuisine
        if diet:
            params["diet"] = diet
        if intolerances:
            # Edamam uses health parameter for intolerances
            # Format: health=peanut-free, etc.
            intolerances_list = intolerances.split(',')
            health_params = []
            for intolerance in intolerances_list:
                health_params.append(f"{intolerance.strip().lower()}-free")
            params["health"] = health_params
        
        # Make the API request
        logger.info(f"Making request to Edamam API: {BASE_URL}")
        response = requests.get(BASE_URL, params=params)
        
        # Log the response status code
        logger.info(f"Response status code: {response.status_code}")
        
        # If the response is not successful, log the response content
        if response.status_code != 200:
            logger.error(f"Error response: {response.text}")
            logger.info("Using sample recipes as fallback")
            return random.sample(SAMPLE_RECIPES, min(number, len(SAMPLE_RECIPES)))
        
        # Parse and return the results
        data = response.json()
        hits = data.get("hits", [])
        recipes = []
        
        for hit in hits[:number]:  # Limit to requested number
            recipe = hit.get("recipe", {})
            
            # Transform to match our expected format
            transformed_recipe = {
                "id": recipe.get("uri", "").split("_")[-1],  # Extract ID from URI
                "title": recipe.get("label", ""),
                "image": recipe.get("image", ""),
                "sourceUrl": recipe.get("url", ""),
                "sourceName": recipe.get("source", ""),
                "readyInMinutes": recipe.get("totalTime", 0),
                "servings": recipe.get("yield", 0),
                "healthScore": 0,  # Not directly available
                "spoonacularScore": 0,  # Not available
                "pricePerServing": 0,  # Not available
                "diets": recipe.get("dietLabels", []),
                "cuisines": recipe.get("cuisineType", []),
                "dishTypes": recipe.get("dishType", []),
                "extendedIngredients": [
                    {
                        "id": i,
                        "name": ingredient.get("food", ""),
                        "amount": ingredient.get("quantity", 0),
                        "unit": ingredient.get("measure", ""),
                        "original": ingredient.get("text", "")
                    }
                    for i, ingredient in enumerate(recipe.get("ingredients", []))
                ],
                "summary": ", ".join(recipe.get("ingredientLines", [])),
                "instructions": "",  # Not directly available in basic response
                "nutrition": {
                    "nutrients": [
                        {
                            "name": "Calories",
                            "amount": recipe.get("calories", 0),
                            "unit": "kcal",
                            "percentOfDailyNeeds": 0
                        }
                    ]
                }
            }
            
            recipes.append(transformed_recipe)
        
        logger.info(f"Found {len(recipes)} recipes")
        return recipes
        
    except Exception as e:
        logger.error(f"Error in search_recipes: {str(e)}")
        logger.info("Using sample recipes as fallback due to error")
        return random.sample(SAMPLE_RECIPES, min(number, len(SAMPLE_RECIPES)))

def get_random_recipes(tags="", number=5):
    """
    Get random recipes, optionally filtered by tags.
    
    Args:
        tags (str, optional): Comma-separated list of tags. Defaults to "".
        number (int, optional): Number of results to return. Defaults to 5.
    
    Returns:
        list: List of recipe objects
    """
    try:
        logger.info(f"Getting random recipes with tags: {tags}")
        logger.info(f"Using Edamam API key: {EDAMAM_API_KEY}")
        logger.info(f"Using Edamam APP ID: {EDAMAM_APP_ID}")
        
        # Prepare the API endpoint and parameters
        params = {
            "type": "public",
            "app_id": EDAMAM_APP_ID,
            "app_key": EDAMAM_API_KEY,
            "q": tags if tags else "random",  # Use tags as query or "random" if no tags
            "random": "true",
        }
        
        # Add tags if provided
        if tags:
            tag_list = tags.split(',')
            for tag in tag_list:
                tag = tag.strip().lower()
                if tag in get_cuisines():
                    params["cuisineType"] = tag
                elif tag in get_diets():
                    params["diet"] = tag
        
        # Log the request parameters
        logger.info(f"Request parameters: {params}")
        
        # Make the API request
        logger.info(f"Making request to Edamam API: {BASE_URL}")
        response = requests.get(BASE_URL, params=params)
        
        # Log the response status code
        logger.info(f"Response status code: {response.status_code}")
        
        # If the response is not successful, log the response content
        if response.status_code != 200:
            logger.error(f"Error response: {response.text}")
            logger.info("Using sample recipes as fallback")
            return random.sample(SAMPLE_RECIPES, min(number, len(SAMPLE_RECIPES)))
        
        # Parse and return the results
        data = response.json()
        hits = data.get("hits", [])
        recipes = []
        
        for hit in hits[:number]:  # Limit to requested number
            recipe = hit.get("recipe", {})
            
            # Transform to match our expected format
            transformed_recipe = {
                "id": recipe.get("uri", "").split("_")[-1],  # Extract ID from URI
                "title": recipe.get("label", ""),
                "image": recipe.get("image", ""),
                "sourceUrl": recipe.get("url", ""),
                "sourceName": recipe.get("source", ""),
                "readyInMinutes": recipe.get("totalTime", 0),
                "servings": recipe.get("yield", 0),
                "healthScore": 0,  # Not directly available
                "spoonacularScore": 0,  # Not available
                "pricePerServing": 0,  # Not available
                "diets": recipe.get("dietLabels", []),
                "cuisines": recipe.get("cuisineType", []),
                "dishTypes": recipe.get("dishType", []),
                "extendedIngredients": [
                    {
                        "id": i,
                        "name": ingredient.get("food", ""),
                        "amount": ingredient.get("quantity", 0),
                        "unit": ingredient.get("measure", ""),
                        "original": ingredient.get("text", "")
                    }
                    for i, ingredient in enumerate(recipe.get("ingredients", []))
                ],
                "summary": ", ".join(recipe.get("ingredientLines", [])),
                "instructions": "",  # Not directly available in basic response
                "nutrition": {
                    "nutrients": [
                        {
                            "name": "Calories",
                            "amount": recipe.get("calories", 0),
                            "unit": "kcal",
                            "percentOfDailyNeeds": 0
                        }
                    ]
                }
            }
            
            recipes.append(transformed_recipe)
        
        logger.info(f"Retrieved {len(recipes)} random recipes")
        return recipes
        
    except Exception as e:
        logger.error(f"Error in get_random_recipes: {str(e)}")
        logger.info("Using sample recipes as fallback due to error")
        return random.sample(SAMPLE_RECIPES, min(number, len(SAMPLE_RECIPES)))

def get_cuisines():
    """
    Get a list of supported cuisines.
    
    Returns:
        list: List of cuisine names
    """
    return [
        "American", "Asian", "British", "Caribbean", "Central Europe", 
        "Chinese", "Eastern Europe", "French", "Indian", "Italian", 
        "Japanese", "Kosher", "Mediterranean", "Mexican", "Middle Eastern", 
        "Nordic", "South American", "South East Asian"
    ]

def get_diets():
    """
    Get a list of supported diets.
    
    Returns:
        list: List of diet names
    """
    return [
        "Balanced", "High-Fiber", "High-Protein", "Low-Carb", "Low-Fat", 
        "Low-Sodium"
    ]

def get_intolerances():
    """
    Get a list of supported intolerances.
    
    Returns:
        list: List of intolerance names
    """
    return [
        "Alcohol", "Celery", "Crustacean", "Dairy", "Egg", "Fish", "Gluten", 
        "Grain", "Peanut", "Sesame", "Shellfish", "Soy", "Sulfite", "Tree Nut", 
        "Wheat"
    ] 