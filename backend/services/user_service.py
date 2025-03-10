import logging
from models.user import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory user storage
_users = {}

def get_user(user_id):
    """
    Get a user by ID, creating a new user if not found.
    
    Args:
        user_id (str): The user's ID
    
    Returns:
        User: The user object
    """
    if user_id not in _users:
        logger.info(f"Creating new user with ID: {user_id}")
        _users[user_id] = User(user_id)
    return _users[user_id]

def get_user_favorites(user_id, limit=None, sort_by='added_at', reverse=True):
    """
    Get a user's favorite recipes.
    
    Args:
        user_id (str): The user's ID
        limit (int, optional): Maximum number of favorites to return. Defaults to None.
        sort_by (str, optional): Field to sort by. Defaults to 'added_at'.
        reverse (bool, optional): Whether to reverse the sort order. Defaults to True.
    
    Returns:
        list: List of favorite recipes
    """
    user = get_user(user_id)
    return user.get_favorites(limit, sort_by, reverse)

def add_favorite(user_id, recipe):
    """
    Add a recipe to a user's favorites.
    
    Args:
        user_id (str): The user's ID
        recipe (dict): Recipe object to add to favorites
    
    Returns:
        bool: True if added successfully, False if already in favorites
    """
    user = get_user(user_id)
    return user.add_favorite(recipe)

def remove_favorite(user_id, recipe_id):
    """
    Remove a recipe from a user's favorites.
    
    Args:
        user_id (str): The user's ID
        recipe_id (int): ID of the recipe to remove
    
    Returns:
        bool: True if removed successfully, False if not in favorites
    """
    user = get_user(user_id)
    return user.remove_favorite(recipe_id)

def is_favorite(user_id, recipe_id):
    """
    Check if a recipe is in a user's favorites.
    
    Args:
        user_id (str): The user's ID
        recipe_id (int): ID of the recipe to check
    
    Returns:
        bool: True if in favorites, False otherwise
    """
    user = get_user(user_id)
    return user.is_favorite(recipe_id)

def update_user_preferences(user_id, preferences):
    """
    Update a user's preferences.
    
    Args:
        user_id (str): The user's ID
        preferences (dict): New preferences to update
    """
    user = get_user(user_id)
    user.update_preferences(preferences)

def get_user_preferences(user_id):
    """
    Get a user's preferences.
    
    Args:
        user_id (str): The user's ID
    
    Returns:
        dict: User preferences
    """
    user = get_user(user_id)
    return user.preferences 