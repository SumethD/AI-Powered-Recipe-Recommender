import re
from typing import Dict, List, Optional, Union, Any, Tuple
import logging
import uuid

# Set up logging
logger = logging.getLogger(__name__)

# Define conversion factors for common ingredients and units
# Conversion to standard units (solids to grams, liquids to milliliters)
VOLUME_TO_ML = {
    'teaspoon': 4.93,
    'tsp': 4.93,
    'tablespoon': 14.79,
    'tbsp': 14.79,
    'fluid ounce': 29.57,
    'fl oz': 29.57,
    'cup': 236.59,
    'cups': 236.59,
    'pint': 473.18,
    'pt': 473.18,
    'quart': 946.35,
    'qt': 946.35,
    'gallon': 3785.41,
    'gal': 3785.41,
    'ml': 1,
    'milliliter': 1,
    'milliliters': 1,
    'l': 1000,
    'liter': 1000,
    'liters': 1000
}

WEIGHT_TO_GRAMS = {
    'gram': 1,
    'g': 1,
    'grams': 1,
    'kilogram': 1000,
    'kg': 1000,
    'kilograms': 1000,
    'ounce': 28.35,
    'oz': 28.35,
    'ounces': 28.35,
    'pound': 453.59,
    'lb': 453.59,
    'pounds': 453.59
}

# Density of common ingredients (g/ml) for volume to weight conversion
INGREDIENT_DENSITY = {
    'water': 1.0,
    'milk': 1.03,
    'olive oil': 0.92,
    'vegetable oil': 0.92,
    'oil': 0.92,
    'flour': 0.53,
    'all-purpose flour': 0.53,
    'sugar': 0.85,
    'granulated sugar': 0.85,
    'brown sugar': 0.72,
    'salt': 1.22,
    'butter': 0.91,
    'honey': 1.42,
    'maple syrup': 1.32,
    'rice': 0.75,
    'oats': 0.42,
    'yogurt': 1.03
}

# Unit display preferences
PREFERRED_UNITS = {
    'flour': 'cups',
    'sugar': 'cups',
    'oil': 'tablespoons',
    'butter': 'tablespoons',
    'salt': 'teaspoons',
    'milk': 'cups',
    'water': 'cups',
    'chocolate chips': 'cups',
    'oats': 'cups',
    'rice': 'cups'
}

# Add these count units to the recognized count items
COUNT_UNITS = [
    "", "whole", "piece", "pieces", "count", "can", "cans", "slice", "slices", 
    "stalk", "stalks", "clove", "cloves", "bunch", "bunches", "sprig", "sprigs",
    "leaf", "leaves", "ear", "ears", "head", "heads", "loaf", "loaves"
]

def normalize_ingredient_name(name: str) -> str:
    """
    Normalize ingredient name for better matching
    """
    # Convert to lowercase and remove extra whitespace
    name = name.lower().strip()
    
    # Remove common prefixes like "fresh", "frozen", "dried"
    prefixes = ["fresh ", "frozen ", "dried ", "ground ", "chopped ", "sliced ", "diced ",
               "minced ", "grated ", "shredded ", "whole "]
    for prefix in prefixes:
        if name.startswith(prefix):
            name = name.replace(prefix, "", 1)
    
    # Remove common suffixes
    suffixes = [", sliced", ", chopped", ", diced", ", minced", ", grated", 
               ", for garnish", ", to taste", ", optional"]
    for suffix in suffixes:
        if suffix in name:
            name = name.replace(suffix, "")
            
    return name.strip()

def is_liquid(name: str) -> bool:
    """
    Determine if an ingredient is a liquid based on its name
    """
    liquid_words = ["water", "milk", "juice", "oil", "vinegar", "wine", "beer", "stock", 
                   "broth", "cream", "sauce", "syrup", "honey", "liquor", "vodka", "whiskey"]
    
    for word in liquid_words:
        if word in name:
            return True
    return False

