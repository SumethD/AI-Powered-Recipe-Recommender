#!/usr/bin/env python
"""
Shopping List Cleaner

This script removes unwanted numeric prefixes from shopping list items.
It can be used to fix formatting issues where numbers appear at the beginning of items.

Usage:
1. Copy your shopping list to a text file
2. Run: python clean_shopping_list.py input.txt > cleaned.txt
   OR
   Run: python clean_shopping_list.py  (to read from stdin)

Author: AI-Powered Recipe Recommender Team
"""

import sys
import re

def clean_shopping_list(input_text):
    """
    Clean the shopping list format by removing numeric prefixes
    that appear at the beginning of ingredient lines
    """
    lines = input_text.strip().split('\n')
    cleaned_lines = []
    
    # Process each line
    for line in lines:
        # Skip blank lines
        if line.strip() == "":
            cleaned_lines.append(line)
            continue
            
        # Skip category headers (e.g., "Produce (5)")
        if re.match(r'^[\w\s&]+\(\d+\)$', line):
            cleaned_lines.append(line)
            continue
        
        # Check for the "1 * " pattern at the beginning of the line
        if line.startswith("1 * "):
            # Remove the "1 * " prefix
            cleaned_line = line[4:]  # Skip "1 * " (4 characters)
            cleaned_lines.append(cleaned_line)
            print(f"Removing '1 * ' prefix from: {line}", file=sys.stderr)
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
        input_text = sys.stdin.read()
    
    # Clean the shopping list
    cleaned_text = clean_shopping_list(input_text)
    
    # Output the cleaned text
    print(cleaned_text)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 