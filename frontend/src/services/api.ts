import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Recipe API
export const recipeApi = {
  // Search recipes by ingredients
  searchByIngredients: async (ingredients: string[], limit = 10, ranking = 1, ignorePantry = false, apiProvider: string = 'edamam') => {
    try {
      console.log(`API call: Searching by ingredients: ${ingredients.join(', ')} with provider: ${apiProvider}`);
      
      // Add a timeout to the request
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
      
      const response = await api.post('/recipes/ingredients', {
        ingredients,
        limit,
        ranking,
        ignore_pantry: ignorePantry,
        apiProvider
      }, {
        signal: controller.signal
      });
      
      // Clear the timeout
      clearTimeout(timeoutId);
      
      console.log("Search by ingredients response status:", response.status);
      console.log("Search by ingredients response data:", response.data);
      
      // Check if the response has the expected format
      if (response.data && response.data.success && response.data.recipes) {
        return response.data.recipes;
      } else if (response.data && Array.isArray(response.data)) {
        return response.data;
      } else {
        console.error("Unexpected response format:", response.data);
        return [];
      }
    } catch (error: any) {
      console.error('Error searching recipes by ingredients:', error);
      
      // Provide more specific error messages
      if (error.code === 'ECONNABORTED' || error.name === 'AbortError') {
        throw new Error('Request timed out. The server took too long to respond.');
      } else if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        console.error('Error response data:', error.response.data);
        console.error('Error response status:', error.response.status);
        throw new Error(`Server error: ${error.response.data?.error || error.response.statusText || 'Unknown error'}`);
      } else if (error.request) {
        // The request was made but no response was received
        console.error('No response received:', error.request);
        throw new Error('No response from server. Please check your connection and try again.');
      } else {
        // Something happened in setting up the request that triggered an Error
        throw error;
      }
    }
  },

  // Search recipes by query
  searchRecipes: async (query: string, cuisine?: string, diet?: string, intolerances?: string, limit = 10, apiProvider: string = 'edamam') => {
    try {
      console.log("Searching recipes with query:", query);
      const response = await api.get('/recipes/search', {
        params: {
          query,
          cuisine,
          diet,
          intolerances,
          limit,
          apiProvider
        },
      });
      
      console.log("Search recipes response:", response.data);
      
      // Check if the response has the expected format
      if (response.data && response.data.success && response.data.recipes) {
        return response.data.recipes;
      } else if (response.data && Array.isArray(response.data)) {
        return response.data;
      } else {
        console.error("Unexpected response format:", response.data);
        return [];
      }
    } catch (error) {
      console.error('Error searching recipes:', error);
      throw error;
    }
  },

  // Get random recipes
  getRandomRecipes: async (limit = 10, tags?: string, apiProvider: string = 'edamam') => {
    try {
      console.log("Getting random recipes");
      const response = await api.get('/recipes/random', {
        params: {
          limit,
          tags,
          apiProvider
        },
      });
      
      console.log("Random recipes response:", response.data);
      
      // Check if the response has the expected format
      if (response.data && response.data.success && response.data.recipes) {
        return response.data.recipes;
      } else if (response.data && Array.isArray(response.data)) {
        return response.data;
      } else {
        console.error("Unexpected response format:", response.data);
        return [];
      }
    } catch (error) {
      console.error('Error getting random recipes:', error);
      throw error;
    }
  },

  // Get recipe details
  getRecipeDetails: async (recipeId: number | string, apiProvider: string = 'edamam') => {
    if (!recipeId) {
      console.error('Recipe ID is required');
      throw new Error('Recipe ID is required');
    }

    try {
      // Convert recipeId to string to ensure compatibility
      const recipeIdStr = String(recipeId);
      console.log(`Getting details for recipe: ${recipeIdStr} with provider: ${apiProvider}`);
      
      // Add a timeout to the request
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
      
      const response = await api.get(`/recipes/${recipeIdStr}`, {
        params: { apiProvider },
        signal: controller.signal
      });
      
      // Clear the timeout
      clearTimeout(timeoutId);
      
      console.log("Recipe details response status:", response.status);
      console.log("Recipe details response data:", response.data);
      
      // Check if the response has the expected format
      if (response.data && response.data.success && response.data.recipe) {
        return response.data.recipe;
      } else if (response.data && !Array.isArray(response.data) && typeof response.data === 'object') {
        return response.data;
      } else {
        console.error("Unexpected response format:", response.data);
        return null;
      }
    } catch (error: any) {
      console.error(`Error getting recipe details for ${recipeId}:`, error);
      
      // Provide more specific error messages
      if (error.code === 'ECONNABORTED' || error.name === 'AbortError') {
        throw new Error('Request timed out. The server took too long to respond.');
      } else if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        console.error('Error response data:', error.response.data);
        console.error('Error response status:', error.response.status);
        throw new Error(`Server error: ${error.response.data?.error || error.response.statusText || 'Unknown error'}`);
      } else if (error.request) {
        // The request was made but no response was received
        console.error('No response received:', error.request);
        throw new Error('No response from server. Please check your connection and try again.');
      } else {
        // Something happened in setting up the request that triggered an Error
        throw error;
      }
    }
  },

  // Get supported cuisines
  getCuisines: async () => {
    try {
      const response = await api.get('/recipes/cuisines');
      return response.data;
    } catch (error) {
      console.error('Error getting cuisines:', error);
      throw error;
    }
  },

  // Get supported diets
  getDiets: async () => {
    try {
      const response = await api.get('/recipes/diets');
      return response.data;
    } catch (error) {
      console.error('Error getting diets:', error);
      throw error;
    }
  },

  // Get supported intolerances
  getIntolerances: async () => {
    try {
      const response = await api.get('/recipes/intolerances');
      return response.data;
    } catch (error) {
      console.error('Error getting intolerances:', error);
      throw error;
    }
  },
};

