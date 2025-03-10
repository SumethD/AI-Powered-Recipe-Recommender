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
  searchByIngredients: async (ingredients: string[], limit = 10, ranking = 1, ignorePantry = false) => {
    try {
      const response = await api.get('/recipes/ingredients', {
        params: {
          ingredients: ingredients.join(','),
          limit,
          ranking,
          ignorePantry,
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error searching recipes by ingredients:', error);
      throw error;
    }
  },

  // Search recipes by query
  searchRecipes: async (query: string, cuisine?: string, diet?: string, intolerances?: string, limit = 10) => {
    try {
      const response = await api.get('/recipes/search', {
        params: {
          query,
          cuisine,
          diet,
          intolerances,
          limit,
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error searching recipes:', error);
      throw error;
    }
  },

  // Get random recipes
  getRandomRecipes: async (tags?: string, limit = 10) => {
    try {
      const response = await api.get('/recipes/random', {
        params: {
          tags,
          limit,
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error getting random recipes:', error);
      throw error;
    }
  },

  // Get recipe details
  getRecipeDetails: async (recipeId: number, userId?: string) => {
    try {
      if (!recipeId || isNaN(recipeId)) {
        throw new Error('Invalid recipe ID');
      }
      
      const response = await api.get(`/recipes/${recipeId}`, {
        params: {
          user_id: userId,
        },
      });
      
      if (!response.data) {
        throw new Error('Recipe not found');
      }
      
      return response.data;
    } catch (error) {
      console.error('Error getting recipe details:', error);
      if (error instanceof Error) {
        throw new Error(`Failed to get recipe details: ${error.message}`);
      } else {
        throw new Error('Failed to get recipe details');
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
  // Get user favorites
  getFavorites: async (userId: string, limit?: number, sortBy = 'added_at', reverse = true) => {
    try {
      const response = await api.get('/recipes/favorites', {
        params: {
          user_id: userId,
          limit,
          sort_by: sortBy,
          reverse,
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error getting favorites:', error);
      throw error;
    }
  },

  // Add recipe to favorites
  addFavorite: async (userId: string, recipe: any) => {
    try {
      const response = await api.post('/recipes/favorites', {
        user_id: userId,
        recipe,
      });
      return response.data;
    } catch (error) {
      console.error('Error adding favorite:', error);
      throw error;
    }
  },

  // Remove recipe from favorites
  removeFavorite: async (userId: string, recipeId: number) => {
    try {
      const response = await api.delete(`/recipes/favorites/${recipeId}`, {
        params: {
          user_id: userId,
        },
      });
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

export default {
  recipeApi,
  userApi,
  chatApi,
}; 