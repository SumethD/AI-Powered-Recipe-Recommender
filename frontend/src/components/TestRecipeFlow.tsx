import React, { useState, useEffect } from 'react';
import { Box, Button, Card, CardContent, Container, Grid, TextField, Typography, CircularProgress, Divider } from '@mui/material';
import { Recipe } from '../context/RecipeContext';
import { recipeApi } from '../services/api';
import axios from 'axios';

// Create a direct axios instance for testing purposes
const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

const TestRecipeFlow: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [searchResults, setSearchResults] = useState<Recipe[]>([]);
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null);
  const [selectedRecipeDetails, setSelectedRecipeDetails] = useState<Recipe | null>(null);
  const [isSearching, setIsSearching] = useState<boolean>(false);
  const [isLoadingDetails, setIsLoadingDetails] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [logs, setLogs] = useState<string[]>([]);

  const addLog = (message: string) => {
    setLogs(prevLogs => [...prevLogs, `${new Date().toISOString()}: ${message}`]);
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setError('Please enter a search query');
      return;
    }

    setError(null);
    setIsSearching(true);
    setSearchResults([]);
    setSelectedRecipe(null);
    setSelectedRecipeDetails(null);
    
    try {
      addLog(`Searching for recipes with query: ${searchQuery}`);
      
      // Use axios directly instead of recipeApi
      const response = await api.get('/recipes/search', {
        params: {
          query: searchQuery,
          apiProvider: 'edamam'
        }
      });
      
      addLog(`Raw API response: ${JSON.stringify(response.data).substring(0, 200)}...`);
      
      let recipes: Recipe[] = [];
      
      // Handle different response formats
      if (response.data && response.data.recipes && Array.isArray(response.data.recipes)) {
        recipes = response.data.recipes;
        addLog(`Found ${recipes.length} recipes in response.data.recipes`);
      } else if (response.data && Array.isArray(response.data)) {
        recipes = response.data;
        addLog(`Found ${recipes.length} recipes in response.data array`);
      } else {
        addLog(`Unexpected response format: ${JSON.stringify(response.data).substring(0, 200)}...`);
        setError('Unexpected response format');
        setIsSearching(false);
        return;
      }
      
      if (recipes.length > 0) {
        setSearchResults(recipes);
        addLog(`Found ${recipes.length} recipes`);
        
        // Log recipe IDs and titles for debugging
        recipes.forEach((recipe: Recipe, index: number) => {
          addLog(`Recipe ${index + 1}: ID=${recipe.id}, Title=${recipe.title || 'No title'}`);
        });
      } else {
        setError('No recipes found');
        addLog('No recipes found in response');
      }
    } catch (err) {
      setError('Error searching for recipes');
      addLog(`Search error: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setIsSearching(false);
    }
  };

  const handleRecipeClick = async (recipe: Recipe) => {
    setSelectedRecipe(recipe);
    setSelectedRecipeDetails(null);
    setIsLoadingDetails(true);
    setError(null);
    
    try {
      addLog(`Fetching details for recipe: ID=${recipe.id}, Title=${recipe.title || 'No title'}`);
      
      // Convert recipe ID to string and ensure it's properly formatted
      const recipeId = String(recipe.id).trim().toLowerCase();
      addLog(`Normalized recipe ID: ${recipeId}`);
      
      // Use axios directly instead of recipeApi
      const response = await api.get(`/recipes/${recipeId}`);
      
      addLog(`Raw API response: ${JSON.stringify(response.data).substring(0, 200)}...`);
      
      let recipeDetails: Recipe | null = null;
      
      // Handle different response formats
      if (response.data && response.data.recipe) {
        recipeDetails = response.data.recipe;
        addLog(`Found recipe details in response.data.recipe`);
      } else if (response.data && !Array.isArray(response.data) && typeof response.data === 'object') {
        recipeDetails = response.data;
        addLog(`Found recipe details in response.data object`);
      } else {
        addLog(`Unexpected response format: ${JSON.stringify(response.data).substring(0, 200)}...`);
        setError('Unexpected response format');
        setIsLoadingDetails(false);
        return;
      }
      
      if (recipeDetails) {
        setSelectedRecipeDetails(recipeDetails);
        addLog(`Successfully loaded recipe details: Title=${recipeDetails.title || 'No title'}`);
        
        // Verify ID consistency
        const normalizedResponseId = typeof recipeDetails.id === 'string' 
          ? recipeDetails.id.toLowerCase() 
          : recipeDetails.id.toString();
        const normalizedRequestId = typeof recipe.id === 'string' 
          ? recipe.id.toLowerCase() 
          : recipe.id.toString();
          
        if (normalizedResponseId === normalizedRequestId) {
          addLog('Recipe ID consistency check: PASSED');
        } else {
          addLog(`Recipe ID consistency check: FAILED. Search ID=${recipe.id}, Details ID=${recipeDetails.id}`);
        }
        
        // Verify title consistency
        if (recipeDetails.title === recipe.title) {
          addLog('Recipe title consistency check: PASSED');
        } else {
          addLog(`Recipe title consistency check: FAILED. Search title=${recipe.title || 'No title'}, Details title=${recipeDetails.title || 'No title'}`);
        }
      } else {
        setError('No recipe details found');
        addLog('No recipe details found in response');
      }
    } catch (err) {
      setError(`Error fetching recipe details: ${err instanceof Error ? err.message : String(err)}`);
      addLog(`Details error: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setIsLoadingDetails(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const clearLogs = () => {
    setLogs([]);
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Recipe Flow Test
      </Typography>
      
      <Box sx={{ mb: 4 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={8}>
            <TextField
              fullWidth
              label="Search for recipes"
              variant="outlined"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={handleKeyPress}
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <Button
              fullWidth
              variant="contained"
              color="primary"
              onClick={handleSearch}
              disabled={isSearching}
              sx={{ height: '56px' }}
            >
              {isSearching ? <CircularProgress size={24} /> : 'Search'}
            </Button>
          </Grid>
        </Grid>
      </Box>
      
      {error && (
        <Box sx={{ mb: 2 }}>
          <Typography color="error">{error}</Typography>
        </Box>
      )}
      
      <Grid container spacing={4}>
        <Grid item xs={12} md={6}>
          <Typography variant="h5" gutterBottom>
            Search Results
          </Typography>
          
          {isSearching ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <Box>
              {searchResults.length > 0 ? (
                <Grid container spacing={2}>
                  {searchResults.map((recipe) => (
                    <Grid item xs={12} key={recipe.id}>
                      <Card 
                        sx={{ 
                          cursor: 'pointer',
                          bgcolor: selectedRecipe?.id === recipe.id ? 'primary.light' : 'background.paper'
                        }}
                        onClick={() => handleRecipeClick(recipe)}
                      >
                        <CardContent>
                          <Typography variant="h6">{recipe.title}</Typography>
                          <Typography variant="body2" color="text.secondary">
                            ID: {recipe.id}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              ) : (
                <Typography>No recipes found</Typography>
              )}
            </Box>
          )}
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Typography variant="h5" gutterBottom>
            Recipe Details
          </Typography>
          
          {isLoadingDetails ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
              <CircularProgress />
            </Box>
          ) : selectedRecipeDetails ? (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {selectedRecipeDetails.title}
                </Typography>
                
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  ID: {selectedRecipeDetails.id}
                </Typography>
                
                {selectedRecipeDetails.image && (
                  <Box sx={{ my: 2, textAlign: 'center' }}>
                    <img 
                      src={selectedRecipeDetails.image} 
                      alt={selectedRecipeDetails.title} 
                      style={{ maxWidth: '100%', maxHeight: '200px' }}
                    />
                  </Box>
                )}
                
                <Divider sx={{ my: 2 }} />
                
                <Typography variant="subtitle1" gutterBottom>
                  Source: {selectedRecipeDetails.sourceName || 'Unknown'}
                </Typography>
                
                {selectedRecipeDetails.sourceUrl && (
                  <Typography variant="body2" gutterBottom>
                    <a href={selectedRecipeDetails.sourceUrl} target="_blank" rel="noopener noreferrer">
                      View Original Recipe
                    </a>
                  </Typography>
                )}
                
                <Divider sx={{ my: 2 }} />
                
                <Typography variant="subtitle1" gutterBottom>
                  Ingredients:
                </Typography>
                
                {selectedRecipeDetails.extendedIngredients && selectedRecipeDetails.extendedIngredients.length > 0 ? (
                  <ul>
                    {selectedRecipeDetails.extendedIngredients.map((ingredient, index) => (
                      <li key={index}>{ingredient.original}</li>
                    ))}
                  </ul>
                ) : (
                  <Typography variant="body2">No ingredients information available</Typography>
                )}
                
                <Divider sx={{ my: 2 }} />
                
                <Typography variant="subtitle1" gutterBottom>
                  Instructions:
                </Typography>
                
                {selectedRecipeDetails.instructions ? (
                  <Typography variant="body2" dangerouslySetInnerHTML={{ __html: selectedRecipeDetails.instructions }} />
                ) : selectedRecipeDetails.sourceUrl ? (
                  <Typography variant="body2">
                    Instructions are available at the{' '}
                    <a href={selectedRecipeDetails.sourceUrl} target="_blank" rel="noopener noreferrer">
                      source website
                    </a>
                  </Typography>
                ) : (
                  <Typography variant="body2">No instructions available</Typography>
                )}
              </CardContent>
            </Card>
          ) : selectedRecipe ? (
            <Typography>Loading recipe details...</Typography>
          ) : (
            <Typography>Select a recipe to view details</Typography>
          )}
        </Grid>
      </Grid>
      
      <Box sx={{ mt: 4 }}>
        <Typography variant="h5" gutterBottom>
          Debug Logs
          <Button 
            variant="outlined" 
            size="small" 
            onClick={clearLogs} 
            sx={{ ml: 2 }}
          >
            Clear Logs
          </Button>
        </Typography>
        
        <Card sx={{ bgcolor: '#f5f5f5', maxHeight: '300px', overflow: 'auto' }}>
          <CardContent>
            {logs.length > 0 ? (
              logs.map((log, index) => (
                <Typography key={index} variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.8rem', mb: 0.5 }}>
                  {log}
                </Typography>
              ))
            ) : (
              <Typography variant="body2">No logs yet</Typography>
            )}
          </CardContent>
        </Card>
      </Box>
    </Container>
  );
};

export default TestRecipeFlow; 