#!/usr/bin/env python
"""
Test script to verify the fix for the "1 " prefix issue in the shopping list.
This script simulates the shopping list route's behavior with our fix.
"""

import re
import json

def test_prefix_fix():
    """Test the fix for the "1 " prefix issue in the shopping list."""
    
    # Sample shopping list items with the "1 " prefix issue
    sample_items = [
        {
            "id": "123",
            "display_text": "1 cooked rice to serve",
            "standardizedDisplay": "1 g"
        },
        {
            "id": "456",
            "display_text": "1 1 1/2 tbsp low sodium soy sauce",
            "standardizedDisplay": "1 ml"
        },
        {
            "id": "789",
            "display_text": "1 2 tbsp water",
            "standardizedDisplay": "1 ml"
        },
        {
            "id": "101",
            "display_text": "1 1/2 cup cold water",
            "standardizedDisplay": "1 ml"
        }
    ]
    
    print("\n===== TESTING PREFIX FIX =====\n")
    
    # Apply the fix to each item
    for item in sample_items:
        print(f"Original: {item['display_text']}")
        
        # Apply the fix from shopping_list_routes.py
        match = re.match(r'^(\d+)\s+(.+)$', item['display_text'])
        if match and match.group(1) in [item['id'], str(item['id'])]:
            # Remove the ID from the beginning
            item['display_text'] = match.group(2)
            print(f"After ID check: {item['display_text']}")
        
        # Apply our new fix for the "1 " prefix
        if re.match(r'^1\s+', item['display_text']) and not re.match(r'^1\s+\d', item['display_text']):
            # Only remove if it's "1 " followed by something that's not a number
            # This preserves valid measurements like "1 1/2 cup" or "1 2 tbsp"
            item['display_text'] = re.sub(r'^1\s+', '', item['display_text'])
            print(f"After prefix fix: {item['display_text']}")
        
        print(f"Final: {item['display_text']}\n")
    
    # Print the final shopping list
    print("\n===== FINAL SHOPPING LIST =====\n")
    for item in sample_items:
        print(f"• {item['display_text']}")
        print(f"  Standardized: {item['standardizedDisplay']}")

if __name__ == "__main__":
    test_prefix_fix() 