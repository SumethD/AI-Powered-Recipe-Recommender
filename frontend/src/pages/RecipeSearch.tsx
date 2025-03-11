import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  TextField,
  Button,
  Grid,
  Card,
  CardContent,
  CardMedia,
  CardActionArea,
  Box,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  OutlinedInput,
  Divider,
  CircularProgress,
  Alert,
  Paper,
  InputAdornment,
  IconButton,
  Tab,
  Tabs,
  SelectChangeEvent,
  Tooltip,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  Search as SearchIcon,
  Clear as ClearIcon,
  Add as AddIcon,
  Favorite as FavoriteIcon,
  FavoriteBorder as FavoriteBorderIcon,
} from '@mui/icons-material';
import { useRecipes } from '../context/RecipeContext';
import { useUser } from '../context/UserContext';
import { recipeApi } from '../services/api';
import { Recipe } from '../context/RecipeContext';
import { styled } from '@mui/material/styles';

interface LocationState {
  ingredients?: string[];
  query?: string;
  activeTab?: number;
  apiProvider?: string;
}

// Styled components
const StyledCard = styled(Card)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  position: 'relative',
  cursor: 'pointer',
  transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
  '&:hover': {
    transform: 'translateY(-4px)',
    boxShadow: theme.shadows[8],
  },
}));

const StyledCardMedia = styled(CardMedia)({
  paddingTop: '56.25%', // 16:9 aspect ratio
  backgroundSize: 'cover',
  cursor: 'pointer',
});

const StyledCardContent = styled(CardContent)({
  flexGrow: 1,
  cursor: 'pointer',
});

const StyledCardActions = styled(CardActionArea)({
  justifyContent: 'space-between',
});

