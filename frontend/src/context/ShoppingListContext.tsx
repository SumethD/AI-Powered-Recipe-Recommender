import React, { createContext, useState, useContext, ReactNode, useEffect } from 'react';
import { Recipe, Ingredient, useRecipes } from './RecipeContext';
import {
  standardizeIngredientMeasurement,
  parseFraction,
  isLiquid,
  formatIngredientMeasurement
} from '../utils/ingredientConverter';

// Define ingredient categories
export enum IngredientCategory {
  Produce = 'Produce',
  Dairy = 'Dairy',
  Meat = 'Meat',
  Seafood = 'Seafood',
  BakingAndSpices = 'Baking & Spices',
  Grains = 'Grains & Pasta',
  Canned = 'Canned Goods',
  Frozen = 'Frozen',
  Condiments = 'Condiments & Sauces',
  Beverages = 'Beverages',
  Snacks = 'Snacks',
  Other = 'Other'
}

// Define shopping list item interface
export interface ShoppingListItem {
  id: string;
  name: string;
  amount: number;
  unit: string;
  standardizedDisplay: string; // New property for standardized display
  originalAmount: number; // Store original amount
  originalUnit: string; // Store original unit
  category: IngredientCategory;
  checked: boolean;
  recipeIds: (number | string)[];  // References to recipes that use this ingredient
}

// Define context type
export interface ShoppingListContextType {
  selectedRecipes: Recipe[];
  shoppingList: ShoppingListItem[];
  totalCount: number;
  checkedCount: number;
  addRecipeToList: (recipe: Recipe) => void;
  removeRecipeFromList: (recipeId: number | string) => void;
  clearShoppingList: () => void;
  generateShoppingList: () => void;
  toggleItemChecked: (itemId: string) => void;
  updateItemAmount: (itemId: string, amount: number) => void;
  removeItemFromList: (itemId: string) => void;
  isRecipeInList: (recipeId: number | string) => boolean;
}

// Create context
const ShoppingListContext = createContext<ShoppingListContextType | null>(null);

// Define provider props
type ShoppingListProviderProps = {
  children: ReactNode;
};

// Helper function to categorize ingredients
const categorizeIngredient = (name: string): IngredientCategory => {
  name = name.toLowerCase();
  
  // Produce
  if (/lettuce|spinach|kale|arugula|cabbage|carrot|onion|garlic|potato|tomato|pepper|cucumber|zucchini|squash|pumpkin|broccoli|cauliflower|corn|pea|bean|lentil|fruit|apple|banana|orange|berry|lemon|lime|herb|cilantro|parsley|basil|mint|thyme|rosemary|avocado|mushroom/i.test(name)) {
    return IngredientCategory.Produce;
  }
  
  // Dairy
  if (/milk|cream|cheese|yogurt|butter|egg|margarine/i.test(name)) {
    return IngredientCategory.Dairy;
  }
  
  // Meat
  if (/beef|steak|chicken|pork|ham|bacon|sausage|turkey|meat|lamb|veal/i.test(name)) {
    return IngredientCategory.Meat;
  }
  
  // Seafood
  if (/fish|salmon|tuna|shrimp|prawn|crab|lobster|clam|mussel|oyster|scallop|seafood/i.test(name)) {
    return IngredientCategory.Seafood;
  }
  
  // Baking & Spices
  if (/flour|sugar|baking powder|baking soda|yeast|salt|pepper|spice|cinnamon|vanilla|cocoa|chocolate|extract/i.test(name)) {
    return IngredientCategory.BakingAndSpices;
  }
  
  // Grains & Pasta
  if (/rice|pasta|noodle|spaghetti|macaroni|bread|cereal|oat|quinoa|barley|grain/i.test(name)) {
    return IngredientCategory.Grains;
  }
  
  // Canned Goods
  if (/can|canned|jar|preserved|soup|broth|stock/i.test(name)) {
    return IngredientCategory.Canned;
  }
  
  // Frozen
  if (/frozen|ice cream|popsicle/i.test(name)) {
    return IngredientCategory.Frozen;
  }
  
  // Condiments & Sauces
  if (/sauce|ketchup|mustard|mayo|mayonnaise|vinegar|oil|dressing|syrup|honey|jam|jelly/i.test(name)) {
    return IngredientCategory.Condiments;
  }
  
  // Beverages
  if (/water|juice|soda|tea|coffee|wine|beer|alcohol|drink/i.test(name)) {
    return IngredientCategory.Beverages;
  }
  
  // Snacks
  if (/chip|cracker|nut|seed|snack|popcorn|pretzel/i.test(name)) {
    return IngredientCategory.Snacks;
  }
  
  // Default
  return IngredientCategory.Other;
};

