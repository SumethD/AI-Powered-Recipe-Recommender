#!/usr/bin/env python
"""
Test script to verify our backend fix for the "1 " prefix issue in the shopping list.
This simulates the processing done in shopping_list_routes.py.
"""

import re

def test_prefix_fix():
    """Test our updated fix for the "1 " prefix issue in the shopping list."""
    
    # Sample shopping list items with the "1 " prefix issue
    sample_items = [
        {
            "id": "123",
            "display_text": "1 1 teaspoon of salt",
            "standardizedDisplay": "1 g"
        },
        {
            "id": "456",
            "display_text": "1 ½ cup sugar",
            "standardizedDisplay": "1 ml"
        },
        {
            "id": "789",
            "display_text": "1 2 tablespoons water",
            "standardizedDisplay": "1 2 tbsp water"
        },
        {
            "id": "101",
            "display_text": "1 sunflower oil for frying",
            "standardizedDisplay": "1 g"
        }
    ]
    
    print("\n===== TESTING BACKEND PREFIX FIX =====\n")
    
    # Apply the updated fix to each item
    for item in sample_items:
        print(f"Original: {item['display_text']}")
        
        # Apply our updated fix for the "1 " prefix
        if re.match(r'^1\s+', item['display_text']):
            # Get the next part after "1 "
            next_part = item['display_text'][2:].strip()
            
            # Simply remove the "1 " prefix for all cases
            item['display_text'] = next_part
            print(f"After prefix removal: {item['display_text']}")
        
        # Fix standardizedDisplay too
        if 'standardizedDisplay' in item and re.match(r'^1\s+', item['standardizedDisplay']):
            # Get the next part after "1 "
            next_part = item['standardizedDisplay'][2:].strip()
            
            # Simply remove the "1 " prefix for all cases
            item['standardizedDisplay'] = next_part
            print(f"Fixed standardized: {item['standardizedDisplay']}")
            
            # If we end up with just "g" or "ml", use a better display
            if item['standardizedDisplay'] in ["g", "ml"]:
                # In a real scenario, we'd use item['formatted_amount']
                # For our test, we'll use a placeholder value
                std_unit = item['standardizedDisplay']
                item['standardizedDisplay'] = f"0.5 {std_unit} {item['display_text']}"
                print(f"Fixed empty standardized: {item['standardizedDisplay']}")
        
        print(f"Final: {item['display_text']}")
        print(f"Final standardized: {item['standardizedDisplay']}\n")
    
    # Print the final shopping list
    print("\n===== FINAL SHOPPING LIST =====\n")
    for item in sample_items:
        print(f"• {item['display_text']}")
        print(f"  Standardized: {item['standardizedDisplay']}")

if __name__ == "__main__":
    test_prefix_fix() 