// User API
export const userApi = {
  // Get user details
  getUser: async (userId: string) => {
    try {
      const response = await api.get(`/users/${userId}`);
      return response.data;
    } catch (error) {
      console.error('Error getting user details:', error);
      throw error;
    }
  },

  // Get user favorites
  getFavorites: async (userId: string) => {
    try {
      const response = await api.get(`/users/${userId}/favorites`);
      return response.data.favorites;
    } catch (error) {
      console.error('Error getting user favorites:', error);
      throw error;
    }
  },

  // Add favorite
  addFavorite: async (userId: string, recipe: any) => {
    try {
      const response = await api.post(`/users/${userId}/favorites`, { recipe });
      return response.data;
    } catch (error) {
      console.error('Error adding favorite:', error);
      throw error;
    }
  },

  // Remove favorite
  removeFavorite: async (userId: string, recipeId: number | string) => {
    try {
      const response = await api.delete(`/users/${userId}/favorites/${recipeId}`);
      return response.data;
    } catch (error) {
      console.error('Error removing favorite:', error);
      throw error;
    }
  },

  // Get user preferences
  getPreferences: async (userId: string) => {
    try {
      const response = await api.get('/recipes/preferences', {
        params: {
          user_id: userId,
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error getting preferences:', error);
      throw error;
    }
  },

  // Update user preferences
  updatePreferences: async (userId: string, preferences: any) => {
    try {
      const response = await api.post('/recipes/preferences', {
        user_id: userId,
        preferences,
      });
      return response.data;
    } catch (error) {
      console.error('Error updating preferences:', error);
      throw error;
    }
  },
};

// Chat API
export const chatApi = {
  // Ask a question to the AI assistant
  askQuestion: async (question: string, userId?: string, model = 'gpt-4o-mini', context?: string) => {
    try {
      const response = await api.post('/chat/ask', {
        question,
        user_id: userId,
        model,
        context,
      });
      return response.data;
    } catch (error) {
      console.error('Error asking question:', error);
      throw error;
    }
  },

  // Submit feedback for an AI response
  submitFeedback: async (userId: string, question: string, aiResponse: string, rating: number, feedback?: string) => {
    try {
      const response = await api.post('/chat/feedback', {
        user_id: userId,
        question,
        response: aiResponse,
        rating,
        feedback,
      });
      return response.data;
    } catch (error) {
      console.error('Error submitting feedback:', error);
      throw error;
    }
  },
};

// Create a default export object
const apiService = {
  recipeApi,
  userApi,
  chatApi,
};

export default apiService; 