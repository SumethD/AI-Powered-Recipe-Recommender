import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import { RecipeProvider, useRecipes } from './RecipeContext';
import { UserProvider } from './UserContext';
import { recipeApi, userApi } from '../services/api';

// Mock the API services
jest.mock('../services/api', () => ({
  recipeApi: {
    searchByIngredients: jest.fn(),
    searchRecipes: jest.fn(),
    getRandomRecipes: jest.fn(),
    getRecipeDetails: jest.fn(),
  },
  userApi: {
    getFavorites: jest.fn(),
    addFavorite: jest.fn(),
    removeFavorite: jest.fn(),
  },
}));

// Test component that uses the RecipeContext
const TestComponent = () => {
  const { 
    recipes, 
    selectedRecipe, 
    isLoading, 
    error, 
    searchByIngredients,
    searchRecipes,
    getRecipeDetails,
    toggleFavorite,
    favorites,
    loadFavorites
  } = useRecipes();

  return (
    <div>
      <div data-testid="loading">{isLoading ? 'Loading...' : 'Not loading'}</div>
      <div data-testid="error">{error || 'No error'}</div>
      <div data-testid="recipes-count">{recipes.length}</div>
      <div data-testid="selected-recipe">{selectedRecipe ? selectedRecipe.title : 'No recipe selected'}</div>
      <div data-testid="favorites-count">{favorites.length}</div>
      <button data-testid="search-ingredients" onClick={() => searchByIngredients(['chicken', 'rice'])}>
        Search by Ingredients
      </button>
      <button data-testid="search-query" onClick={() => searchRecipes('pasta')}>
        Search by Query
      </button>
      <button data-testid="get-details" onClick={() => getRecipeDetails(123)}>
        Get Recipe Details
      </button>
      <button data-testid="load-favorites" onClick={() => loadFavorites()}>
        Load Favorites
      </button>
      <button 
        data-testid="toggle-favorite" 
        onClick={() => toggleFavorite({ id: 123, title: 'Test Recipe', image: 'test.jpg' })}
      >
        Toggle Favorite
      </button>
    </div>
  );
};

// Wrap the test component with providers
const renderWithProviders = () => {
  return render(
    <UserProvider>
      <RecipeProvider>
        <TestComponent />
      </RecipeProvider>
    </UserProvider>
  );
};

describe('RecipeContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('should show loading state when searching recipes by ingredients', async () => {
    // Mock the API response
    (recipeApi.searchByIngredients as jest.Mock).mockResolvedValue({
      data: [{ id: 1, title: 'Chicken Rice', image: 'chicken.jpg' }]
    });

    renderWithProviders();

    // Initial state
    expect(screen.getByTestId('loading')).toHaveTextContent('Not loading');
    expect(screen.getByTestId('recipes-count')).toHaveTextContent('0');

    // Click the search button
    await act(async () => {
      screen.getByTestId('search-ingredients').click();
    });

    // Should show loading state
    expect(screen.getByTestId('loading')).toHaveTextContent('Loading...');

    // Wait for the API call to resolve
    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('Not loading');
    });

    // Should have recipes
    expect(screen.getByTestId('recipes-count')).toHaveTextContent('1');
    expect(recipeApi.searchByIngredients).toHaveBeenCalledWith(['chicken', 'rice']);
  });

  test('should show error state when API call fails', async () => {
    // Mock the API error
    (recipeApi.searchRecipes as jest.Mock).mockRejectedValue(new Error('API error'));

    renderWithProviders();

    // Initial state
    expect(screen.getByTestId('error')).toHaveTextContent('No error');

    // Click the search button
    await act(async () => {
      screen.getByTestId('search-query').click();
    });

    // Wait for the API call to reject
    await waitFor(() => {
      expect(screen.getByTestId('error')).toHaveTextContent('Failed to search recipes');
    });
  });

  test('should load recipe details', async () => {
    // Mock the API response
    (recipeApi.getRecipeDetails as jest.Mock).mockResolvedValue({
      data: { id: 123, title: 'Pasta Carbonara', image: 'pasta.jpg' }
    });

    renderWithProviders();

    // Initial state
    expect(screen.getByTestId('selected-recipe')).toHaveTextContent('No recipe selected');

    // Click the get details button
    await act(async () => {
      screen.getByTestId('get-details').click();
    });

    // Wait for the API call to resolve
    await waitFor(() => {
      expect(screen.getByTestId('selected-recipe')).toHaveTextContent('Pasta Carbonara');
    });

    expect(recipeApi.getRecipeDetails).toHaveBeenCalledWith(123, undefined);
  });

  test('should load favorites', async () => {
    // Mock the API response
    (userApi.getFavorites as jest.Mock).mockResolvedValue({
      data: [
        { id: 1, title: 'Favorite 1', image: 'fav1.jpg' },
        { id: 2, title: 'Favorite 2', image: 'fav2.jpg' }
      ]
    });

    renderWithProviders();

    // Initial state
    expect(screen.getByTestId('favorites-count')).toHaveTextContent('0');

    // Click the load favorites button
    await act(async () => {
      screen.getByTestId('load-favorites').click();
    });

    // Wait for the API call to resolve
    await waitFor(() => {
      expect(screen.getByTestId('favorites-count')).toHaveTextContent('2');
    });
  });
}); 