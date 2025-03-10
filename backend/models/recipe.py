import datetime
from flask import current_app

class Recipe:
    """
    Model representing a recipe with standardized attributes
    """
    
    def __init__(self, id, title, image=None, source_url=None, source_name=None, 
                 ready_in_minutes=None, servings=None, summary=None, instructions=None,
                 ingredients=None, nutrition=None, cuisines=None, diets=None, 
                 dish_types=None, occasions=None, likes=None, used_ingredients=None, 
                 missed_ingredients=None, unused_ingredients=None):
        """
        Initialize a Recipe object
        
        Args:
            id: Recipe ID
            title: Recipe title
            image: URL to recipe image
            source_url: URL to recipe source
            source_name: Name of recipe source
            ready_in_minutes: Time to prepare recipe in minutes
            servings: Number of servings
            summary: Recipe summary
            instructions: Recipe instructions
            ingredients: List of ingredients
            nutrition: Nutrition information
            cuisines: List of cuisines
            diets: List of diets
            dish_types: List of dish types
            occasions: List of occasions
            likes: Number of likes
            used_ingredients: Ingredients used (for ingredient-based search)
            missed_ingredients: Ingredients missing (for ingredient-based search)
            unused_ingredients: Ingredients not used (for ingredient-based search)
        """
        self.id = id
        self.title = title
        self.image = image
        self.source_url = source_url
        self.source_name = source_name
        self.ready_in_minutes = ready_in_minutes
        self.servings = servings
        self.summary = summary
        self.instructions = instructions
        self.ingredients = ingredients or []
        self.nutrition = nutrition
        self.cuisines = cuisines or []
        self.diets = diets or []
        self.dish_types = dish_types or []
        self.occasions = occasions or []
        self.likes = likes
        self.used_ingredients = used_ingredients or []
        self.missed_ingredients = missed_ingredients or []
        self.unused_ingredients = unused_ingredients or []
        self.created_at = datetime.datetime.now().isoformat()
    
    @classmethod
    def from_api_response(cls, data):
        """
        Create a Recipe object from an API response
        
        Args:
            data: Dictionary containing recipe data from API
            
        Returns:
            Recipe object
        """
        try:
            # Extract basic recipe information
            recipe_id = data.get('id')
            title = data.get('title')
            
            # Create a new Recipe object
            recipe = cls(
                id=recipe_id,
                title=title,
                image=data.get('image'),
                source_url=data.get('sourceUrl'),
                source_name=data.get('sourceName'),
                ready_in_minutes=data.get('readyInMinutes'),
                servings=data.get('servings'),
                summary=data.get('summary'),
                instructions=data.get('instructions'),
                likes=data.get('likes'),
                used_ingredients=data.get('usedIngredients', []),
                missed_ingredients=data.get('missedIngredients', []),
                unused_ingredients=data.get('unusedIngredients', [])
            )
            
            # Extract ingredients if available
            if 'extendedIngredients' in data:
                recipe.ingredients = data['extendedIngredients']
            
            # Extract nutrition information if available
            if 'nutrition' in data:
                recipe.nutrition = data['nutrition']
            
            # Extract additional information if available
            if 'cuisines' in data:
                recipe.cuisines = data['cuisines']
            
            if 'diets' in data:
                recipe.diets = data['diets']
            
            if 'dishTypes' in data:
                recipe.dish_types = data['dishTypes']
            
            if 'occasions' in data:
                recipe.occasions = data['occasions']
            
            return recipe
        
        except Exception as e:
            current_app.logger.error(f"Error creating Recipe from API response: {str(e)}")
            # Return a minimal Recipe object with available data
            return cls(
                id=data.get('id', 0),
                title=data.get('title', 'Unknown Recipe')
            )
    
    def to_dict(self):
        """
        Convert Recipe object to dictionary
        
        Returns:
            Dictionary representation of Recipe
        """
        return {
            'id': self.id,
            'title': self.title,
            'image': self.image,
            'source_url': self.source_url,
            'source_name': self.source_name,
            'ready_in_minutes': self.ready_in_minutes,
            'servings': self.servings,
            'summary': self.summary,
            'instructions': self.instructions,
            'ingredients': self.ingredients,
            'nutrition': self.nutrition,
            'cuisines': self.cuisines,
            'diets': self.diets,
            'dish_types': self.dish_types,
            'occasions': self.occasions,
            'likes': self.likes,
            'used_ingredients': self.used_ingredients,
            'missed_ingredients': self.missed_ingredients,
            'unused_ingredients': self.unused_ingredients,
            'created_at': self.created_at
        }
    
    def __str__(self):
        """
        String representation of Recipe
        
        Returns:
            String representation
        """
        return f"Recipe(id={self.id}, title={self.title})" 