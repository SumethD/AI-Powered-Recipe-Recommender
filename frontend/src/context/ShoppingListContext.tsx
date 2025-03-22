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
  addRecipeToList: (recipe: Recipe) => void;
  removeRecipeFromList: (recipeId: number | string) => void;
  clearShoppingList: () => void;
  generateShoppingList: () => void;
  toggleItemChecked: (itemId: string) => void;
  updateItemAmount: (itemId: string, amount: number) => void;
  removeItemFromList: (itemId: string) => void;
  isRecipeInList: (recipeId: number | string) => boolean;
  addToShoppingList: (recipe: Recipe) => void;
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
export const ShoppingListProvider = ({ children }: ShoppingListProviderProps) => {
  const [selectedRecipes, setSelectedRecipes] = useState<Recipe[]>([]);
  const [shoppingList, setShoppingList] = useState<ShoppingListItem[]>([]);
  
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
    try {
      // Display loading state if needed
      // Create a request to the backend API
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/shopping-list/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          recipes: selectedRecipes
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        console.error('Error generating shopping list:', errorData);
        throw new Error(errorData.error || 'Failed to generate shopping list');
      }
      
      const data = await response.json();
      setShoppingList(data.shopping_list);
    } catch (error) {
      console.error('Error generating shopping list:', error);
      // Fallback to generating client-side if the API fails
      generateShoppingListClientSide();
    }
  };
  
  // Fallback function that generates the list on the client side (using the original implementation)
  const generateShoppingListClientSide = () => {
    // Get all ingredients from selected recipes
    const allIngredients: {
      name: string;
      amount: number;
      unit: string;
      recipeId: number | string;
    }[] = [];
    
    selectedRecipes.forEach(recipe => {
      if (recipe.extendedIngredients) {
        recipe.extendedIngredients.forEach(ingredient => {
          // Handle cases where amount might be a string (like "1/2")
          let ingredientAmount = ingredient.amount;
          if (typeof ingredientAmount === 'string') {
            ingredientAmount = parseFraction(ingredientAmount);
          }

          allIngredients.push({
            name: normalizeIngredientName(ingredient.name),
            amount: ingredientAmount,
            unit: normalizeUnit(ingredient.unit),
            recipeId: recipe.id
          });
        });
      }
    });
    
    // Aggregate ingredients
    const aggregatedIngredients: Record<string, ShoppingListItem> = {};
    
    allIngredients.forEach(ingredient => {
      const key = `${ingredient.name}|${ingredient.unit}`;
      
      // Standardize the ingredient measurement
      const { amount: standardizedAmount, unit: standardizedUnit } = standardizeIngredientMeasurement(
        ingredient.amount,
        ingredient.unit,
        ingredient.name
      );
      
      // Create display string for standardized measurement
      const standardizedDisplay = formatIngredientMeasurement(
        standardizedAmount,
        standardizedUnit,
        ingredient.name
      );
      
      if (aggregatedIngredients[key]) {
        // Update existing ingredient
        aggregatedIngredients[key].amount += ingredient.amount;
        
        // Update standardized amount based on new total
        const { amount: newStandardizedAmount } = standardizeIngredientMeasurement(
          aggregatedIngredients[key].amount,
          ingredient.unit,
          ingredient.name
        );
        
        // Update standardized display
        aggregatedIngredients[key].standardizedDisplay = formatIngredientMeasurement(
          newStandardizedAmount,
          standardizedUnit,
          ingredient.name
        );
        
        // Add recipe reference if not already present
        if (!aggregatedIngredients[key].recipeIds.includes(ingredient.recipeId)) {
          aggregatedIngredients[key].recipeIds.push(ingredient.recipeId);
        }
      } else {
        // Create new ingredient
        aggregatedIngredients[key] = {
          id: generateId(),
          name: ingredient.name,
          amount: ingredient.amount,
          unit: ingredient.unit,
          originalAmount: ingredient.amount,
          originalUnit: ingredient.unit,
          standardizedDisplay: standardizedDisplay,
          category: categorizeIngredient(ingredient.name),
          checked: false,
          recipeIds: [ingredient.recipeId]
        };
      }
    });
    
    // Convert to array and sort by category
    const newShoppingList = Object.values(aggregatedIngredients).sort((a, b) => {
      if (a.category !== b.category) {
        return a.category.localeCompare(b.category);
      }
      return a.name.localeCompare(b.name);
    });
    
    setShoppingList(newShoppingList);
  };
  
  // Toggle the checked status of an item
  const toggleItemChecked = (itemId: string) => {
    setShoppingList(prevList => 
      prevList.map(item => 
        item.id === itemId ? { ...item, checked: !item.checked } : item
      )
    );
  };
  
  // Update the amount of an item
  const updateItemAmount = (itemId: string, amount: number) => {
    if (amount <= 0) {
      removeItemFromList(itemId);
      return;
    }
    
    setShoppingList(prevList => 
      prevList.map(item => 
        item.id === itemId ? { ...item, amount } : item
      )
    );
  };
  
  // Remove an item from the list
  const removeItemFromList = (itemId: string) => {
    setShoppingList(prevList => prevList.filter(item => item.id !== itemId));
  };
  
  // Context value
  const contextValue: ShoppingListContextType = {
    selectedRecipes,
    shoppingList,
    addRecipeToList,
    removeRecipeFromList,
    clearShoppingList,
    generateShoppingList,
    toggleItemChecked,
    updateItemAmount,
    removeItemFromList,
    isRecipeInList,
    addToShoppingList: addRecipeToList
  };
  
  return (
    <ShoppingListContext.Provider
      value={contextValue}
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