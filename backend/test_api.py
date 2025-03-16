import requests
import json
import sys
import re

def test_shopping_list_api():
    """Test the shopping list API endpoint"""
    url = "http://localhost:5000/api/shopping-list/generate"
    
    # Test data with edge cases similar to what we've been testing with
    data = {
        "recipes": [
            {
                "id": "123",
                "title": "Test Recipe with Problematic Ingredients",
                "servings": 4,
                "extendedIngredients": [
                    {
                        "name": "2 stalks celery, finely chopped",
                        "amount": 2,
                        "unit": ""
                    },
                    {
                        "name": "6-8 slices of bread (gluten-free if preferred)",
                        "amount": 6,
                        "unit": ""
                    },
                    {
                        "name": "sea salt, to taste",
                        "amount": 1,
                        "unit": "teaspoon"
                    },
                    {
                        "name": "1 can hearts of palm, drained and rinsed",
                        "amount": 1,
                        "unit": "can"
                    },
                    {
                        "name": "vegan mayo (more if needed)",
                        "amount": 0.33,
                        "unit": "cup"
                    },
                    {
                        "name": "dulce or kelp granules/flakes (*see note)",
                        "amount": 1,
                        "unit": "teaspoon"
                    },
                    {
                        "name": "dill",
                        "amount": 0.5,
                        "unit": "teaspoon"
                    },
                    {
                        "name": "sriracha sauce",
                        "amount": 2,
                        "unit": "tablespoons"
                    }
                ]
            }
        ]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        # Send request to API
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        # Check response status
        if response.status_code == 200:
            results = response.json()
            
            if results["success"]:
                shopping_list = results["shoppingList"]
                
                print(f"\n===== SHOPPING LIST API RESPONSE =====\n")
                print(f"Total items: {len(shopping_list)}\n")
                
                # Group items by category
                categories = {}
                for item in shopping_list:
                    category = item['category']
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(item)
                
                # Print items by category
                for category, items in sorted(categories.items()):
                    print(f"\n{category} ({len(items)})")
                    print("-" * 40)
                    
                    for item in items:
                        # Print display text
                        print(f"• {item['display_text']}")
                        print(f"  Standardized: {item['standardizedDisplay']}")
                        
                        # Check if display_text starts with an ID-like number
                        if re.match(r'^\d+\s+', item['display_text']):
                            print(f"  ⚠️ WARNING: Display text starts with a number: {item['display_text']}")
                
                # Check for key formatting improvements we made
                check_formatting_improvements(shopping_list)
                
                return True
            else:
                print(f"API error: {results.get('error', 'Unknown error')}")
                return False
        else:
            print(f"API returned status code {response.status_code}")
            print(response.text)
            return False
    except requests.exceptions.ConnectionError:
        print("Connection error: Make sure the API server is running")
        return False

def check_formatting_improvements(shopping_list):
    """Check for the key formatting improvements we made"""
    print("\n===== CHECKING FORMATTING IMPROVEMENTS =====\n")
    
    # Check for count-based items (Can/Cans, Slice/Slices)
    count_items = [item for item in shopping_list if item['unit'] == 'count']
    if count_items:
        print("✓ Found count-based items:")
        for item in count_items:
            print(f"  • {item['display_text']}")
            # Check proper pluralization
            if item['amount'] == 1 and "Cans of" in item['display_text']:
                print("  ✗ ERROR: Singular item has plural unit")
            elif item['amount'] > 1 and "Can of" in item['display_text']:
                print("  ✗ ERROR: Plural item has singular unit")
    else:
        print("✗ No count-based items found")
    
    # Check for clean ingredient names
    print("\nChecking for clean ingredient names:")
    for item in shopping_list:
        # Check for redundant unit words in name
        words = item['name'].lower().split()
        if item['unit'] in ['teaspoon', 'tablespoon', 'cup'] and item['unit'] in words:
            print(f"  ✗ Redundant unit in ingredient name: {item['name']}")
        # Check for leading numbers in name
        if words and words[0].isdigit():
            print(f"  ✗ Leading number in ingredient name: {item['name']}")
    
    # Check for fraction formatting
    fraction_items = [item for item in shopping_list if item['formatted_amount'] in ['1/2', '1/4', '3/4', '1/3', '2/3']]
    if fraction_items:
        print("\n✓ Found items with fraction formatting:")
        for item in fraction_items:
            print(f"  • {item['display_text']}")
    else:
        print("\n✗ No items with fraction formatting found")
    
    # Check for proper unit abbreviations
    print("\nChecking for proper unit abbreviations:")
    for item in shopping_list:
        if item['unit'] == 'teaspoon' and 'tsp' not in item['display_text']:
            print(f"  ✗ Missing tsp abbreviation: {item['display_text']}")
        elif item['unit'] == 'tablespoon' and 'tbsp' not in item['display_text']:
            print(f"  ✗ Missing tbsp abbreviation: {item['display_text']}")
            
    # Check for standardized display values
    print("\nChecking for standardized display values:")
    for item in shopping_list:
        if item['standardizedDisplay'] in ["1 g", "1 ml"]:
            print(f"  ✗ Generic standardized value: {item['standardizedDisplay']} for {item['name']}")
        
        # Check for leading "1 " in standardizedDisplay (when it's not actually 1)
        if re.match(r'^1\s+\w+\s+', item['standardizedDisplay']) and item['amount'] != 1:
            print(f"  ✗ Standardized display starts with '1' but amount is {item['amount']}: {item['standardizedDisplay']}")

def clean_shopping_list_format(input_text):
    """
    Clean the shopping list format by removing numeric prefixes (like '1 ')
    that appear at the beginning of ingredient lines
    """
    print("\n===== CLEANED SHOPPING LIST FORMAT =====\n")
    
    lines = input_text.strip().split('\n')
    cleaned_lines = []
    
    # Detect the pattern: we expect lines that start with a lone number
    # followed by actual ingredient information
    for line in lines:
        # Skip category headers, standardized lines, and blank lines
        if (line.strip() == "" or 
            'Standardized:' in line or 
            re.match(r'^[\w\s&]+\(\d+\)$', line)):
            cleaned_lines.append(line)
            print(f"{line}")
            continue
        
        # Check for lines that start with a digit followed by a space
        # This will identify our problematic lines
        if re.match(r'^\d+\s+', line):
            # The challenging part is distinguishing between:
            # "1 " as a prefix vs "1 " as part of a measurement like "1 cup"
            
            # If it starts with "1 " and is followed by another number,
            # it's likely a valid measurement (e.g., "1 1/2 cup" or "1 2 tbsp")
            if re.match(r'^1\s+\d', line):
                # This is a valid quantity, keep it
                cleaned_lines.append(line)
                print(f"{line}")
            else:
                # Check for common measurement words after the leading number
                measurement_words = ["cup", "tbsp", "tsp", "teaspoon", "tablespoon",
                                   "g", "kg", "ml", "l", "oz", "lb", "pound"]
                
                # Extract the first "word" after the leading digit
                # e.g., from "1 cup flour" we get "cup"
                match = re.match(r'^\d+\s+(\w+)', line)
                if match and match.group(1).lower() in measurement_words:
                    # This is a legitimate measurement, keep it
                    cleaned_lines.append(line)
                    print(f"{line}")
                else:
                    # This is likely a prefix we should remove
                    # Remove the leading digit and any spaces after it
                    cleaned_line = re.sub(r'^\d+\s+', '', line)
                    cleaned_lines.append(cleaned_line)
                    print(f"{cleaned_line}")
        else:
            # No leading digit, keep as is
            cleaned_lines.append(line)
            print(f"{line}")
    
    return '\n'.join(cleaned_lines)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--clean":
        # Read from stdin for piped input
        import sys
        input_text = sys.stdin.read()
        clean_shopping_list_format(input_text)
    else:
        test_shopping_list_api() 