import axios from 'axios';
import { recipeApi, userApi, chatApi } from './api';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('API Services', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Recipe API', () => {
    test('searchByIngredients should call the correct endpoint with the right parameters', async () => {
      const mockResponse = { data: { data: [{ id: 1, title: 'Test Recipe' }] } };
      mockedAxios.create.mockReturnThis();
      mockedAxios.post.mockResolvedValueOnce(mockResponse);

      const ingredients = ['chicken', 'rice'];
      const result = await recipeApi.searchByIngredients(ingredients);

      expect(mockedAxios.post).toHaveBeenCalledWith('/recipes/by-ingredients', {
        ingredients,
        limit: 10,
        ranking: 1,
        ignorePantry: false,
      });
      expect(result).toEqual(mockResponse.data);
    });

    test('searchRecipes should call the correct endpoint with the right parameters', async () => {
      const mockResponse = { data: { data: [{ id: 1, title: 'Test Recipe' }] } };
      mockedAxios.create.mockReturnThis();
      mockedAxios.get.mockResolvedValueOnce(mockResponse);

      const query = 'pasta';
      const cuisine = 'italian';
      const diet = 'vegetarian';
      const intolerances = 'gluten';
      const result = await recipeApi.searchRecipes(query, cuisine, diet, intolerances);

      expect(mockedAxios.get).toHaveBeenCalledWith('/recipes/search', {
        params: {
          query,
          cuisine,
          diet,
          intolerances,
          limit: 10,
        },
      });
      expect(result).toEqual(mockResponse.data);
    });

    test('getRecipeDetails should call the correct endpoint with the right parameters', async () => {
      const mockResponse = { data: { data: { id: 1, title: 'Test Recipe' } } };
      mockedAxios.create.mockReturnThis();
      mockedAxios.get.mockResolvedValueOnce(mockResponse);

      const recipeId = 1;
      const userId = 'user123';
      const result = await recipeApi.getRecipeDetails(recipeId, userId);

      expect(mockedAxios.get).toHaveBeenCalledWith(`/recipes/${recipeId}`, {
        params: {
          user_id: userId,
        },
      });
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe('User API', () => {
    test('getFavorites should call the correct endpoint with the right parameters', async () => {
      const mockResponse = { data: { data: [{ id: 1, title: 'Test Recipe' }] } };
      mockedAxios.create.mockReturnThis();
      mockedAxios.get.mockResolvedValueOnce(mockResponse);

      const userId = 'user123';
      const result = await userApi.getFavorites(userId);

      expect(mockedAxios.get).toHaveBeenCalledWith('/recipes/favorites', {
        params: {
          user_id: userId,
          sort_by: 'added_at',
          reverse: true,
        },
      });
      expect(result).toEqual(mockResponse.data);
    });

    test('addFavorite should call the correct endpoint with the right parameters', async () => {
      const mockResponse = { data: { success: true } };
      mockedAxios.create.mockReturnThis();
      mockedAxios.post.mockResolvedValueOnce(mockResponse);

      const userId = 'user123';
      const recipe = { id: 1, title: 'Test Recipe' };
      const result = await userApi.addFavorite(userId, recipe);

      expect(mockedAxios.post).toHaveBeenCalledWith('/recipes/favorites', {
        user_id: userId,
        recipe,
      });
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe('Chat API', () => {
    test('askQuestion should call the correct endpoint with the right parameters', async () => {
      const mockResponse = { data: { data: { response: 'Test response' } } };
      mockedAxios.create.mockReturnThis();
      mockedAxios.post.mockResolvedValueOnce(mockResponse);

      const question = 'How do I make pasta?';
      const userId = 'user123';
      const model = 'gpt-4o-mini';
      const context = JSON.stringify({ recipeId: 1 });
      const result = await chatApi.askQuestion(question, userId, model, context);

      expect(mockedAxios.post).toHaveBeenCalledWith('/chat/ask', {
        question,
        user_id: userId,
        model,
        context,
      });
      expect(result).toEqual(mockResponse.data);
    });

    test('submitFeedback should call the correct endpoint with the right parameters', async () => {
      const mockResponse = { data: { success: true } };
      mockedAxios.create.mockReturnThis();
      mockedAxios.post.mockResolvedValueOnce(mockResponse);

      const userId = 'user123';
      const question = 'How do I make pasta?';
      const aiResponse = 'Boil water and add pasta.';
      const rating = 5;
      const feedback = 'Great response!';
      const result = await chatApi.submitFeedback(userId, question, aiResponse, rating, feedback);

      expect(mockedAxios.post).toHaveBeenCalledWith('/chat/feedback', {
        user_id: userId,
        question,
        response: aiResponse,
        rating,
        feedback,
      });
      expect(result).toEqual(mockResponse.data);
    });
  });
}); 