def determine_best_unit(name: str, is_liquid_flag: bool, quantity: float, original_unit: str = None) -> str:
    """
    Determine the best unit for displaying an ingredient
    
    Args:
        name: The ingredient name
        is_liquid_flag: Whether the ingredient is a liquid
        quantity: The quantity of the ingredient
        original_unit: The original unit provided (if any)
        
    Returns:
        The best unit for display
    """
    # Original unit, if provided and it's a count unit, should be preferred
    if original_unit and original_unit.lower() in COUNT_UNITS:
        return "count"
        
    # Check for count items based on the name
    normalized_name = normalize_ingredient_name(name)
    
    # Apply regex patterns to identify count patterns
    count_patterns = [
        r"\bcan(s)?\b", r"\bstalk(s)?\b", r"\bslice(s)?\b", r"\bclove(s)?\b",
        r"\bbunch(es)?\b", r"\bsprig(s)?\b", r"\bleaf|leaves\b", r"\bear(s)?\b",
        r"\bhead(s)?\b", r"\bloaf|loaves\b", r"\bwhole\b", r"\bpiece(s)?\b"
    ]
    
    # Check if name contains count patterns
    for pattern in count_patterns:
        if re.search(pattern, normalized_name, re.IGNORECASE):
            return "count"
    
    # Check against count items list
    count_items = ["egg", "eggs", "banana", "apple", "orange", "potato", "onion", "tomato"]
    for item in count_items:
        if item in normalized_name:
            return "count"
            
    # Check if the ingredient has a preferred unit
    for key in PREFERRED_UNITS:
        if key in normalized_name:
            return PREFERRED_UNITS[key]
    
    # If no preferred unit, choose based on type and quantity
    if is_liquid_flag:
        if quantity < 15:  # Less than 15ml
            return "teaspoon"
        elif quantity < 60:  # Less than 60ml
            return "tablespoon"
        elif quantity < 1000:  # Less than 1L
            return "cup"
        else:
            return "liter"
    else:  # For solids
        if quantity < 10:  # Tiny amount
            return "teaspoon"
        elif quantity < 30:  # Small amount
            return "tablespoon"
        elif quantity < 500:  # Medium amount
            return "cup" if normalized_name in ["flour", "sugar", "rice", "oats"] else "grams"
        else:
            return "kg"

def convert_to_standard_unit(quantity: float, unit: str, ingredient_name: str) -> Tuple[float, str]:
    """
    Convert a quantity and unit to a standardized measurement
    """
    if not unit:  # Handle count items like "2 eggs"
        # Check if it's a whole item that should be counted
        clean_name = clean_ingredient_name(ingredient_name)
        if any(count_word in clean_name.lower() for count_word in ["can", "stalk", "slice", "clove", "bunch", "sprig", "leaf", "head", "loaf"]):
            return quantity, "count"
        
    unit = unit.lower().strip()
    
    # Handle special cases for count items
    if unit in COUNT_UNITS:
        return quantity, "count"
    
    # Normalize tablespoon/tablespoons
    if unit in ["tablespoon", "tablespoons"]:
        unit = "tbsp"
    
    # Normalize teaspoon/teaspoons
    if unit in ["teaspoon", "teaspoons"]:
        unit = "tsp"
    
    # Determine if it's a liquid
    liquid = is_liquid(ingredient_name)
    
    # Convert to standard unit
    if liquid and unit in VOLUME_TO_ML:
        # Convert to ml
        return quantity * VOLUME_TO_ML[unit], "ml"
    elif not liquid and unit in WEIGHT_TO_GRAMS:
        # Convert to grams
        return quantity * WEIGHT_TO_GRAMS[unit], "g"
    elif not liquid and unit in VOLUME_TO_ML:
        # Convert volume to weight if possible
        normalized_name = normalize_ingredient_name(ingredient_name)
        
        # Try to find the density of the ingredient
        density = None
        for key, value in INGREDIENT_DENSITY.items():
            if key in normalized_name:
                density = value
                break
        
        if density:
            # Convert volume to ml, then to grams using density
            ml = quantity * VOLUME_TO_ML[unit]
            return ml * density, "g"
        else:
            # Just convert to ml if we don't know the density
            return quantity * VOLUME_TO_ML[unit], "ml"
    
    # If we can't convert, return as is
    logger.warning(f"Could not standardize unit '{unit}' for '{ingredient_name}'")
    return quantity, unit

