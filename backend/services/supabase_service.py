import os
import logging
import supabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get Supabase credentials from environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')

# Log status (without showing the full key for security reasons)
logger.info(f"Supabase URL: {SUPABASE_URL}")
if SUPABASE_KEY:
    key_preview = SUPABASE_KEY[:5] + "..." if len(SUPABASE_KEY) > 5 else "INVALID"
    logger.info(f"Supabase Key: {key_preview}")
else:
    logger.warning("Supabase Key not found in environment variables")

# Validate configuration
if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("Supabase URL or Key not configured correctly")
    raise ValueError("Missing Supabase configuration. Check your .env file.")

# Initialize Supabase client
supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

def get_saved_recipe_ids(user_id):
    """
    Get the saved recipe IDs for a user from Supabase.
    
    Args:
        user_id (str): The user's ID (UUID from Supabase auth)
    
    Returns:
        list: List of saved recipe IDs
    """
    try:
        logger.info(f"Fetching saved recipe IDs for user: {user_id}")
        
        # Query the saved_recipes table for this user
        response = supabase_client.table('saved_recipes') \
            .select('recipe_id') \
            .eq('user_id', user_id) \
            .execute()
        
        # Extract recipe_ids from the response
        recipe_ids = [item['recipe_id'] for item in response.data]
        logger.info(f"Found {len(recipe_ids)} saved recipes for user {user_id}")
        
        return recipe_ids
    except Exception as e:
        logger.error(f"Error fetching saved recipe IDs: {str(e)}")
        return []

def save_recipe(user_id, recipe_id):
    """
    Save a recipe ID for a user in Supabase.
    
    Args:
        user_id (str): The user's ID (UUID from Supabase auth)
        recipe_id (str): The Edamam recipe ID to save
    
    Returns:
        bool: True if saved successfully
    """
    try:
        logger.info(f"Saving recipe {recipe_id} for user {user_id}")
        
        # Insert the recipe ID into the saved_recipes table
        response = supabase_client.table('saved_recipes') \
            .insert({
                'user_id': user_id,
                'recipe_id': recipe_id
            }) \
            .execute()
        
        return True
    except Exception as e:
        logger.error(f"Error saving recipe: {str(e)}")
        return False

def remove_saved_recipe(user_id, recipe_id):
    """
    Remove a saved recipe for a user from Supabase.
    
    Args:
        user_id (str): The user's ID (UUID from Supabase auth)
        recipe_id (str): The Edamam recipe ID to remove
    
    Returns:
        bool: True if removed successfully
    """
    try:
        logger.info(f"Removing recipe {recipe_id} for user {user_id}")
        
        # Delete the recipe from the saved_recipes table
        response = supabase_client.table('saved_recipes') \
            .delete() \
            .eq('user_id', user_id) \
            .eq('recipe_id', recipe_id) \
            .execute()
        
        return True
    except Exception as e:
        logger.error(f"Error removing saved recipe: {str(e)}")
        return False 