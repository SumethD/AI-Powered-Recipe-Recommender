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
  id: number | string;
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
export interface RecipeContextType {
  recipes: Recipe[];
  selectedRecipe: Recipe | null;
  isLoading: boolean;
  error: string | null;
  searchByIngredients: (ingredients: string[], apiProvider?: string) => Promise<void>;
  searchRecipes: (query: string, cuisine?: string, diet?: string, intolerances?: string, apiProvider?: string) => Promise<void>;
  getRandomRecipes: (count?: number) => Promise<void>;
  getRecipeDetails: (recipeId: number | string, apiProvider?: string) => Promise<Recipe | null>;
  toggleFavorite: (recipe: Recipe) => Promise<void>;
  favorites: Recipe[];
  loadFavorites: () => Promise<void>;
  isFavorite: (recipeId: number | string) => boolean;
  setSelectedRecipe: React.Dispatch<React.SetStateAction<Recipe | null>>;
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
  const searchByIngredients = async (ingredients: string[], apiProvider: string = 'edamam'): Promise<void> => {
    if (!ingredients || ingredients.length === 0) {
      setError('Please provide at least one ingredient');
      return;
    }

    setIsLoading(true);
    setError(null);
    
    try {
      console.log(`Searching for recipes with ingredients: ${ingredients.join(', ')} using API provider: ${apiProvider}`);
      const response = await recipeApi.searchByIngredients(ingredients, 10, 1, false, apiProvider);
      
      console.log("Response from searchByIngredients:", response);
      
      if (response && Array.isArray(response)) {
        if (response.length === 0) {
          setError('No recipes found with these ingredients. Try adding more ingredients or using different ones.');
          setRecipes([]);
        } else {
          // Mark favorites
          const markedRecipes = response.map((recipe: Recipe) => ({
            ...recipe,
            isFavorite: favorites.some(fav => fav.id === recipe.id)
          }));
          setRecipes(markedRecipes);
        }
      } else {
        setRecipes([]);
        if (response && response.error) {
          setError(response.error);
        } else {
          setError('Unexpected response format from the server');
          console.error("Unexpected response format:", response);
        }
      }
      setIsLoading(false);
    } catch (err: any) {
      console.error('Error searching recipes by ingredients:', err);
      setError(err.message || 'Failed to search recipes by ingredients. Please try again later.');
      setIsLoading(false);
      setRecipes([]);
    }
  };

  // Search recipes by query
  const searchRecipes = async (query: string, cuisine?: string, diet?: string, intolerances?: string, apiProvider: string = 'edamam'): Promise<void> => {
    if (!query || query.trim() === '') {
      setError('Please provide a search query');
      return;
    }

    setIsLoading(true);
    setError(null);
    
    try {
      const response = await recipeApi.searchRecipes(query, cuisine, diet, intolerances, 10, 'edamam');
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
  const getRandomRecipes = async (count?: number): Promise<void> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await recipeApi.getRandomRecipes(count, undefined, 'edamam');
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
      setError(err.message || 'Failed to get random recipes');
      setIsLoading(false);
      setRecipes([]);
      console.error('Error getting random recipes:', err);
    }
  };

  // Get recipe details
  const getRecipeDetails = async (recipeId: number | string, apiProvider: string = 'edamam'): Promise<Recipe | null> => {
    console.log("getRecipeDetails called with:", { recipeId, apiProvider });
    
    if (!recipeId) {
      console.error("Invalid recipe ID: empty");
      setError('Invalid recipe ID');
      return null;
    }

    // For number IDs (Spoonacular), validate that it's a valid number
    if (typeof recipeId === 'number' && isNaN(recipeId)) {
      console.error("Invalid recipe ID: NaN");
      setError('Invalid recipe ID');
      return null;
    }
    
    // For string IDs, normalize to lowercase
    const normalizedId = typeof recipeId === 'string' ? recipeId.toLowerCase() : recipeId;
    console.log("Normalized recipe ID:", normalizedId);

    setIsLoading(true);
    setError(null);
    
    // Add retry logic
    const maxRetries = 2;
    let retryCount = 0;
    let lastError: any = null;
    
    while (retryCount <= maxRetries) {
      try {
        if (retryCount > 0) {
          console.log(`Retry attempt ${retryCount} for recipe ID: ${normalizedId}`);
        }
        
        console.log("Calling API with:", { recipeId: normalizedId, apiProvider });
        const response = await recipeApi.getRecipeDetails(String(normalizedId), apiProvider);
        console.log("API response:", response);
        
        if (response) {
          // Verify the recipe has required fields
          if (!response.title) {
            console.warn("Recipe has no title");
            setError('Recipe data is incomplete');
            setIsLoading(false);
            return null;
          }
          
          // Check if recipe is in favorites
          const isFavorite = favorites.some(fav => {
            const favId = typeof fav.id === 'string' ? fav.id.toLowerCase() : fav.id;
            const recipeIdNormalized = typeof normalizedId === 'string' ? normalizedId.toLowerCase() : normalizedId;
            return favId.toString() === recipeIdNormalized.toString();
          });
          
          const recipeWithFavorite = {
            ...response,
            isFavorite
          };
          console.log("Setting selected recipe:", recipeWithFavorite);
          setSelectedRecipe(recipeWithFavorite);
          
          // Add a small delay before setting isLoading to false to ensure smooth UI transitions
          await new Promise(resolve => setTimeout(resolve, 300));
          
          setIsLoading(false);
          return recipeWithFavorite;
        } else {
          console.error("Recipe not found or error in response:", response);
          lastError = new Error('Recipe not found');
          retryCount++;
          
          if (retryCount <= maxRetries) {
            // Wait before retrying (exponential backoff)
            await new Promise(resolve => setTimeout(resolve, 1000 * retryCount));
            continue;
          }
          
          setSelectedRecipe(null);
          setError('Recipe not found');
          setIsLoading(false);
          return null;
        }
      } catch (err: any) {
        console.error(`Error getting recipe details (attempt ${retryCount + 1}):`, err);
        lastError = err;
        retryCount++;
        
        if (retryCount <= maxRetries) {
          // Wait before retrying (exponential backoff)
          await new Promise(resolve => setTimeout(resolve, 1000 * retryCount));
          continue;
        }
        
        setError(err.message || 'Failed to get recipe details. Please try again.');
        setIsLoading(false);
        setSelectedRecipe(null);
        return null;
      }
    }
    
    // If we get here, all retries failed
    setError(lastError?.message || 'Failed to get recipe details after multiple attempts');
    setIsLoading(false);
    setSelectedRecipe(null);
    return null;
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

  // Check if a recipe is in favorites
  const isFavorite = (recipeId: number | string): boolean => {
    return favorites.some(fav => fav.id === recipeId);
  };

  // Context value
  const contextValue: RecipeContextType = {
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
    loadFavorites,
    isFavorite,
    setSelectedRecipe
  };

  // Use React.createElement to avoid JSX linter errors
  return React.createElement(RecipeContext.Provider, { value: contextValue }, children);
};

// Custom hook to use the context
export const useRecipes = (): RecipeContextType => {
  const context = useContext(RecipeContext);
  if (!context) {
    throw new Error('useRecipes must be used within a RecipeProvider');
  }
  return context;
}; 