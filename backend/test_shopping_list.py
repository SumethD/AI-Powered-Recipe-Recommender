import unittest
import json
import sys
import os
from services.shopping_list import generate_shopping_list, normalize_ingredient_name, convert_to_standard_unit

# Sample test data
TEST_RECIPES = [
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
            {
                "name": "granulated sugar",
                "amount": 1.5,
                "unit": "cups"
            },
            {
                "name": "unsalted butter",
                "amount": 0.5,
                "unit": "cup"
            },
            {
                "name": "eggs",
                "amount": 2,
                "unit": ""
            },
            {
                "name": "milk",
                "amount": 1,
                "unit": "cup"
            }
        ]
    },
    {
        "id": "456",
        "title": "Pancakes",
        "servings": 4,
        "extendedIngredients": [
            {
                "name": "all-purpose flour",
                "amount": 1,
                "unit": "cup"
            },
            {
                "name": "milk",
                "amount": 0.75,
                "unit": "cup"
            },
            {
                "name": "eggs",
                "amount": 1,
                "unit": ""
            },
            {
                "name": "granulated sugar",
                "amount": 2,
                "unit": "tablespoons"
            },
            {
                "name": "baking powder",
                "amount": 1,
                "unit": "teaspoon"
            }
        ]
    }
]

class TestShoppingList(unittest.TestCase):
    def test_generate_shopping_list(self):
        """Test generating a shopping list from recipes"""
        shopping_list = generate_shopping_list(TEST_RECIPES)
        
        # Check that we have the expected number of items in the shopping list
        # 7 unique ingredients: flour, sugar, butter, eggs, milk, baking powder
        self.assertEqual(len(shopping_list), 6)
        
        # Check that the ingredients were combined properly
        flour_item = next((item for item in shopping_list if 'flour' in item['name'].lower()), None)
        self.assertIsNotNone(flour_item)
        self.assertEqual(flour_item['unit'], 'cups')
        self.assertEqual(float(flour_item['amount']), 3.0)  # 2 cups + 1 cup
        
        milk_item = next((item for item in shopping_list if 'milk' in item['name'].lower()), None)
        self.assertIsNotNone(milk_item)
        self.assertEqual(milk_item['unit'], 'cups')
        self.assertEqual(float(milk_item['amount']), 1.75)  # 1 cup + 0.75
        
        eggs_item = next((item for item in shopping_list if 'egg' in item['name'].lower()), None)
        self.assertIsNotNone(eggs_item)
        self.assertEqual(eggs_item['unit'], 'count')
        self.assertEqual(float(eggs_item['amount']), 3.0)  # 2 + 1
        
        # Verify that items have categories
        for item in shopping_list:
            self.assertIn('category', item)
            self.assertIsNotNone(item['category'])
            self.assertNotEqual(item['category'], '')
    
    def test_normalize_ingredient_name(self):
        """Test normalizing ingredient names"""
        test_cases = [
            ("Fresh Basil", "basil"),
            ("frozen spinach", "spinach"),
            ("Dried Oregano", "oregano"),
            ("Ground Cinnamon", "cinnamon"),
            ("Chopped Onions", "onions"),
            ("Sliced Almonds", "almonds"),
            ("Minced Garlic", "garlic"),
            ("2% Milk", "2% milk"),
            ("Olive Oil, extra virgin", "olive oil, extra virgin"),
            ("Salt, to taste", "salt"),
        ]
        
        for input_name, expected_output in test_cases:
            self.assertEqual(normalize_ingredient_name(input_name), expected_output)
    
    def test_convert_to_standard_unit(self):
        """Test converting units to standard measurements"""
        test_cases = [
            # (quantity, unit, ingredient, expected_qty, expected_unit)
            (1, "cup", "flour", 1 * 236.59 * 0.53, "g"),  # 1 cup flour → X g (density 0.53)
            (2, "tablespoons", "sugar", 2 * 14.79 * 0.85, "g"),  # 2 tbsp sugar → X g (density 0.85)
            (1, "cup", "milk", 236.59, "ml"),  # 1 cup milk → X ml (liquid)
            (3, "ounces", "cheddar cheese", 3 * 28.35, "g"),  # 3 oz cheese → X g
            (2, "", "eggs", 2, "count"),  # 2 eggs → 2 count
            (0.5, "teaspoon", "salt", 0.5 * 4.93 * 1.22, "g")  # 0.5 tsp salt → X g (density 1.22)
        ]
        
        for qty, unit, ingredient, expected_qty, expected_unit in test_cases:
            qty_result, unit_result = convert_to_standard_unit(qty, unit, ingredient)
            self.assertEqual(unit_result, expected_unit)
            self.assertAlmostEqual(qty_result, expected_qty, delta=0.1)

if __name__ == "__main__":
    unittest.main() 