#!/usr/bin/env python
"""
Shopping List Prefix Remover

This script removes unwanted numeric prefixes from shopping list items.
It's a simple utility to fix the formatting of copy-pasted shopping lists.

Usage:
1. Copy your shopping list to a text file
2. Run: python remove_prefix.py input.txt > cleaned.txt
   OR
   Run: python remove_prefix.py  (to read from stdin)

Author: AI-Powered Recipe Recommender Team
"""

import sys
import re

def clean_shopping_list(input_text):
    """
    Remove the unwanted prefixes from each ingredient line
    """
    lines = input_text.strip().split('\n')
    cleaned_lines = []
    
    # Process each line
    for line in lines:
        # Skip blank lines
        if line.strip() == "":
            cleaned_lines.append(line)
            continue
            
        # Skip category headers (e.g., "Baking & Spices (8)")
        if re.match(r'^[\w\s&]+\(\d+\)$', line):
            cleaned_lines.append(line)
            continue
            
        # Skip standardized lines
        if line.strip().startswith("Standardized:"):
            cleaned_lines.append(line)
            continue
        
        # Check for the "1 * " pattern
        if line.startswith("1 * "):
            # Remove the "1 * " prefix
            cleaned_line = line[4:]  # Skip "1 * " (4 characters)
            cleaned_lines.append(cleaned_line)
            continue
        
        # Check for the "1 " prefix followed by another number or fraction
        # This handles cases like "1 1 teaspoon" or "1 1/2 cup" or "1 ½ cup" or "1 5 tablespoons"
        if line.strip().startswith("1 "):
            # Get the next character(s) after "1 "
            next_part = line[2:].strip()
            
            # Check if the next part starts with a number or fraction
            if (re.match(r'^\d', next_part) or 
                re.match(r'^[½⅓⅔¼¾]', next_part) or 
                re.match(r'^\d+/\d+', next_part)):
                # Remove just the "1 " prefix but keep the actual measurement
                cleaned_line = next_part
                cleaned_lines.append(cleaned_line)
            else:
                # Keep line as is if it doesn't follow the pattern
                cleaned_lines.append(line)
        else:
            # Keep line as is
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def main():
    # Read from file if provided, otherwise from stdin
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                input_text = f.read()
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            return 1
    else:
        # Read from stdin
        print("Paste your shopping list below (press Ctrl+D or Ctrl+Z+Enter when done):", file=sys.stderr)
        input_text = sys.stdin.read()
    
    # Clean the shopping list
    cleaned_text = clean_shopping_list(input_text)
    
    # Output the cleaned text
    print(cleaned_text)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 