from flask import Blueprint, request, jsonify
import re
import logging
from collections import defaultdict

# Configure logging
logger = logging.getLogger("shopping_list")

# Create blueprint
shopping_list_bp = Blueprint('shopping_list', __name__)

# Helper functions for processing ingredients
def parse_ingredient(ingredient_str):
    """Parse an ingredient string into quantity, unit, and name."""
    # Basic pattern to extract quantity, unit and name
    # This is a simplified version - a production system would need more robust parsing
    pattern = r'^([\d\/\.\s]+)?\s*([a-zA-Z]+\s+)?\s*(.+)$'
    match = re.match(pattern, ingredient_str.strip())
    
    if not match:
        return {'amount': 1, 'unit': '', 'name': ingredient_str.strip()}
    
    quantity_str, unit_str, name = match.groups()
    
    # Default values
    quantity = 1
    unit = ''
    
    # Process quantity if it exists
    if quantity_str:
        try:
            # Handle fractions
            if '/' in quantity_str:
                num, denom = quantity_str.split('/')
                quantity = float(num.strip()) / float(denom.strip())
            else:
                quantity = float(quantity_str.strip())
        except ValueError:
            # If parsing fails, default to 1
            quantity = 1
    
    # Process unit if it exists
    if unit_str:
        unit = unit_str.strip()
    
    return {
        'amount': quantity,
        'unit': unit,
        'name': name.strip()
    }

def normalize_unit(unit):
    """Normalize units to standard forms."""
    unit = unit.lower().strip()
    
    # Volume units
    if unit in ['tsp', 'teaspoon', 'teaspoons']:
        return 'tsp'
    if unit in ['tbsp', 'tablespoon', 'tablespoons', 'tbs', 'tbl']:
        return 'tbsp'
    if unit in ['cup', 'cups', 'c']:
        return 'cup'
    if unit in ['oz', 'ounce', 'ounces', 'fl oz', 'fluid ounce', 'fluid ounces']:
        return 'oz'
    if unit in ['ml', 'milliliter', 'milliliters', 'millilitre', 'millilitres']:
        return 'ml'
    if unit in ['l', 'liter', 'liters', 'litre', 'litres']:
        return 'liter'
    
    # Weight units
    if unit in ['g', 'gram', 'grams']:
        return 'g'
    if unit in ['kg', 'kilogram', 'kilograms']:
        return 'kg'
    if unit in ['lb', 'pound', 'pounds']:
        return 'lb'
    
    # Generic counts
    if unit in ['', 'whole', 'piece', 'pieces', 'unit', 'units', 'count']:
        return ''
    
    return unit

def normalize_ingredient_name(name):
    """Normalize ingredient names by removing preparation words."""
    return name.lower()\
        .replace('fresh ', '')\
        .replace('frozen ', '')\
        .replace('dried ', '')\
        .replace('ground ', '')\
        .replace('chopped ', '')\
        .replace('sliced ', '')\
        .replace('diced ', '')\
        .replace('minced ', '')\
        .replace('grated ', '')\
        .replace('shredded ', '')\
        .strip()

def categorize_ingredient(name):
    """Categorize ingredients into common grocery categories."""
    name = name.lower()
    
    # Produce
    if re.search(r'lettuce|spinach|kale|arugula|cabbage|carrot|onion|garlic|potato|tomato|pepper|cucumber|zucchini|squash|pumpkin|broccoli|cauliflower|corn|pea|bean|lentil|fruit|apple|banana|orange|berry|lemon|lime|herb|cilantro|parsley|basil|mint|thyme|rosemary|avocado|mushroom', name):
        return 'Produce'
    
    # Dairy
    if re.search(r'milk|cream|cheese|yogurt|butter|egg|margarine', name):
        return 'Dairy'
    
    # Meat
    if re.search(r'beef|steak|chicken|pork|ham|bacon|sausage|turkey|meat|lamb|veal', name):
        return 'Meat'
    
    # Seafood
    if re.search(r'fish|salmon|tuna|shrimp|prawn|crab|lobster|clam|mussel|oyster|scallop|seafood', name):
        return 'Seafood'
    
    # Baking & Spices
    if re.search(r'flour|sugar|baking powder|baking soda|yeast|salt|pepper|spice|cinnamon|vanilla|cocoa|chocolate|extract', name):
        return 'Baking & Spices'
    
    # Grains & Pasta
    if re.search(r'rice|pasta|noodle|spaghetti|macaroni|bread|cereal|oat|quinoa|barley|grain', name):
        return 'Grains & Pasta'
    
    # Canned Goods
    if re.search(r'can|canned|jar|preserved|soup|broth|stock', name):
        return 'Canned Goods'
    
    # Frozen
    if re.search(r'frozen|ice cream|popsicle', name):
        return 'Frozen'
    
    # Condiments & Sauces
    if re.search(r'sauce|ketchup|mustard|mayo|mayonnaise|vinegar|oil|dressing|syrup|honey|jam|jelly', name):
        return 'Condiments & Sauces'
    
    # Beverages
    if re.search(r'water|juice|soda|tea|coffee|wine|beer|alcohol|drink', name):
        return 'Beverages'
    
    # Snacks
    if re.search(r'chip|cracker|nut|seed|snack|popcorn|pretzel', name):
        return 'Snacks'
    
    # Default
    return 'Other'

