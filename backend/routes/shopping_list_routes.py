from flask import Blueprint, request, jsonify
import logging
from services.shopping_list import generate_shopping_list
import re

# Set up logging
logger = logging.getLogger(__name__)

# Create Blueprint
shopping_list_bp = Blueprint('shopping_list', __name__)

@shopping_list_bp.route('/generate', methods=['POST'])
def generate_shopping_list_endpoint():
    """
    Generate a shopping list from a list of recipes
    
    Request body:
    {
        "recipes": [
            {
                "id": "123",
                "title": "Chocolate Cake",
                "servings": 8,
                "extendedIngredients": [
                    {
                        "name": "all-purpose flour",
                        "amount": 2,
                        "unit": "cups"
                    },
                    ...
                ]
            },
            ...
        ]
    }
    
    Response:
    {
        "shoppingList": [
            {
                "id": "1",
                "name": "all-purpose flour",
                "amount": 2,
                "formatted_amount": "2",
                "unit": "cups",
                "display_text": "2 cups all-purpose flour",
                "category": "Baking & Spices",
                "checked": false,
                "standardizedDisplay": "265 g"
            },
            ...
        ],
        "success": true
    }
    """
    try:
        # Get request data
        request_data = request.get_json()
        
        # Validate request
        if not request_data:
            return jsonify({"success": False, "error": "No data provided"}), 400
            
        recipes = request_data.get('recipes', [])
        if not recipes:
            return jsonify({"success": False, "error": "No recipes provided"}), 400
            
        # Generate shopping list
        shopping_list = generate_shopping_list(recipes)
        
        # Ensure each item has properly formatted display_text
        for item in shopping_list:
            # Fix common formatting issues
            
            # 1. Fix display_text if needed
            if 'display_text' not in item:
                # For backwards compatibility, generate display_text if missing
                unit = item.get('unit', '')
                if unit == 'count':
                    item['display_text'] = f"{item['formatted_amount']} {item['name']}"
                else:
                    item['display_text'] = f"{item['formatted_amount']} {unit} {item['name']}"
            
            # 2. Fix id at beginning of display text
            # If display_text starts with a number followed by a space, check if it's the item ID
            match = re.match(r'^(\d+)\s+(.+)$', item['display_text'])
            if match and match.group(1) in [item['id'], str(item['id'])]:
                # Remove the ID from the beginning
                item['display_text'] = match.group(2)
            
            # 3. Remove any numeric prefix that might be an ID
            # This is a more aggressive approach to fix the "1 " prefix issue
            if re.match(r'^1\s+', item['display_text']):
                # Get the next part after "1 "
                next_part = item['display_text'][2:].strip()
                
                # Remove the "1 " prefix and keep whatever comes after
                item['display_text'] = next_part
            
            # 4. Fix standardizedDisplay
            if 'standardizedDisplay' in item:
                # If standardizedDisplay just shows "1 g" or "1 ml", fix it
                if item['standardizedDisplay'] in ["1 g", "1 ml"]:
                    std_unit = "g" if "g" in item['standardizedDisplay'] else "ml"
                    item['standardizedDisplay'] = f"{item['formatted_amount']} {std_unit} {item['name']}"
                
                # Also check for the "1 " prefix in standardizedDisplay
                if re.match(r'^1\s+', item['standardizedDisplay']):
                    # Get the next part after "1 "
                    next_part = item['standardizedDisplay'][2:].strip()
                    
                    # Remove the "1 " prefix and keep whatever comes after
                    item['standardizedDisplay'] = next_part
                    
                    # If we end up with just "g" or "ml", use the formatted_amount
                    if item['standardizedDisplay'] in ["g", "ml"]:
                        std_unit = item['standardizedDisplay']
                        item['standardizedDisplay'] = f"{item['formatted_amount']} {std_unit} {item['name']}"
        
        # Calculate category counts and other stats
        categories = {}
        total_count = len(shopping_list)
        checked_count = sum(1 for item in shopping_list if item.get('checked', False))
        
        for item in shopping_list:
            category = item['category']
            if category not in categories:
                categories[category] = 0
            categories[category] += 1
            
        # Add category count to each item
        for item in shopping_list:
            item['category_count'] = categories[item['category']]
        
        # Return response
        return jsonify({
            "success": True,
            "shoppingList": shopping_list,
            "categories": {category: count for category, count in categories.items()},
            "totalCount": total_count,
            "checkedCount": checked_count
        })
    
    except Exception as e:
        logger.error(f"Error generating shopping list: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Error generating shopping list: {str(e)}"
        }), 500 