def format_quantity(quantity: float, unit: str) -> str:
    """
    Format a quantity for display
    """
    # For count items, always use whole numbers
    if unit == "count":
        return str(int(quantity)) if isinstance(quantity, float) and quantity.is_integer() else f"{quantity:.1f}"
    
    # For small quantities, show more decimal places
    if quantity < 10:
        # Use fractions for common values
        if abs(quantity - 0.25) < 0.01:
            return "1/4"
        elif abs(quantity - 0.5) < 0.01:
            return "1/2"
        elif abs(quantity - 0.75) < 0.01:
            return "3/4"
        elif abs(quantity - 0.33) < 0.01:
            return "1/3"
        elif abs(quantity - 0.67) < 0.01:
            return "2/3"
        else:
            return f"{quantity:.2f}".rstrip('0').rstrip('.')
    else:
        # For larger values, round to 1 decimal place
        return f"{quantity:.1f}".rstrip('0').rstrip('.')

def convert_from_standard_unit(quantity: float, std_unit: str, target_unit: str, ingredient_name: str) -> float:
    """
    Convert a quantity from a standard unit to a display unit
    """
    if std_unit == "count" or target_unit == "count":
        return quantity
    
    # Convert from standard to target
    if std_unit == "ml" and target_unit in VOLUME_TO_ML:
        return quantity / VOLUME_TO_ML[target_unit]
    elif std_unit == "g" and target_unit in WEIGHT_TO_GRAMS:
        return quantity / WEIGHT_TO_GRAMS[target_unit]
    elif std_unit == "g" and target_unit in VOLUME_TO_ML:
        # Converting weight to volume
        normalized_name = normalize_ingredient_name(ingredient_name)
        
        # Try to find the density of the ingredient
        density = None
        for key, value in INGREDIENT_DENSITY.items():
            if key in normalized_name:
                density = value
                break
        
        if density:
            # Convert g to ml using density, then to target volume unit
            ml = quantity / density
            return ml / VOLUME_TO_ML[target_unit]
    
    # Return as is if conversion not possible
    return quantity

