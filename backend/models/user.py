import os
import json
import logging
import time
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class User:
    """
    User model for storing user data and favorites.
    """
    
    def __init__(self, user_id, name="User"):
        """
        Initialize a user with the given ID.
        
        Args:
            user_id (str): The user's unique identifier
            name (str, optional): The user's name. Defaults to "User".
        """
        self.id = user_id
        self.name = name
        self.preferences = {
            "diets": [],
            "intolerances": [],
            "cuisines": []
        }
        self.favorites = []
        self._load_favorites()
    
    def _get_favorites_path(self):
        """
        Get the path to the user's favorites file.
        
        Returns:
            str: Path to the favorites file
        """
        # Create data directory if it doesn't exist
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # Create user directory if it doesn't exist
        user_dir = os.path.join(data_dir, "users")
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        
        return os.path.join(user_dir, f"{self.id}_favorites.json")
    
    def _load_favorites(self):
        """
        Load favorites from file.
        """
        try:
            favorites_path = self._get_favorites_path()
            if os.path.exists(favorites_path):
                with open(favorites_path, 'r') as f:
                    self.favorites = json.load(f)
                logger.info(f"Loaded {len(self.favorites)} favorites for user {self.id}")
            else:
                logger.info(f"No favorites file found for user {self.id}")
                self.favorites = []
        except Exception as e:
            logger.error(f"Error loading favorites for user {self.id}: {str(e)}")
            self.favorites = []
    
    def _save_favorites(self):
        """
        Save favorites to file.
        """
        try:
            favorites_path = self._get_favorites_path()
            with open(favorites_path, 'w') as f:
                json.dump(self.favorites, f, indent=2)
            logger.info(f"Saved {len(self.favorites)} favorites for user {self.id}")
        except Exception as e:
            logger.error(f"Error saving favorites for user {self.id}: {str(e)}")
    
    def add_favorite(self, recipe):
        """
        Add a recipe to favorites.
        
        Args:
            recipe (dict): Recipe object to add to favorites
        
        Returns:
            bool: True if added successfully, False if already in favorites
        """
        # Check if recipe is already in favorites
        for fav in self.favorites:
            if fav.get('id') == recipe.get('id'):
                logger.info(f"Recipe {recipe.get('id')} already in favorites for user {self.id}")
                return False
        
        # Add timestamp
        recipe['added_at'] = time.time()
        
        # Add to favorites and save
        self.favorites.append(recipe)
        self._save_favorites()
        logger.info(f"Added recipe {recipe.get('id')} to favorites for user {self.id}")
        return True
    
    def remove_favorite(self, recipe_id):
        """
        Remove a recipe from favorites.
        
        Args:
            recipe_id (int or str): ID of the recipe to remove (can be a string for Edamam recipes)
        
        Returns:
            bool: True if removed successfully, False if not in favorites
        """
        initial_count = len(self.favorites)
        self.favorites = [fav for fav in self.favorites if str(fav.get('id')) != str(recipe_id)]
        
        if len(self.favorites) < initial_count:
            self._save_favorites()
            logger.info(f"Removed recipe {recipe_id} from favorites for user {self.id}")
            return True
        else:
            logger.info(f"Recipe {recipe_id} not found in favorites for user {self.id}")
            return False
    
    def get_favorites(self, limit=None, sort_by='added_at', reverse=True):
        """
        Get the user's favorite recipes.
        
        Args:
            limit (int, optional): Maximum number of favorites to return. Defaults to None.
            sort_by (str, optional): Field to sort by. Defaults to 'added_at'.
            reverse (bool, optional): Whether to reverse the sort order. Defaults to True.
        
        Returns:
            list: List of favorite recipes
        """
        # Sort favorites
        if sort_by in self.favorites[0] if self.favorites else []:
            sorted_favorites = sorted(self.favorites, key=lambda x: x.get(sort_by, 0), reverse=reverse)
        else:
            sorted_favorites = self.favorites
        
        # Apply limit if specified
        if limit is not None and limit > 0:
            return sorted_favorites[:limit]
        return sorted_favorites
    
    def is_favorite(self, recipe_id):
        """
        Check if a recipe is in the user's favorites.
        
        Args:
            recipe_id (int or str): ID of the recipe to check (can be a string for Edamam recipes)
        
        Returns:
            bool: True if in favorites, False otherwise
        """
        return any(str(fav.get('id')) == str(recipe_id) for fav in self.favorites)
    
    def update_preferences(self, preferences):
        """
        Update user preferences.
        
        Args:
            preferences (dict): New preferences to update
        """
        if preferences:
            for key, value in preferences.items():
                if key in self.preferences:
                    self.preferences[key] = value
            logger.info(f"Updated preferences for user {self.id}")
    
    def to_dict(self):
        """
        Convert user object to dictionary.
        
        Returns:
            dict: User data as dictionary
        """
        return {
            'id': self.id,
            'name': self.name,
            'preferences': self.preferences,
            'favorites_count': len(self.favorites)
        } 