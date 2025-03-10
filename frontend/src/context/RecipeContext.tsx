import React, { createContext, useState, useContext, ReactNode, useEffect } from 'react';
import { useUser } from './UserContext';
import { recipeApi, userApi } from '../services/api';

// Define recipe types
export interface Ingredient {
  id: number;
  name: string;
  amount: number;
  unit: string;
  original: string;
  image?: string;
}

export interface Nutrient {
  name: string;
  amount: number;
  unit: string;
  percentOfDailyNeeds: number;
}

export interface Nutrition {
  nutrients: Nutrient[];
  caloricBreakdown?: {
    percentProtein: number;
    percentFat: number;
    percentCarbs: number;
  };
  weightPerServing?: {
    amount: number;
    unit: string;
  };
}

export interface Recipe {
  id: number;
  title: string;
  image: string;
  imageType?: string;
  servings?: number;
  readyInMinutes?: number;
  license?: string;
  sourceName?: string;
  sourceUrl?: string;
  spoonacularScore?: number;
  healthScore?: number;
  spoonacularSourceUrl?: string;
  pricePerServing?: number;
  cheap?: boolean;
  creditsText?: string;
  dairyFree?: boolean;
  gaps?: string;
  glutenFree?: boolean;
  instructions?: string;
  ketogenic?: boolean;
  lowFodmap?: boolean;
  occasions?: string[];
  sustainable?: boolean;
  vegan?: boolean;
  vegetarian?: boolean;
  veryHealthy?: boolean;
  veryPopular?: boolean;
  whole30?: boolean;
  weightWatcherSmartPoints?: number;
  dishTypes?: string[];
  extendedIngredients?: Ingredient[];
  summary?: string;
  cuisines?: string[];
  diets?: string[];
  likes?: number;
  usedIngredientCount?: number;
  missedIngredientCount?: number;
  usedIngredients?: Ingredient[];
  missedIngredients?: Ingredient[];
  unusedIngredients?: Ingredient[];
  isFavorite?: boolean;
  created_at?: string;
  nutrition?: Nutrition;
}

// Define context type
interface RecipeContextType {
  recipes: Recipe[];
  selectedRecipe: Recipe | null;
  isLoading: boolean;
  error: string | null;
  searchByIngredients: (ingredients: string[]) => Promise<void>;
  searchRecipes: (query: string, cuisine?: string, diet?: string, intolerances?: string) => Promise<void>;
  getRandomRecipes: (tags?: string) => Promise<void>;
  getRecipeDetails: (recipeId: number) => Promise<void>;
  toggleFavorite: (recipe: Recipe) => Promise<void>;
  favorites: Recipe[];
  loadFavorites: () => Promise<void>;
}

// Create context
const RecipeContext = createContext<RecipeContextType | null>(null);

// Provider props
type RecipeProviderProps = {
  children: ReactNode;
};

