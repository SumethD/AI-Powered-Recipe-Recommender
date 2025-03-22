from flask import Blueprint, request, jsonify
import logging
from services.supabase_service import get_saved_recipe_ids, save_recipe, remove_saved_recipe
from services.edamam_service import get_recipe_by_id

# Create blueprint
saved_recipes_bp = Blueprint('saved_recipes', __name__)
logger = logging.getLogger(__name__)

@saved_recipes_bp.route('/api/saved-recipes', methods=['GET'])
def get_saved_recipes():
    """Get saved recipe IDs for the logged-in user"""
    try:
        # Get the user ID from the request
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
        
        # Get the saved recipe IDs from Supabase
        recipe_ids = get_saved_recipe_ids(user_id)
        
        # Return the list of recipe IDs
        return jsonify({"success": True, "recipe_ids": recipe_ids})
    
    except Exception as e:
        logger.error(f"Error getting saved recipes: {str(e)}")
        return jsonify({"error": "Failed to get saved recipes"}), 500


@saved_recipes_bp.route('/api/recipes/batch', methods=['POST'])
def get_recipe_batch():
    """Get recipe details for a batch of recipe IDs"""
    try:
        # Get the list of recipe IDs from the request body
        data = request.json
        recipe_ids = data.get('recipe_ids', [])
        
        if not recipe_ids:
            return jsonify({"error": "Recipe IDs are required"}), 400
        
        # Get recipe details for each ID
        recipes = []
        for recipe_id in recipe_ids:
            try:
                recipe = get_recipe_by_id(recipe_id)
                if recipe:
                    recipes.append(recipe)
            except Exception as e:
                logger.error(f"Error getting recipe details for {recipe_id}: {str(e)}")
        
        # Return the list of recipe details
        return jsonify({"success": True, "recipes": recipes})
    
    except Exception as e:
        logger.error(f"Error getting recipe batch: {str(e)}")
        return jsonify({"error": "Failed to get recipe batch"}), 500


@saved_recipes_bp.route('/api/saved-recipes', methods=['POST'])
def save_recipe_route():
    """Save a recipe for the logged-in user"""
    try:
        # Get the user ID and recipe ID from the request
        data = request.json
        user_id = data.get('user_id')
        recipe_id = data.get('recipe_id')
        
        if not user_id or not recipe_id:
            return jsonify({"error": "User ID and recipe ID are required"}), 400
        
        # Save the recipe
        success = save_recipe(user_id, recipe_id)
        
        if success:
            return jsonify({"success": True, "message": "Recipe saved successfully"})
        else:
            return jsonify({"error": "Failed to save recipe"}), 500
    
    except Exception as e:
        logger.error(f"Error saving recipe: {str(e)}")
        return jsonify({"error": "Failed to save recipe"}), 500


@saved_recipes_bp.route('/api/saved-recipes/<recipe_id>', methods=['DELETE'])
def remove_saved_recipe_route(recipe_id):
    """Remove a saved recipe for the logged-in user"""
    try:
        # Get the user ID from the request
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
        
        # Remove the recipe
        success = remove_saved_recipe(user_id, recipe_id)
        
        if success:
            return jsonify({"success": True, "message": "Recipe removed successfully"})
        else:
            return jsonify({"error": "Failed to remove recipe"}), 500
    
    except Exception as e:
        logger.error(f"Error removing saved recipe: {str(e)}")
        return jsonify({"error": "Failed to remove recipe"}), 500 