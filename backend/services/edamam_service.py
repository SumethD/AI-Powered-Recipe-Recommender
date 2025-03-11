import os
import logging
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure API key
EDAMAM_APP_ID = os.getenv("EDAMAM_APP_ID")
EDAMAM_API_KEY = os.getenv("EDAMAM_API_KEY")
print(f"Using Edamam API key: {EDAMAM_API_KEY}")
print(f"Using Edamam APP ID: {EDAMAM_APP_ID}")
BASE_URL = "https://api.edamam.com/api/recipes/v2"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        logger.info(f"Edamam service: Searching for recipes with ingredients: {ingredients}")
        
        # Check if API key is available
        if not EDAMAM_API_KEY or not EDAMAM_APP_ID:
            logger.error("Edamam API key or App ID not found")
            raise Exception("Edamam API key or App ID not configured")
        
        # Prepare the API endpoint and parameters
        params = {
            "type": "public",
            "app_id": EDAMAM_APP_ID,
            "app_key": EDAMAM_API_KEY,
            "q": " ".join(ingredients),
            "random": "true",
        }
        
        # Make the API request
        logger.info(f"Making request to Edamam API: {BASE_URL} with params: {params}")
        
        try:
            response = requests.get(BASE_URL, params=params, timeout=30)
            
            # Log the response status code
            logger.info(f"Response status code: {response.status_code}")
            
            # If the response is not successful, log the response content
            if response.status_code != 200:
                logger.error(f"Error response: {response.text}")
                raise Exception(f"Edamam API error: {response.status_code} - {response.text}")
            
            # Parse and return the results
            data = response.json()
            
            # Check if the response has the expected format
            if 'hits' not in data:
                logger.error(f"Unexpected response format: 'hits' not found in response")
                logger.error(f"Response data: {data}")
                raise Exception("Unexpected response format from Edamam API")
                
            hits = data.get("hits", [])
            logger.info(f"Received {len(hits)} hits from Edamam API")
            
            recipes = []
            
            for hit in hits[:number]:  # Limit to requested number
                recipe = hit.get("recipe", {})
                
                # Extract ID from URI
                recipe_id = recipe.get("uri", "").split("_")[-1]
                
                # Normalize the ID to lowercase
                recipe_id = recipe_id.lower()
                
                # Get the recipe title, ensuring it's not empty
                title = recipe.get("label", "")
                if not title:
                    logger.warning(f"Recipe {recipe_id} has no title, using 'Untitled Recipe'")
                    title = "Untitled Recipe"
                
                # Log the recipe for debugging
                logger.info(f"Found recipe: ID={recipe_id}, Title={title}")
                
                # Transform the recipe using the common function
                transformed_recipe = transform_edamam_recipe(recipe, recipe_id)
                recipes.append(transformed_recipe)
            
            logger.info(f"Returning {len(recipes)} recipes")
            return recipes
            
        except requests.exceptions.Timeout:
            logger.error("Request to Edamam API timed out")
            raise Exception("Request to Edamam API timed out")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            raise Exception(f"Request error: {str(e)}")
        
    except Exception as e:
        logger.error(f"Error in get_recipes_by_ingredients: {str(e)}")
        raise Exception(f"Failed to get recipes by ingredients: {str(e)}")

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
        
        # Validate recipe_id
        if not recipe_id:
            logger.error("Empty recipe ID provided")
            raise Exception("Recipe ID is required")
        
        # Normalize the recipe ID to lowercase if it's a string
        if isinstance(recipe_id, str):
            recipe_id = recipe_id.lower()
            logger.info(f"Normalized recipe ID to lowercase: {recipe_id}")
        
        # Check if API key is available
        if not EDAMAM_API_KEY or not EDAMAM_APP_ID:
            logger.error("Edamam API key or App ID not found")
            raise Exception("Edamam API key or App ID not configured")
        
        # For Edamam, we need to construct the full URI for the recipe
        # The format is: http://www.edamam.com/ontologies/edamam.owl#recipe_{ID}
        edamam_uri = f"http://www.edamam.com/ontologies/edamam.owl#recipe_{recipe_id}"
        encoded_uri = requests.utils.quote(edamam_uri)
        
        # Method 1: Try to get the recipe using the URI parameter
        params = {
            "type": "public",
            "app_id": EDAMAM_APP_ID,
            "app_key": EDAMAM_API_KEY,
            "uri": edamam_uri
        }
        
        logger.info(f"Making request to Edamam API with URI: {edamam_uri}")
        response = requests.get(BASE_URL, params=params)
        
        logger.info(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            hits = data.get("hits", [])
            
            if hits and len(hits) > 0:
                recipe = hits[0].get("recipe", {})
                
                # Verify the recipe has a title
                recipe_title = recipe.get('label', '')
                if not recipe_title:
                    logger.warning(f"Recipe {recipe_id} has no title")
                    recipe_title = "Untitled Recipe"
                    recipe['label'] = recipe_title
                
                logger.info(f"Successfully retrieved recipe: {recipe_title}")
                
                # Transform to match our expected format
                transformed_recipe = transform_edamam_recipe(recipe, recipe_id)
                return transformed_recipe
            else:
                logger.warning(f"No hits found for recipe ID {recipe_id}")
        
        # If the first method fails, try an alternative approach using a search
        logger.warning(f"URI method failed, trying search method for recipe ID: {recipe_id}")
        
        # Method 2: Try searching for the recipe using the ID as a query (fallback)
        search_params = {
            "type": "public",
            "app_id": EDAMAM_APP_ID,
            "app_key": EDAMAM_API_KEY,
            "q": recipe_id,
        }
        
        logger.info(f"Making search request to: {BASE_URL}")
        search_response = requests.get(BASE_URL, params=search_params)
        
        if search_response.status_code != 200:
            logger.error(f"Search request failed with status code {search_response.status_code}")
            raise Exception(f"Failed to retrieve recipe details: {search_response.status_code}")
        
        # Parse and return the results
        data = search_response.json()
        hits = data.get("hits", [])
        
        if not hits or len(hits) == 0:
            logger.error(f"No recipes found for ID {recipe_id}")
            raise Exception(f"Recipe with ID {recipe_id} not found")
        
        # Just use the first recipe from the search results as a fallback
        recipe = hits[0].get("recipe", {})
        
        # Verify the recipe has a title
        recipe_title = recipe.get('label', '')
        if not recipe_title:
            logger.warning(f"Recipe {recipe_id} has no title")
            recipe_title = "Untitled Recipe"
            recipe['label'] = recipe_title
        
        # Transform to match our expected format
        transformed_recipe = transform_edamam_recipe(recipe, recipe_id)
        logger.info(f"Found recipe in search results: {transformed_recipe['title']}")
        return transformed_recipe
        
    except Exception as e:
        logger.error(f"Error in get_recipe_details: {str(e)}")
        raise Exception(f"Failed to get recipe details: {str(e)}")

def transform_edamam_recipe(recipe, recipe_id):
    """
    Transform an Edamam recipe to match our expected format.
    
    Args:
        recipe (dict): The Edamam recipe
        recipe_id (str): The recipe ID
    
    Returns:
        dict: Transformed recipe
    """
    try:
        # Ensure recipe_id is a string and normalized to lowercase
        recipe_id_str = str(recipe_id).lower()
        
        # Get the recipe title, ensuring it's not empty
        title = recipe.get("label", "")
        if not title:
            logger.warning(f"Recipe {recipe_id_str} has no title, using 'Untitled Recipe'")
            title = "Untitled Recipe"
        
        # Get the image URL, with a fallback
        image = recipe.get("image", "")
        if not image:
            logger.warning(f"Recipe {recipe_id_str} has no image, using placeholder")
            image = "https://via.placeholder.com/300x200?text=No+Image+Available"
        
        # Get the source information
        source_name = recipe.get("source", "")
        source_url = recipe.get("url", "")
        
        # Get the servings
        servings = recipe.get("yield", 0)
        if not servings or servings <= 0:
            servings = 4  # Default to 4 servings if not specified
        
        # Get the cooking time (in minutes)
        total_time = recipe.get("totalTime", 0)
        if not total_time or total_time <= 0:
            total_time = 30  # Default to 30 minutes if not specified
        
        # Get the ingredients
        ingredient_lines = recipe.get("ingredientLines", [])
        ingredients = []
        
        for i, line in enumerate(ingredient_lines):
            ingredients.append({
                "id": i + 1,
                "name": line,
                "amount": 1,
                "unit": "",
                "original": line,
                "image": ""
            })
        
        # Get the diet labels and health labels
        diet_labels = recipe.get("dietLabels", [])
        health_labels = recipe.get("healthLabels", [])
        
        # Combine diet and health labels
        diets = diet_labels + health_labels
        
        # Get the cuisine type
        cuisines = recipe.get("cuisineType", [])
        
        # Get the dish type
        dish_types = recipe.get("dishType", [])
        
        # Get the nutrition information
        nutrients = []
        nutrition = {
            "nutrients": nutrients,
            "caloricBreakdown": {
                "percentProtein": 0,
                "percentFat": 0,
                "percentCarbs": 0
            }
        }
        
        if "totalNutrients" in recipe:
            total_nutrients = recipe.get("totalNutrients", {})
            
            # Extract common nutrients
            for key, nutrient in total_nutrients.items():
                if nutrient and isinstance(nutrient, dict):
                    nutrients.append({
                        "name": nutrient.get("label", key),
                        "amount": nutrient.get("quantity", 0),
                        "unit": nutrient.get("unit", ""),
                        "percentOfDailyNeeds": 0
                    })
            
            # Calculate caloric breakdown if available
            calories = total_nutrients.get("ENERC_KCAL", {}).get("quantity", 0)
            protein = total_nutrients.get("PROCNT", {}).get("quantity", 0)
            fat = total_nutrients.get("FAT", {}).get("quantity", 0)
            carbs = total_nutrients.get("CHOCDF", {}).get("quantity", 0)
            
            if calories > 0:
                protein_calories = protein * 4  # 4 calories per gram of protein
                fat_calories = fat * 9  # 9 calories per gram of fat
                carb_calories = carbs * 4  # 4 calories per gram of carbs
                
                nutrition["caloricBreakdown"] = {
                    "percentProtein": round((protein_calories / calories) * 100) if protein_calories > 0 else 0,
                    "percentFat": round((fat_calories / calories) * 100) if fat_calories > 0 else 0,
                    "percentCarbs": round((carb_calories / calories) * 100) if carb_calories > 0 else 0
                }
        
        # Create the transformed recipe
        transformed_recipe = {
            "id": recipe_id_str,
            "title": title,
            "image": image,
            "servings": servings,
            "readyInMinutes": total_time,
            "sourceName": source_name,
            "sourceUrl": source_url,
            "instructions": source_url,  # Use source URL as instructions link for Edamam
            "extendedIngredients": ingredients,
            "diets": diets,
            "cuisines": cuisines,
            "dishTypes": dish_types,
            "summary": recipe.get("summary", f"A delicious {title} recipe."),
            "nutrition": nutrition,
            "vegetarian": "Vegetarian" in health_labels,
            "vegan": "Vegan" in health_labels,
            "glutenFree": "Gluten-Free" in health_labels,
            "dairyFree": "Dairy-Free" in health_labels,
        }
        
        return transformed_recipe
        
    except Exception as e:
        logger.error(f"Error transforming Edamam recipe: {str(e)}")
        
        # Return a minimal valid recipe to avoid breaking the frontend
        return {
            "id": recipe_id,
            "title": recipe.get("label", "Untitled Recipe"),
            "image": recipe.get("image", "https://via.placeholder.com/300x200?text=No+Image+Available"),
            "servings": 4,
            "readyInMinutes": 30,
            "sourceUrl": recipe.get("url", ""),
            "instructions": recipe.get("url", ""),
            "extendedIngredients": [],
            "diets": [],
            "cuisines": [],
            "dishTypes": [],
            "summary": f"A recipe for {recipe.get('label', 'food')}.",
        }

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
        if not EDAMAM_API_KEY or not EDAMAM_APP_ID:
            logger.error("Edamam API key or App ID not found")
            raise Exception("Edamam API key or App ID not configured")
        
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
            raise Exception(f"Edamam API error: {response.status_code}")
        
        # Parse and return the results
        data = response.json()
        hits = data.get("hits", [])
        recipes = []
        
        for hit in hits[:number]:  # Limit to requested number
            recipe = hit.get("recipe", {})
            
            # Extract ID from URI
            recipe_id = recipe.get("uri", "").split("_")[-1]
            
            # Normalize the ID to lowercase
            recipe_id = recipe_id.lower()
            
            # Get the recipe title, ensuring it's not empty
            title = recipe.get("label", "")
            if not title:
                logger.warning(f"Recipe {recipe_id} has no title, using 'Untitled Recipe'")
                title = "Untitled Recipe"
            
            # Log the recipe for debugging
            logger.info(f"Found recipe: ID={recipe_id}, Title={title}")
            
            # Transform the recipe using the common function
            transformed_recipe = transform_edamam_recipe(recipe, recipe_id)
            recipes.append(transformed_recipe)
        
        logger.info(f"Found {len(recipes)} recipes")
        return recipes
        
    except Exception as e:
        logger.error(f"Error in search_recipes: {str(e)}")
        raise Exception(f"Failed to search recipes: {str(e)}")

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
        
        # Check if API key is available
        if not EDAMAM_API_KEY or not EDAMAM_APP_ID:
            logger.error("Edamam API key or App ID not found")
            raise Exception("Edamam API key or App ID not configured")
        
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
            raise Exception(f"Edamam API error: {response.status_code}")
        
        # Parse and return the results
        data = response.json()
        hits = data.get("hits", [])
        recipes = []
        
        for hit in hits[:number]:  # Limit to requested number
            recipe = hit.get("recipe", {})
            
            # Extract ID from URI
            recipe_id = recipe.get("uri", "").split("_")[-1]
            
            # Get the recipe title, ensuring it's not empty
            title = recipe.get("label", "")
            if not title:
                logger.warning(f"Recipe {recipe_id} has no title, using 'Untitled Recipe'")
                title = "Untitled Recipe"
            
            # Log the recipe for debugging
            logger.info(f"Found recipe: ID={recipe_id}, Title={title}")
            
            # Transform the recipe using the common function
            transformed_recipe = transform_edamam_recipe(recipe, recipe_id)
            recipes.append(transformed_recipe)
        
        logger.info(f"Retrieved {len(recipes)} random recipes")
        return recipes
        
    except Exception as e:
        logger.error(f"Error in get_random_recipes: {str(e)}")
        raise Exception(f"Failed to get random recipes: {str(e)}")

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