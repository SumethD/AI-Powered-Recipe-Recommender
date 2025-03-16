import json
import sys
import os
from services.shopping_list import generate_shopping_list

def test_improved_formatting():
    """Test the improved ingredient formatting"""
    
    # Print startup message
    print("\n**** STARTING TEST ****\n")
    
    # Load test data with edge cases
    try:
        with open('test_data_with_edge_cases.json', 'r') as f:
            data = json.load(f)
        print("Successfully loaded test data")
    except Exception as e:
        print(f"Error loading test data: {e}")
        return
    
    try:
        # Generate shopping list
        print("Generating shopping list...")
        shopping_list = generate_shopping_list(data['recipes'])
        print(f"Generated {len(shopping_list)} items")
        
        # Print results
        print("\n===== SHOPPING LIST WITH IMPROVED FORMATTING =====\n")
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
        
        print("\n===== RAW ITEM DATA =====\n")
        for item in shopping_list:
            print(json.dumps(item, indent=2, ensure_ascii=False))
            print()
            
        print("**** TEST COMPLETE ****")
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Make sure we're running from the backend directory
    if not os.path.exists('services/shopping_list.py'):
        print("Error: Run this script from the backend directory")
        sys.exit(1)
    
    # Call the test function
    print("Starting improved formatting test")    
    test_improved_formatting() 
    print("Test completed") 