// Provider component
export const RecipeProvider = ({ children }: RecipeProviderProps) => {
  const { user } = useUser();
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [favorites, setFavorites] = useState<Recipe[]>([]);

  // Load favorites when user changes
  useEffect(() => {
    if (user) {
      loadFavorites();
    } else {
      setFavorites([]);
    }
  }, [user]);

  // Search recipes by ingredients
  const searchByIngredients = async (ingredients: string[]): Promise<void> => {
    if (!ingredients || ingredients.length === 0) {
      setError('Please provide at least one ingredient');
      return;
    }

    setIsLoading(true);
    setError(null);
    
    try {
      const response = await recipeApi.searchByIngredients(ingredients);
      if (response && Array.isArray(response)) {
        // Mark favorites
        const markedRecipes = response.map((recipe: Recipe) => ({
          ...recipe,
          isFavorite: favorites.some(fav => fav.id === recipe.id)
        }));
        setRecipes(markedRecipes);
      } else {
        setRecipes([]);
        if (response && response.error) {
          setError(response.error);
        }
      }
      setIsLoading(false);
    } catch (err: any) {
      setError(err.message || 'Failed to search recipes by ingredients');
      setIsLoading(false);
      setRecipes([]);
      console.error('Error searching recipes by ingredients:', err);
    }
  };

  // Search recipes by query
  const searchRecipes = async (query: string, cuisine?: string, diet?: string, intolerances?: string): Promise<void> => {
    if (!query || query.trim() === '') {
      setError('Please provide a search query');
      return;
    }

    setIsLoading(true);
    setError(null);
    
    try {
      const response = await recipeApi.searchRecipes(query, cuisine, diet, intolerances);
      if (response && Array.isArray(response)) {
        // Mark favorites
        const markedRecipes = response.map((recipe: Recipe) => ({
          ...recipe,
          isFavorite: favorites.some(fav => fav.id === recipe.id)
        }));
        setRecipes(markedRecipes);
      } else {
        setRecipes([]);
        if (response && response.error) {
          setError(response.error);
        }
      }
      setIsLoading(false);
    } catch (err: any) {
      setError(err.message || 'Failed to search recipes');
      setIsLoading(false);
      setRecipes([]);
      console.error('Error searching recipes:', err);
    }
  };

  // Get random recipes
  const getRandomRecipes = async (tags?: string): Promise<void> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await recipeApi.getRandomRecipes(tags);
      if (response && response.data) {
        // Mark favorites
        const markedRecipes = response.data.map((recipe: Recipe) => ({
          ...recipe,
          isFavorite: favorites.some(fav => fav.id === recipe.id)
        }));
        setRecipes(markedRecipes);
      } else {
        setRecipes([]);
      }
      setIsLoading(false);
    } catch (err) {
      setError('Failed to get random recipes');
      setIsLoading(false);
      setRecipes([]);
      console.error('Error getting random recipes:', err);
    }
  };

  // Get recipe details
  const getRecipeDetails = async (recipeId: number): Promise<void> => {
    if (!recipeId || isNaN(recipeId)) {
      setError('Invalid recipe ID');
      return;
    }

    setIsLoading(true);
    setError(null);
    
    try {
      const response = await recipeApi.getRecipeDetails(recipeId, user?.id);
      if (response && response.data) {
        // Check if recipe is in favorites
        const isFavorite = favorites.some(fav => fav.id === recipeId);
        setSelectedRecipe({
          ...response.data,
          isFavorite
        });
      } else {
        setSelectedRecipe(null);
        setError('Recipe not found');
      }
      setIsLoading(false);
    } catch (err) {
      console.error('Error getting recipe details:', err);
      setError('Failed to get recipe details. Please try again.');
      setIsLoading(false);
      setSelectedRecipe(null);
    }
  };

  // Toggle favorite
  const toggleFavorite = async (recipe: Recipe): Promise<void> => {
    if (!user) {
      setError('Please log in to save favorites');
      return;
    }
    
    try {
      const isFavorite = favorites.some(fav => fav.id === recipe.id);
      
      if (isFavorite) {
        await userApi.removeFavorite(user.id, recipe.id);
        setFavorites(favorites.filter(fav => fav.id !== recipe.id));
        
        // Update recipes list if the recipe is in the current list
        setRecipes(recipes.map(r => 
          r.id === recipe.id ? { ...r, isFavorite: false } : r
        ));
        
        // Update selected recipe if it's the one being toggled
        if (selectedRecipe && selectedRecipe.id === recipe.id) {
          setSelectedRecipe({ ...selectedRecipe, isFavorite: false });
        }
      } else {
        await userApi.addFavorite(user.id, recipe);
        const favoriteRecipe = { ...recipe, isFavorite: true };
        setFavorites([...favorites, favoriteRecipe]);
        
        // Update recipes list if the recipe is in the current list
        setRecipes(recipes.map(r => 
          r.id === recipe.id ? { ...r, isFavorite: true } : r
        ));
        
        // Update selected recipe if it's the one being toggled
        if (selectedRecipe && selectedRecipe.id === recipe.id) {
          setSelectedRecipe({ ...selectedRecipe, isFavorite: true });
        }
      }
    } catch (err) {
      setError('Failed to update favorites');
      console.error('Error toggling favorite:', err);
    }
  };

  // Load favorites
  const loadFavorites = async (): Promise<void> => {
    if (!user) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await userApi.getFavorites(user.id);
      if (response && response.data) {
        // Mark all as favorites
        const markedFavorites = response.data.map((recipe: Recipe) => ({
          ...recipe,
          isFavorite: true
        }));
        setFavorites(markedFavorites);
      } else {
        setFavorites([]);
      }
      setIsLoading(false);
    } catch (err) {
      setError('Failed to load favorites');
      setIsLoading(false);
      setFavorites([]);
      console.error('Error loading favorites:', err);
    }
  };

  // Context value
  const value = {
    recipes,
    selectedRecipe,
    isLoading,
    error,
    searchByIngredients,
    searchRecipes,
    getRandomRecipes,
    getRecipeDetails,
    toggleFavorite,
    favorites,
    loadFavorites
  };

  // Use React.createElement to avoid JSX linter errors
  return React.createElement(RecipeContext.Provider, { value }, children);
};

// Custom hook to use the context
export const useRecipes = (): RecipeContextType => {
  const context = useContext(RecipeContext);
  if (!context) {
    throw new Error('useRecipes must be used within a RecipeProvider');
  }
  return context;
}; 