def standardize_measurement(amount, unit, name):
    """Standardize measurements to common units."""
    # This is a simplified version - a production system would need more robust conversion logic
    # For example, converting between metric and imperial, handling density-dependent conversions, etc.
    
    # Format the amount for display
    amount_str = str(int(amount)) if amount == int(amount) else str(amount)
    
    # Return as is for now, with an option to implement more conversions later
    return {
        'amount': amount,
        'unit': unit,
        'standardized_display': f"{amount_str} {unit} {name}".strip()
    }

def format_ingredient(amount, unit, name):
    """Format ingredient for display."""
    amount_str = str(int(amount)) if amount == int(amount) else str(amount)
    return f"{amount_str} {unit} {name}".strip()

@shopping_list_bp.route('/generate', methods=['POST'])
def generate_shopping_list():
    """Generate a shopping list from a list of recipes."""
    try:
        data = request.get_json()
        
        if not data or 'recipes' not in data:
            return jsonify({
                'error': 'No recipes provided'
            }), 400
        
        recipes = data['recipes']
        all_ingredients = []
        
        # Extract all ingredients from all recipes
        for recipe in recipes:
            recipe_id = recipe.get('id')
            if not recipe_id:
                continue
                
            ingredients = recipe.get('extendedIngredients', [])
            for ingredient in ingredients:
                # Handle different ingredient formats
                if isinstance(ingredient, str):
                    # Parse from string
                    parsed = parse_ingredient(ingredient)
                    parsed['recipeId'] = recipe_id
                    all_ingredients.append(parsed)
                else:
                    # Already structured
                    name = normalize_ingredient_name(ingredient.get('name', ''))
                    
                    # Get amount
                    amount = ingredient.get('amount', 1)
                    if isinstance(amount, str):
                        # Parse fractions or other formatted amounts
                        try:
                            if '/' in amount:
                                num, denom = amount.split('/')
                                amount = float(num.strip()) / float(denom.strip())
                            else:
                                amount = float(amount.strip())
                        except (ValueError, TypeError):
                            amount = 1
                    
                    # Get unit
                    unit = normalize_unit(ingredient.get('unit', ''))
                    
                    all_ingredients.append({
                        'name': name,
                        'amount': amount,
                        'unit': unit,
                        'recipeId': recipe_id
                    })
        
        # Aggregate ingredients
        aggregated = {}
        
        for ingredient in all_ingredients:
            name = ingredient['name']
            amount = ingredient['amount']
            unit = ingredient['unit']
            recipe_id = ingredient['recipeId']
            
            # Create a key based on normalized name and unit
            key = f"{name}|{unit}"
            
            if key in aggregated:
                # Update existing ingredient
                aggregated[key]['amount'] += amount
                
                # Add recipe reference if not already present
                if recipe_id not in aggregated[key]['recipeIds']:
                    aggregated[key]['recipeIds'].append(recipe_id)
            else:
                # Create new ingredient entry
                standardized = standardize_measurement(amount, unit, name)
                
                # Categorize the ingredient
                category = categorize_ingredient(name)
                
                # Format the amount for display - don't include recipe ID
                amount_str = str(int(amount)) if amount == int(amount) else str(amount)
                
                aggregated[key] = {
                    'id': key,  # Use the key as the ID
                    'name': name,
                    'amount': amount,
                    'unit': unit,
                    'originalAmount': amount,
                    'originalUnit': unit,
                    'standardizedDisplay': standardized['standardized_display'],
                    'category': category,
                    'checked': False,
                    'recipeIds': [recipe_id]
                }
        
        # Convert to list and sort by category then name
        shopping_list = list(aggregated.values())
        shopping_list.sort(key=lambda x: (x['category'], x['name']))
        
        return jsonify({
            'shopping_list': shopping_list
        })
    
    except Exception as e:
        logger.error(f"Error generating shopping list: {str(e)}")
        return jsonify({
            'error': 'An error occurred while generating the shopping list',
            'details': str(e)
        }), 500 