def clean_ingredient_name(name: str) -> str:
    """
    Clean up an ingredient name by removing unnecessary parts.
    
    Args:
        name: The ingredient name to clean
        
    Returns:
        The cleaned ingredient name
    """
    # Convert to lowercase for easier processing
    name_lower = name.lower()
    
    # Remove any unit words from beginning of the ingredient name
    unit_words = COUNT_UNITS + ["teaspoon", "tablespoon", "cup", "tsp", "tbsp", 
                               "ounce", "gram", "milliliter", "liter", "pound", "kilogram"]
    
    for unit in unit_words:
        if name_lower.startswith(unit.lower() + " "):
            name = name[len(unit) + 1:]
            break
            
        # Also check for plural forms
        if unit != "tsp" and unit != "tbsp" and name_lower.startswith(unit.lower() + "s "):
            name = name[len(unit) + 2:]
            break
    
    # Remove common prefixes that aren't part of the actual ingredient name
    prefixes_to_remove = [
        r'^\d+\s+', # Remove leading numbers like "1 " 
        r'^\d+\s*-\s*\d+\s+', # Remove ranges like "6-8 " at the beginning
        r'^\d+\s*to\s*\d+\s+', # Remove ranges like "6 to 8 " at the beginning
        r'^[\d/]+ cups?\s+', # Remove leading quantities with cups
        r'^[\d/]+ tablespoons?\s+', # Remove leading quantities with tablespoons
        r'^[\d/]+ teaspoons?\s+', # Remove leading quantities with teaspoons
        r'^[\d/]+ tsps?\s+', # Remove leading quantities with tsp
        r'^[\d/]+ tbsps?\s+', # Remove leading quantities with tbsp
        r'^[\d/]+ ounces?\s+', # Remove leading quantities with ounces
        r'^[\d/]+ oz\s+', # Remove leading quantities with oz
        r'^[\d/]+ pounds?\s+', # Remove leading quantities with pounds
        r'^[\d/]+ lbs?\s+', # Remove leading quantities with lbs
        r'^[\d/]+ kilograms?\s+', # Remove leading quantities with kilograms
        r'^[\d/]+ grams?\s+', # Remove leading quantities with grams
        r'^[\d/]+ g\s+', # Remove leading quantities with g
        r'^[\d/]+ milliliters?\s+', # Remove leading quantities with milliliters
        r'^[\d/]+ ml\s+', # Remove leading quantities with ml
        r'^[\d/]+ liters?\s+', # Remove leading quantities with liters
        r'^[\d/]+ l\s+', # Remove leading quantities with l
        r'^[\d/]+ cans?\s+of\s+', # Remove leading quantities with cans of
        r'^[\d/]+ cans?\s+', # Remove leading quantities with cans
        r'^[\d/]+ slices?\s+of\s+', # Remove leading quantities with slices of
        r'^[\d/]+ slices?\s+', # Remove leading quantities with slices
        r'^[\d/]+ stalks?\s+of\s+', # Remove leading quantities with stalks of
        r'^[\d/]+ stalks?\s+', # Remove leading quantities with stalks
        r'^[\d/]+ cloves?\s+of\s+', # Remove leading quantities with cloves of
        r'^[\d/]+ cloves?\s+', # Remove leading quantities with cloves
        r'^[\d/]+ bunche?s?\s+of\s+', # Remove leading quantities with bunches of
        r'^[\d/]+ bunche?s?\s+', # Remove leading quantities with bunches
        r'^[\d/]+ sprigs?\s+of\s+', # Remove leading quantities with sprigs of
        r'^[\d/]+ sprigs?\s+', # Remove leading quantities with sprigs
        r'^[\d/]+ leaves?\s+of\s+', # Remove leading quantities with leaves of
        r'^[\d/]+ leaves?\s+', # Remove leading quantities with leaves
        r'^[\d/]+ heads?\s+of\s+', # Remove leading quantities with heads of
        r'^[\d/]+ heads?\s+', # Remove leading quantities with heads
        r'^[\d/]+\s*-\s*[\d/]+\s+', # Remove ranges like "6-8 " 
        r'^[\d/]+\s*to\s*[\d/]+\s+', # Remove ranges like "1 to 2 "
        r'^for the\s+', # Remove "for the" prefix
        r'^for\s+', # Remove "for" prefix 
        r'^the\s+', # Remove "the" prefix
        r'^of\s+', # Remove "of" prefix
        r'^approximately\s+', # Remove "approximately" prefix
        r'^about\s+', # Remove "about" prefix
        r'^around\s+', # Remove "around" prefix
        r'^or so\s+', # Remove "or so" prefix
        r'^to taste\s+', # Remove "to taste" prefix
    ]
    
    # Remove count unit words at the beginning of the name
    for unit in COUNT_UNITS:
        # Match full word boundaries to avoid matching substrings
        pattern = r'^' + re.escape(unit) + r'\b\s*'
        if re.search(pattern, name_lower):
            name = re.sub(pattern, '', name, flags=re.IGNORECASE)
    
    # Apply each prefix pattern
    for pattern in prefixes_to_remove:
        name = re.sub(pattern, '', name, flags=re.IGNORECASE)
    
    # Remove phrases like "divided", "plus more for garnish", etc.
    suffixes_to_remove = [
        r',?\s+divided$',
        r',?\s+plus more for \w+$',
        r',?\s+plus extra for \w+$',
        r',?\s+plus more as needed$',
        r',?\s+plus extra$',
        r',?\s+optional$',
        r',?\s+to serve$',
        r',?\s+for serving$',
        r',?\s+for garnish$',
        r',?\s+for the top$',
        r',?\s+for decoration$',
        r',?\s+to taste$',
        r',?\s+or to taste$',
        r',?\s+\(divided\)$',
        r',?\s+\(optional\)$',
        r',?\s+\(to serve\)$',
        r',?\s+\(for serving\)$',
        r',?\s+\(for garnish\)$'
    ]
    
    # Apply each suffix pattern
    for pattern in suffixes_to_remove:
        name = re.sub(pattern, '', name, flags=re.IGNORECASE)
    
    # Remove number ranges within the text (like "6-8" in "6-8 slices of bread")
    name = re.sub(r'\b\d+\s*-\s*\d+\b', '', name)
    name = re.sub(r'\b\d+\s*to\s*\d+\b', '', name)
    
    # Capitalize the first letter of each word
    words = name.split()
    if words:
        name = ' '.join(word.capitalize() if not (word.lower() == 'and' or word.lower() == 'or' or word.lower() == 'of' or word.lower() == 'the' or word.lower() == 'with') else word.lower() for word in words)
    
    return name.strip()

