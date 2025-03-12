import axios from 'axios';
import { Recipe } from '../types';

// Define the base URL for the API
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8003';

// Define interfaces for the request and response
export interface RecipeInstructionsRequest {
  recipe_id: string;
  recipe_name: string;
  source_url?: string;
  ingredients: string[];
  servings?: number;
  cuisine?: string;
  diets?: string[];
}

export interface RecipeInstructionsResponse {
  instructions: string;
  recipe_id?: string;
  source?: string;
  cached?: boolean;
}

// Add this interface to track the progress of instruction fetching
export interface InstructionsFetchStatus {
  status: 'idle' | 'loading' | 'succeeded' | 'failed';
  error?: string;
  retryCount: number;
  lastAttempt?: Date;
}

/**
 * Get recipe instructions from the API
 * Implements a retry mechanism for better reliability
 */
async function getRecipeInstructions(
  request: RecipeInstructionsRequest, 
  setStatus?: (status: InstructionsFetchStatus) => void,
  maxRetries = 2
): Promise<RecipeInstructionsResponse> {
  let retryCount = 0;
  let lastError: any = null;

  // Update status if callback is provided
  const updateStatus = (status: 'idle' | 'loading' | 'succeeded' | 'failed', error?: string) => {
    if (setStatus) {
      setStatus({
        status,
        error,
        retryCount,
        lastAttempt: new Date()
      });
    }
  };

  // Set initial loading state
  updateStatus('loading');
  
  // Check if it's an AllRecipes URL and use the specialized API
  if (request.source_url && request.source_url.includes("allrecipes.com")) {
    try {
      // Create an AbortController for this request
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 15000); // 15 second timeout
      
      try {
        // Make the API call to the specialized AllRecipes API
        const response = await axios.post(
          `${API_BASE_URL.replace('8003', '8002')}/api/allrecipes`,
          { url: request.source_url },
          {
            headers: { 'Content-Type': 'application/json' },
            timeout: 15000, // 15 second timeout
            signal: controller.signal
          }
        );
        
        // Clear the timeout since the request completed successfully
        clearTimeout(timeoutId);
        
        // Check if we have a valid response
        if (response.data && response.data.instructions) {
          // Update status to succeeded
          updateStatus('succeeded');
          return { instructions: response.data.instructions };
        } else {
          throw new Error('Received empty instructions from AllRecipes API');
        }
      } finally {
        // Always clear the timeout to prevent memory leaks
        clearTimeout(timeoutId);
      }
    } catch (error: any) {
      console.warn(`Error using AllRecipes API: ${error.message}. Falling back to standard API.`);
      // Fall through to standard API
    }
  }
  
  // Standard API call with retries
  while (retryCount <= maxRetries) {
    try {
      // Create an AbortController for this request
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
      
      try {
        // Make the API call with the abort controller signal
        const response = await axios.post<RecipeInstructionsResponse>(
          `${API_BASE_URL}/api/recipe-instructions`,
          request,
          {
            headers: { 'Content-Type': 'application/json' },
            timeout: 10000, // 10 second timeout
            signal: controller.signal
          }
        );
        
        // Clear the timeout since the request completed successfully
        clearTimeout(timeoutId);
        
        // Check if we have a valid response
        if (response.data && response.data.instructions) {
          // Update status to succeeded
          updateStatus('succeeded');
          return response.data;
        } else {
          throw new Error('Received empty instructions from server');
        }
      } finally {
        // Always clear the timeout to prevent memory leaks
        clearTimeout(timeoutId);
      }
    } catch (error: any) {
      lastError = error;
      retryCount++;
      
      // Only retry network errors or timeout errors
      const isNetworkError = !error.response && Boolean(error.request);
      const isTimeoutError = error.code === 'ECONNABORTED' || error.name === 'AbortError';
      
      if (retryCount <= maxRetries && (isNetworkError || isTimeoutError)) {
        console.warn(`Retry ${retryCount}/${maxRetries} for recipe instructions: ${error.message}`);
        // Wait a moment before retrying (use exponential backoff)
        await new Promise(resolve => setTimeout(resolve, 1000 * retryCount));
        updateStatus('loading', `Retrying (${retryCount}/${maxRetries})...`);
      } else {
        // We've exhausted retries or it's not a retryable error
        break;
      }
    }
  }
  
  // If we get here, all retries failed
  const errorMessage = lastError?.message || 'Failed to fetch recipe instructions';
  console.error('Error fetching recipe instructions:', lastError);
  
  // Update status to failed
  updateStatus('failed', errorMessage);
  
  // Return a user-friendly error message
  throw new Error(`Unable to get cooking instructions. ${retryCount > 0 ? 'Tried ' + retryCount + ' times. ' : ''}Please check your connection or try again later.`);
}

/**
 * Formats ingredients into a string array
 * @param ingredients The ingredients to format
 * @returns A string array of ingredients
 */
export const formatIngredientsForAPI = (
  ingredients: any[] | string[]
): string[] => {
  if (!ingredients || ingredients.length === 0) {
    return [];
  }

  // If ingredients are already strings, return them
  if (typeof ingredients[0] === 'string') {
    return ingredients as string[];
  }

  // If ingredients are objects with an 'original' property (like from Spoonacular)
  if (ingredients[0] && 'original' in ingredients[0]) {
    return ingredients.map(ing => ing.original);
  }

  // Fallback: try to convert to string
  return ingredients.map(ing => String(ing));
};

/**
 * Prepares a recipe for the instructions API
 * @param recipe The recipe to prepare
 * @returns A RecipeInstructionsRequest object
 */
export const prepareRecipeForInstructionsAPI = (
  recipe: Recipe
): RecipeInstructionsRequest => {
  // Extract ingredients
  let ingredients: string[] = [];
  if (recipe.extendedIngredients && recipe.extendedIngredients.length > 0) {
    ingredients = formatIngredientsForAPI(recipe.extendedIngredients);
  } else if (recipe.ingredients && recipe.ingredients.length > 0) {
    ingredients = formatIngredientsForAPI(recipe.ingredients);
  }

  // Prepare the request
  return {
    recipe_id: recipe.id,
    recipe_name: recipe.title || recipe.name,
    source_url: recipe.sourceUrl || recipe.source_url,
    ingredients,
    servings: recipe.servings,
    cuisine: recipe.cuisines?.[0] || recipe.cuisine,
    diets: recipe.diets || [],
  };
};

// Export default object with all service functions
export default {
  getRecipeInstructions,
  prepareRecipeForInstructionsAPI,
  formatIngredientsForAPI
}; 