// Generate a unique ID
const generateId = (): string => {
  return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
};

// Provider component
export const ShoppingListProvider: React.FC<ShoppingListProviderProps> = ({ children }) => {
  const [selectedRecipes, setSelectedRecipes] = useState<Recipe[]>([]);
  const [shoppingList, setShoppingList] = useState<ShoppingListItem[]>([]);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [checkedCount, setCheckedCount] = useState<number>(0);
  
  // Load from localStorage on init
  useEffect(() => {
    try {
      const savedRecipes = localStorage.getItem('selectedRecipes');
      const savedList = localStorage.getItem('shoppingList');
      
      if (savedRecipes) {
        setSelectedRecipes(JSON.parse(savedRecipes));
      }
      
      if (savedList) {
        setShoppingList(JSON.parse(savedList));
      }
    } catch (error) {
      console.error('Error loading shopping list from localStorage:', error);
    }
  }, []);
  
  // Save to localStorage when changes occur
  useEffect(() => {
    try {
      localStorage.setItem('selectedRecipes', JSON.stringify(selectedRecipes));
      localStorage.setItem('shoppingList', JSON.stringify(shoppingList));
    } catch (error) {
      console.error('Error saving shopping list to localStorage:', error);
    }
  }, [selectedRecipes, shoppingList]);
  
  // Check if a recipe is already in the list
  const isRecipeInList = (recipeId: number | string): boolean => {
    return selectedRecipes.some(recipe => recipe.id === recipeId);
  };
  
  // Add a recipe to the list
  const addRecipeToList = (recipe: Recipe) => {
    if (!isRecipeInList(recipe.id)) {
      setSelectedRecipes(prevRecipes => [...prevRecipes, recipe]);
    }
  };
  
  // Remove a recipe from the list
  const removeRecipeFromList = (recipeId: number | string) => {
    setSelectedRecipes(prevRecipes => prevRecipes.filter(recipe => recipe.id !== recipeId));
    
    // Also remove any items in the shopping list that are only from this recipe
    setShoppingList(prevList => prevList.filter(item => {
      // Filter out this recipe ID from the item's recipeIds
      item.recipeIds = item.recipeIds.filter(id => id !== recipeId);
      
      // Keep the item if it still has references to other recipes
      return item.recipeIds.length > 0;
    }));
  };
  
  // Clear the entire shopping list
  const clearShoppingList = () => {
    setSelectedRecipes([]);
    setShoppingList([]);
    setTotalCount(0);
    setCheckedCount(0);
  };
  
  // Normalize ingredient units for better aggregation
  const normalizeUnit = (unit: string): string => {
    unit = unit.toLowerCase().trim();
    
    // Normalize common volume units
    if (['tsp', 'teaspoon', 'teaspoons'].includes(unit)) return 'tsp';
    if (['tbsp', 'tablespoon', 'tablespoons'].includes(unit)) return 'tbsp';
    if (['cup', 'cups', 'c'].includes(unit)) return 'cup';
    if (['oz', 'ounce', 'ounces', 'fl oz', 'fluid ounce', 'fluid ounces'].includes(unit)) return 'oz';
    if (['ml', 'milliliter', 'milliliters', 'millilitre', 'millilitres'].includes(unit)) return 'ml';
    if (['l', 'liter', 'liters', 'litre', 'litres'].includes(unit)) return 'liter';
    
    // Normalize common weight units
    if (['g', 'gram', 'grams'].includes(unit)) return 'g';
    if (['kg', 'kilogram', 'kilograms'].includes(unit)) return 'kg';
    if (['lb', 'pound', 'pounds'].includes(unit)) return 'lb';
    
    // Generic counts
    if (['', 'whole', 'piece', 'pieces', 'unit', 'units', 'count'].includes(unit)) return '';
    
    return unit;
  };
  
  // Normalize ingredient names for better aggregation
  const normalizeIngredientName = (name: string): string => {
    return name.toLowerCase()
      .replace(/^fresh /, '')
      .replace(/^frozen /, '')
      .replace(/^dried /, '')
      .replace(/^ground /, '')
      .replace(/^chopped /, '')
      .replace(/^sliced /, '')
      .replace(/^diced /, '')
      .replace(/^minced /, '')
      .replace(/^grated /, '')
      .replace(/^shredded /, '')
      .trim();
  };
  
  // Generate the shopping list from the selected recipes
  const generateShoppingList = async () => {
    if (selectedRecipes.length === 0) {
      console.log("No recipes selected to generate shopping list");
      return;
    }

    try {
      // Call the backend API to generate the shopping list
      const response = await fetch('/api/shopping-list/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ recipes: selectedRecipes })
      });

      if (!response.ok) {
        throw new Error(`API call failed with status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success) {
        // Use the shopping list and stats from the backend
        setShoppingList(data.shoppingList);
        setTotalCount(data.totalCount || data.shoppingList.length);
        setCheckedCount(data.checkedCount || 0);
      } else {
        console.error("Error generating shopping list:", data.error);
      }
    } catch (error) {
      console.error("Failed to generate shopping list:", error);
    }
  };
  
  // Toggle the checked status of an item
  const toggleItemChecked = (itemId: string) => {
    setShoppingList(prevList => {
      const newList = prevList.map(item => 
        item.id === itemId ? { ...item, checked: !item.checked } : item
      );
      
      // Update checkedCount based on the new list
      const newCheckedCount = newList.filter(item => item.checked).length;
      setCheckedCount(newCheckedCount);
      
      return newList;
    });
  };
  
  // Update the amount of an item
  const updateItemAmount = (itemId: string, amount: number) => {
    if (amount <= 0) {
      removeItemFromList(itemId);
      return;
    }
    
    setShoppingList(prevList => {
      const newList = prevList.map(item => 
        item.id === itemId ? { ...item, amount } : item
      );
      return newList;
    });
  };
  
  // Remove an item from the list
  const removeItemFromList = (itemId: string) => {
    setShoppingList(prevList => {
      // Check if the item being removed is checked
      const removedItem = prevList.find(item => item.id === itemId);
      const newList = prevList.filter(item => item.id !== itemId);
      
      // If the removed item was checked, update the checked count
      if (removedItem?.checked) {
        setCheckedCount(prev => prev - 1);
      }
      
      // Update total count
      setTotalCount(newList.length);
      
      return newList;
    });
  };
  
  return (
    <ShoppingListContext.Provider
      value={{
        selectedRecipes,
        shoppingList,
        totalCount,
        checkedCount,
        addRecipeToList,
        removeRecipeFromList,
        clearShoppingList,
        generateShoppingList,
        toggleItemChecked,
        updateItemAmount,
        removeItemFromList,
        isRecipeInList
      }}
    >
      {children}
    </ShoppingListContext.Provider>
  );
};

// Custom hook to use the shopping list context
export const useShoppingList = (): ShoppingListContextType => {
  const context = useContext(ShoppingListContext);
  if (!context) {
    throw new Error('useShoppingList must be used within a ShoppingListProvider');
  }
  return context;
}; 