def generate_shopping_list(recipes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate a consolidated shopping list from multiple recipes.
    
    Args:
        recipes: List of recipe objects with ingredients and servings
        
    Returns:
        A list of consolidated ingredients with standardized quantities
    """
    # Validate input
    if not recipes:
        logger.warning("No recipes provided for shopping list generation")
        return []
    
    # Dictionary to store standardized ingredients
    standardized_ingredients = {}
    
    # Process each recipe
    for recipe in recipes:
        # Get recipe servings
        servings = recipe.get('servings', 1)
        if not servings or servings <= 0:
            servings = 1
            
        # Get ingredients
        ingredients = recipe.get('extendedIngredients', [])
        if not ingredients:
            logger.warning(f"No ingredients found for recipe {recipe.get('id', 'unknown')}")
            continue
            
        # Process each ingredient
        for ingredient in ingredients:
            name = ingredient.get('name', '')
            if not name:
                continue
                
            # Clean and normalize ingredient name
            clean_name = clean_ingredient_name(name)
            normalized_name = normalize_ingredient_name(name)
            
            # If clean_name is empty, use the original name
            if not clean_name:
                clean_name = name
            
            # Get quantity and unit
            quantity = ingredient.get('amount', 0)
            if isinstance(quantity, str):
                try:
                    quantity = float(quantity)
                except ValueError:
                    logger.warning(f"Invalid quantity for {name}: {quantity}")
                    quantity = 0
                    
            unit = ingredient.get('unit', '')
            
            # Skip if no quantity
            if quantity <= 0:
                continue
                
            # Adjust quantity based on servings if needed
            # quantity = quantity * (desired_servings / servings)
            
            # Convert to standard unit
            std_quantity, std_unit = convert_to_standard_unit(quantity, unit, normalized_name)
            
            # Add to standardized ingredients
            if normalized_name in standardized_ingredients:
                # Make sure the units match
                existing_std_unit = standardized_ingredients[normalized_name]['std_unit']
                if existing_std_unit != std_unit:
                    # Try to convert between units if they don't match
                    if existing_std_unit == "ml" and std_unit == "g":
                        # Convert ml to g using density
                        density = None
                        for key, value in INGREDIENT_DENSITY.items():
                            if key in normalized_name:
                                density = value
                                break
                                
                        if density:
                            # Convert to g
                            existing_quantity = standardized_ingredients[normalized_name]['std_quantity']
                            standardized_ingredients[normalized_name]['std_quantity'] = existing_quantity * density
                            standardized_ingredients[normalized_name]['std_unit'] = "g"
                        else:
                            # If we can't convert, just keep them separate
                            alt_name = f"{normalized_name} (in {std_unit})"
                            standardized_ingredients[alt_name] = {
                                'name': clean_name,
                                'std_quantity': std_quantity,
                                'std_unit': std_unit,
                                'original_unit': unit,
                                'is_liquid': is_liquid(normalized_name)
                            }
                            continue
                    elif existing_std_unit == "g" and std_unit == "ml":
                        # Keep the existing conversion and add new value in grams
                        density = None
                        for key, value in INGREDIENT_DENSITY.items():
                            if key in normalized_name:
                                density = value
                                break
                                
                        if density:
                            # Convert ml to g
                            std_quantity = std_quantity * density
                            std_unit = "g"
                        else:
                            # If we can't convert, just keep them separate
                            alt_name = f"{normalized_name} (in {std_unit})"
                            standardized_ingredients[alt_name] = {
                                'name': clean_name,
                                'std_quantity': std_quantity,
                                'std_unit': std_unit,
                                'original_unit': unit,
                                'is_liquid': is_liquid(normalized_name)
                            }
                            continue
                
                # Add to existing quantity
                standardized_ingredients[normalized_name]['std_quantity'] += std_quantity
            else:
                # Create new entry
                standardized_ingredients[normalized_name] = {
                    'name': clean_name,
                    'std_quantity': std_quantity,
                    'std_unit': std_unit,
                    'original_unit': unit,
                    'is_liquid': is_liquid(normalized_name)
                }
    
    # Convert standardized ingredients to display format
    shopping_list = []
    for normalized_name, data in standardized_ingredients.items():
        # Determine best display unit
        display_unit = determine_best_unit(
            data['name'], 
            data['is_liquid'], 
            data['std_quantity'],
            data['original_unit']
        )
        
        # Convert to display unit
        display_quantity = convert_from_standard_unit(
            data['std_quantity'], 
            data['std_unit'], 
            display_unit, 
            normalized_name
        )
        
        # Format the quantity for display
        formatted_quantity = format_quantity(display_quantity, display_unit)
        
        # Format the display text based on the unit type
        if display_unit == "count":
            # Check if ingredient name contains count-unit words
            has_unit_in_name = False
            detected_unit = None
            
            for unit in ["can", "slice", "stalk", "clove", "bunch", "sprig", "head"]:
                if unit.lower() in normalized_name.lower():
                    has_unit_in_name = True
                    detected_unit = unit
                    break
                    
            # For count items with recognizable units, format appropriately
            if has_unit_in_name and detected_unit:
                # Remove any unit words from the beginning of the name to avoid duplication
                clean_name = data['name']
                # Check if the unit word (or plural) is at the beginning
                if clean_name.lower().startswith(detected_unit.lower() + " "):
                    clean_name = clean_name[len(detected_unit) + 1:]
                elif clean_name.lower().startswith(detected_unit.lower() + "s "):
                    clean_name = clean_name[len(detected_unit) + 2:]
                
                # Format with proper pluralization based on quantity
                # Convert formatted_quantity to a number for comparison
                try:
                    qty_value = float(formatted_quantity)
                    unit_suffix = '' if qty_value == 1.0 else 's'
                except ValueError:
                    # If it's a fraction like "1/2", use plural
                    unit_suffix = 's'
                
                display_text = f"{formatted_quantity} {detected_unit.capitalize()}{unit_suffix} of {clean_name}"
            else:
                # For count items, don't append a unit
                display_text = f"{formatted_quantity} {data['name']}"
        else:
            # Format unit abbreviations appropriately
            unit_display = display_unit
            if display_unit == "teaspoon":
                unit_display = "tsp"
            elif display_unit == "tablespoon":
                unit_display = "tbsp"
            elif display_unit == "grams":
                unit_display = "g"
            elif display_unit == "milliliters":
                unit_display = "ml"
                
            display_text = f"{formatted_quantity} {unit_display} {data['name']}"
        
        # Format the standardized display
        if data['std_unit'] == "count":
            standardized_display = f"{format_quantity(data['std_quantity'], data['std_unit'])} {data['name']}"
        else:
            standardized_unit = data['std_unit']
            # Ensure we're using the actual standardized quantity, not just "1"
            std_quantity_formatted = format_quantity(data['std_quantity'], data['std_unit'])
            standardized_display = f"{std_quantity_formatted} {standardized_unit} {data['name']}"
        
        # Final cleaning - if a word is duplicated at the beginning of the name (like "teaspoon teaspoon"), remove it
        display_text = re.sub(r'(\b\w+\b)\s+\1\b', r'\1', display_text, flags=re.IGNORECASE)
        
        # Fix duplicate "of" phrases (like "Slices of of Bread")
        display_text = re.sub(r'\bof\s+of\b', 'of', display_text, flags=re.IGNORECASE)
        
        # Generate a unique ID that doesn't conflict with the display
        item_id = str(uuid.uuid4())[:8]  # Use first 8 chars of a UUID
        
        # Add to shopping list
        shopping_list.append({
            'id': item_id,  # Use a random ID instead of a sequential number
            'name': data['name'],
            'amount': display_quantity,
            'formatted_amount': formatted_quantity,
            'unit': display_unit,
            'display_text': display_text,
            'category': determine_category(normalized_name),
            'checked': False,
            'standardizedDisplay': standardized_display
        })
    
    # Sort by category and name
    shopping_list.sort(key=lambda x: (x['category'], x['name']))
    
    return shopping_list

def determine_category(name: str) -> str:
    """
    Determine the category of an ingredient based on its name
    """
    name = name.lower()
    
    # Produce
    if any(word in name for word in ["lettuce", "spinach", "kale", "arugula", "cabbage", "carrot", 
            "onion", "garlic", "potato", "tomato", "pepper", "cucumber", "zucchini", "squash", 
            "pumpkin", "broccoli", "cauliflower", "corn", "pea", "bean", "lentil", "fruit", 
            "apple", "banana", "orange", "berry", "lemon", "lime", "herb", "cilantro", "parsley", 
            "basil", "mint", "thyme", "rosemary", "avocado", "mushroom"]):
        return "Produce"
    
    # Dairy
    if any(word in name for word in ["milk", "cream", "cheese", "yogurt", "butter", "egg", "margarine"]):
        return "Dairy"
    
    # Meat
    if any(word in name for word in ["beef", "steak", "chicken", "pork", "ham", "bacon", "sausage", 
            "turkey", "meat", "lamb", "veal"]):
        return "Meat"
    
    # Seafood
    if any(word in name for word in ["fish", "salmon", "tuna", "shrimp", "prawn", "crab", "lobster", 
            "clam", "mussel", "oyster", "scallop", "seafood"]):
        return "Seafood"
    
    # Baking & Spices
    if any(word in name for word in ["flour", "sugar", "baking powder", "baking soda", "yeast", 
            "salt", "pepper", "spice", "cinnamon", "vanilla", "cocoa", "chocolate", "extract"]):
        return "Baking & Spices"
    
    # Grains & Pasta
    if any(word in name for word in ["rice", "pasta", "noodle", "spaghetti", "macaroni", 
            "bread", "cereal", "oat", "quinoa", "barley", "grain"]):
        return "Grains & Pasta"
    
    # Canned Goods
    if any(word in name for word in ["can", "canned", "jar", "preserved", "soup", "broth", "stock"]):
        return "Canned Goods"
    
    # Frozen
    if any(word in name for word in ["frozen", "ice cream", "popsicle"]):
        return "Frozen"
    
    # Condiments & Sauces
    if any(word in name for word in ["sauce", "ketchup", "mustard", "mayo", "mayonnaise", 
            "vinegar", "oil", "dressing", "syrup", "honey", "jam", "jelly"]):
        return "Condiments & Sauces"
    
    # Beverages
    if any(word in name for word in ["water", "juice", "soda", "tea", "coffee", "wine", 
            "beer", "alcohol", "drink"]):
        return "Beverages"
    
    # Snacks
    if any(word in name for word in ["chip", "cracker", "nut", "seed", "snack", "popcorn", "pretzel"]):
        return "Snacks"
    
    # Default
    return "Other" 