const RecipeSearch: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useUser();
  const { recipes, isLoading, error, searchByIngredients, searchRecipes, toggleFavorite } = useRecipes();
  
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [ingredients, setIngredients] = useState<string>('');
  const [ingredientsList, setIngredientsList] = useState<string[]>([]);
  const [searchTab, setSearchTab] = useState<number>(0);
  
  const [cuisines, setCuisines] = useState<string[]>([]);
  const [diets, setDiets] = useState<string[]>([]);
  const [intolerances, setIntolerances] = useState<string[]>([]);
  
  const [selectedCuisine, setSelectedCuisine] = useState<string>('');
  const [selectedDiet, setSelectedDiet] = useState<string>('');
  const [selectedIntolerances, setSelectedIntolerances] = useState<string[]>([]);
  
  const [isFiltersLoading, setIsFiltersLoading] = useState<boolean>(false);
  const [filtersError, setFiltersError] = useState<string | null>(null);

  // State for API provider
  const [apiProvider, setApiProvider] = useState('edamam'); // Default to edamam
  
  const inputRef = useRef<HTMLInputElement>(null);

  // Load filters data on mount
  useEffect(() => {
    const loadFilters = async () => {
      setIsFiltersLoading(true);
      setFiltersError(null);
      try {
        const [cuisinesRes, dietsRes, intolerancesRes] = await Promise.all([
          recipeApi.getCuisines(),
          recipeApi.getDiets(),
          recipeApi.getIntolerances(),
        ]);
        
        if (cuisinesRes && cuisinesRes.success) {
          setCuisines(cuisinesRes.cuisines || []);
        } else {
          setCuisines([]);
        }
        
        if (dietsRes && dietsRes.success) {
          setDiets(dietsRes.diets || []);
        } else {
          setDiets([]);
        }
        
        if (intolerancesRes && intolerancesRes.success) {
          setIntolerances(intolerancesRes.intolerances || []);
        } else {
          setIntolerances([]);
        }
      } catch (error) {
        console.error('Error loading filters:', error);
        setFiltersError('Failed to load filters. Some search options may not be available.');
      } finally {
        setIsFiltersLoading(false);
      }
    };
    
    loadFilters();
  }, []);

  // Check for existing search state when component mounts
  useEffect(() => {
    // If there are already recipes in the context, don't reset them
    if (recipes.length > 0) {
      return;
    }
    
    // Check if we have search parameters from navigation
    const state = location.state as LocationState;
    if (state) {
      // Restore API provider if provided
      if (state.apiProvider) {
        setApiProvider(state.apiProvider);
      }
      
      if (state.ingredients && state.ingredients.length > 0) {
        setIngredientsList(state.ingredients);
        setSearchTab(0); // Switch to ingredients tab
        handleSearchByIngredients(state.ingredients, state.apiProvider);
      } else if (state.query) {
        setSearchQuery(state.query);
        setSearchTab(1); // Switch to query tab
        handleSearchByQuery(state.query, state.apiProvider);
      }
      
      // Restore active tab if provided
      if (state.activeTab !== undefined) {
        setSearchTab(state.activeTab);
      }
    }
  }, [location.state]);

  // Reset search when component unmounts
  useEffect(() => {
    return () => {
      // Don't clear recipes when navigating to recipe details
      // This allows the search results to persist when navigating back
    };
  }, []);

  const handleAddIngredient = () => {
    if (ingredients.trim() === '') return;
    
    // Add ingredient to list if it's not already there
    if (!ingredientsList.includes(ingredients.trim().toLowerCase())) {
      setIngredientsList([...ingredientsList, ingredients.trim().toLowerCase()]);
    }
    
    // Clear input
    setIngredients('');
  };

  const handleRemoveIngredient = (ingredient: string) => {
    setIngredientsList(ingredientsList.filter(item => item !== ingredient));
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (searchTab === 0) {
        handleAddIngredient();
      } else {
        handleSearchByQuery(searchQuery);
      }
    }
  };

  const handleSearchByIngredients = (ingredients: string[] = ingredientsList, customApiProvider?: string) => {
    if (ingredients.length === 0) return;
    searchByIngredients(ingredients, customApiProvider || apiProvider);
  };

  const handleSearchByQuery = (query: string = searchQuery, customApiProvider?: string) => {
    if (query.trim() === '') return;
    
    const intolerancesString = selectedIntolerances.length > 0 
      ? selectedIntolerances.join(',') 
      : undefined;
    
    searchRecipes(query, selectedCuisine, selectedDiet, intolerancesString, customApiProvider || apiProvider);
  };

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setSearchTab(newValue);
  };

  const handleRecipeClick = (recipeId: number | string) => {
    // Log the recipe ID to the console instead of navigating
    console.log("Recipe clicked:", recipeId);
    
    // Find the recipe in the recipes array
    const recipe = recipes.find(r => r.id === recipeId);
    if (recipe) {
      console.log("Recipe details:", recipe);
    }
    
    // No navigation to recipe details page
  };

  const handleToggleFavorite = (recipe: Recipe, event: React.MouseEvent) => {
    event.stopPropagation();
    if (user) {
      toggleFavorite(recipe);
    } else {
      navigate('/login');
    }
  };

  const handleCuisineChange = (event: SelectChangeEvent) => {
    setSelectedCuisine(event.target.value as string);
  };

  const handleDietChange = (event: SelectChangeEvent) => {
    setSelectedDiet(event.target.value as string);
  };

  const handleIntolerancesChange = (event: SelectChangeEvent<string[]>) => {
    const value = event.target.value;
    setSelectedIntolerances(typeof value === 'string' ? value.split(',') : value);
  };

  const handleApiProviderChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setApiProvider(event.target.checked ? 'edamam' : 'spoonacular');
  };

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" component="h1" gutterBottom>
        Recipe Search
      </Typography>
      
      <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
        <Tabs
          value={searchTab}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
          variant="fullWidth"
          sx={{ mb: 3 }}
        >
          <Tab label="Search by Ingredients" />
          <Tab label="Search by Query" />
        </Tabs>
        
        {/* API Provider Toggle */}
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={apiProvider === 'edamam'}
                onChange={handleApiProviderChange}
                color="primary"
              />
            }
            label={`API: ${apiProvider === 'edamam' ? 'Edamam' : 'Spoonacular'}`}
          />
        </Box>

        {searchTab === 0 ? (
          <>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={8}>
                <TextField
                  fullWidth
                  label="Enter an ingredient"
                  variant="outlined"
                  value={ingredients}
                  onChange={(e) => setIngredients(e.target.value)}
                  onKeyPress={handleKeyPress}
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={handleAddIngredient}
                          disabled={ingredients.trim() === ''}
                          edge="end"
                        >
                          <AddIcon />
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <Button
                  variant="contained"
                  color="primary"
                  fullWidth
                  startIcon={<SearchIcon />}
                  onClick={() => handleSearchByIngredients()}
                  disabled={ingredientsList.length === 0}
                >
                  Search Recipes
                </Button>
              </Grid>
              <Grid item xs={12}>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
                  {ingredientsList.map((ingredient) => (
                    <Chip
                      key={ingredient}
                      label={ingredient}
                      onDelete={() => handleRemoveIngredient(ingredient)}
                      color="primary"
                    />
                  ))}
                  {ingredientsList.length === 0 && (
                    <Typography variant="body2" color="text.secondary">
                      Add ingredients to search for recipes.
                    </Typography>
                  )}
                </Box>
              </Grid>
            </Grid>
          </>
        ) : (
          <>
            <Grid container spacing={2}>
              <Grid item xs={12} md={8}>
                <TextField
                  fullWidth
                  label="Search recipes"
                  variant="outlined"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={handleKeyPress}
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={() => setSearchQuery('')}
                          edge="end"
                          sx={{ visibility: searchQuery ? 'visible' : 'hidden' }}
                        >
                          <ClearIcon />
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <Button
                  variant="contained"
                  color="primary"
                  fullWidth
                  startIcon={<SearchIcon />}
                  onClick={() => handleSearchByQuery()}
                  disabled={searchQuery.trim() === ''}
                >
                  Search Recipes
                </Button>
              </Grid>
              
              <Grid item xs={12}>
                <Divider sx={{ my: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Filters
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={4}>
                    <FormControl fullWidth disabled={isFiltersLoading}>
                      <InputLabel id="cuisine-label">Cuisine</InputLabel>
                      <Select
                        labelId="cuisine-label"
                        value={selectedCuisine}
                        onChange={handleCuisineChange}
                        label="Cuisine"
                      >
                        <MenuItem value="">Any Cuisine</MenuItem>
                        {cuisines.map((cuisine) => (
                          <MenuItem key={cuisine} value={cuisine}>
                            {cuisine}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <FormControl fullWidth disabled={isFiltersLoading}>
                      <InputLabel id="diet-label">Diet</InputLabel>
                      <Select
                        labelId="diet-label"
                        value={selectedDiet}
                        onChange={handleDietChange}
                        label="Diet"
                      >
                        <MenuItem value="">Any Diet</MenuItem>
                        {diets.map((diet) => (
                          <MenuItem key={diet} value={diet}>
                            {diet}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <FormControl fullWidth disabled={isFiltersLoading}>
                      <InputLabel id="intolerances-label">Intolerances</InputLabel>
                      <Select
                        labelId="intolerances-label"
                        multiple
                        value={selectedIntolerances}
                        onChange={handleIntolerancesChange}
                        input={<OutlinedInput label="Intolerances" />}
                        renderValue={(selected) => (
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                            {selected.map((value) => (
                              <Chip key={value} label={value} size="small" />
                            ))}
                          </Box>
                        )}
                      >
                        {intolerances.map((intolerance) => (
                          <MenuItem key={intolerance} value={intolerance}>
                            {intolerance}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12}>
                    <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                      <Button
                        variant="outlined"
                        onClick={() => {
                          setSelectedCuisine('');
                          setSelectedDiet('');
                          setSelectedIntolerances([]);
                        }}
                        disabled={
                          !selectedCuisine && !selectedDiet && selectedIntolerances.length === 0
                        }
                      >
                        Clear Filters
                      </Button>
                    </Box>
                  </Grid>
                </Grid>
              </Grid>
            </Grid>
          </>
        )}
      </Paper>
      
      {isLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error" sx={{ my: 2 }}>
          {error}
        </Alert>
      ) : recipes.length > 0 ? (
        <>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h5">
              Found {recipes.length} Recipes
            </Typography>
          </Box>
          <Grid container spacing={3}>
            {recipes.map((recipe) => (
              <Grid item xs={12} sm={6} md={4} key={recipe.id}>
                <StyledCard>
                  <StyledCardMedia
                    image={recipe.image || 'https://via.placeholder.com/300x200?text=No+Image'}
                    title={recipe.title}
                    onClick={() => handleRecipeClick(recipe.id)}
                  />
                  <StyledCardContent onClick={() => handleRecipeClick(recipe.id)}>
                    <Typography gutterBottom variant="h6" component="div" noWrap>
                      {recipe.title}
                    </Typography>
                    
                    {recipe.usedIngredientCount !== undefined && (
                      <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                        <Chip
                          label={`${recipe.usedIngredientCount} used`}
                          size="small"
                          color="success"
                        />
                        <Chip
                          label={`${recipe.missedIngredientCount} missing`}
                          size="small"
                          color="error"
                        />
                      </Box>
                    )}
                    
                    {recipe.readyInMinutes && (
                      <Typography variant="body2" color="text.secondary">
                        Ready in {recipe.readyInMinutes} minutes
                      </Typography>
                    )}
                  </StyledCardContent>
                  <StyledCardActions>
                    <Tooltip title={user ? 'Add to favorites' : 'Login to save favorites'}>
                      <IconButton 
                        onClick={(e) => handleToggleFavorite(recipe, e)}
                        color="primary"
                      >
                        {recipe.isFavorite ? <FavoriteIcon /> : <FavoriteBorderIcon />}
                      </IconButton>
                    </Tooltip>
                    <Typography variant="body2" color="text.secondary">
                      {recipe.healthScore && `Health Score: ${recipe.healthScore}`}
                    </Typography>
                  </StyledCardActions>
                </StyledCard>
              </Grid>
            ))}
          </Grid>
        </>
      ) : (
        <Box sx={{ textAlign: 'center', my: 4 }}>
          <Typography variant="h6" color="text.secondary">
            No recipes found. Try different search terms or ingredients.
          </Typography>
        </Box>
      )}
    </Container>
  );
};

export default RecipeSearch; 