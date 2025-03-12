import React, { useEffect, useState } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { 
  Container, 
  Typography, 
  Box, 
  Grid, 
  Paper, 
  Chip, 
  Divider, 
  Button, 
  List, 
  ListItem, 
  ListItemText, 
  ListItemIcon,
  Card,
  CardMedia,
  CircularProgress,
  Alert,
  IconButton,
  Tooltip,
  styled
} from '@mui/material';
import { 
  AccessTime as AccessTimeIcon, 
  Restaurant as RestaurantIcon, 
  ArrowBack as ArrowBackIcon,
  Favorite as FavoriteIcon,
  FavoriteBorder as FavoriteBorderIcon,
  LocalDining as LocalDiningIcon,
  CheckCircle as CheckCircleIcon,
  FiberManualRecord as FiberManualRecordIcon,
  Code as CodeIcon,  // For displaying source type
  ErrorOutline,
  OpenInNew,
  Refresh,
  Info as InfoIcon
} from '@mui/icons-material';
import { useRecipes } from '../context/RecipeContext';
import { useUser } from '../context/UserContext';
import DOMPurify from 'dompurify';
import recipeInstructionsService, { InstructionsFetchStatus } from '../services/recipeInstructionsService';

// Styled components
const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  borderRadius: 16,
  boxShadow: '0 6px 16px rgba(0,0,0,0.08)',
  height: '100%',
  position: 'relative',
  overflow: 'hidden',
  '&::after': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '4px',
    background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
  },
}));

const RecipeImage = styled(CardMedia)(({ theme }) => ({
  height: 400,
  borderRadius: 16,
  backgroundSize: 'cover',
  backgroundPosition: 'center',
  boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
}));

const InfoChip = styled(Chip)(({ theme }) => ({
  margin: theme.spacing(0.5),
  fontWeight: 600,
  borderRadius: 12,
  boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
}));

const RecipeDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useUser();
  const { getRecipeDetails, toggleFavorite, isFavorite, isLoading, error } = useRecipes();
  const [recipe, setRecipe] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [instructionsSource, setInstructionsSource] = useState<string | null>(null);
  const [fetchingInstructions, setFetchingInstructions] = useState<boolean>(false);
  
  // Add state for tracking instructions fetching status
  const [instructionsStatus, setInstructionsStatus] = useState<InstructionsFetchStatus>({
    status: 'idle',
    retryCount: 0
  });
  
  // Get the API provider from location state or default to 'edamam'
  const apiProvider = location.state?.apiProvider || 'edamam';

  useEffect(() => {
    const fetchRecipeDetails = async () => {
      if (!id) return;
      
      setLoading(true);
      setFetchError(null);
      
      try {
        // Try to get recipe from location state first
        if (location.state?.recipe) {
          setRecipe(location.state.recipe);
        } else {
          // Otherwise fetch it from the API
          const recipeData = await getRecipeDetails(id, apiProvider);
          if (recipeData) {
            setRecipe(recipeData);
          } else {
            setFetchError('Recipe not found');
          }
        }
      } catch (err) {
        console.error('Error fetching recipe details:', err);
        setFetchError('Failed to load recipe details');
      } finally {
        setLoading(false);
      }
    };
    
    fetchRecipeDetails();
  }, [id, getRecipeDetails, location.state, apiProvider]);

  // Update the useEffect that fetches instructions
  useEffect(() => {
    if (recipe && (!recipe.instructions || recipe.instructions === recipe.sourceUrl)) {
      // Create abort controller for cleanup
      const controller = new AbortController();
      
      // Prepare the request
      const request = recipeInstructionsService.prepareRecipeForInstructionsAPI(recipe);
      
      // Fetch instructions with status updates
      recipeInstructionsService.getRecipeInstructions(request, setInstructionsStatus)
        .then(response => {
          // Save both the instructions and the source
          if (response && response.instructions) {
            setRecipe(prev => {
              if (!prev) return null;
              return {
                ...prev,
                instructions: response.instructions,
                source: response.source || 'unknown'
              };
            });
            
            // Update the instructions source state
            if (response.source) {
              setInstructionsSource(response.source);
            }
          }
        })
        .catch(err => {
          console.error('Failed to fetch instructions:', err);
          // We don't set error state here because we'll show the error in the UI based on instructionsStatus
        });
      
      return () => {
        controller.abort();
      };
    }
  }, [recipe?.id, recipe?.sourceUrl]);

  const handleToggleFavorite = async () => {
    if (!recipe) return;
    
    await toggleFavorite(recipe);
    // Update the local recipe state to reflect the favorite status change
    setRecipe({
      ...recipe,
      isFavorite: !recipe.isFavorite
    });
  };

  const handleGoBack = () => {
    navigate(-1); // Go back to previous page
  };

  // Render loading state
  if (loading || isLoading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  // Render error state
  if (fetchError || error) {
    return (
      <Container maxWidth="lg">
        <Alert 
          severity="error" 
          sx={{ mt: 4 }}
          action={
            <Button color="inherit" onClick={handleGoBack}>
              Go Back
            </Button>
          }
        >
          {fetchError || error}
        </Alert>
      </Container>
    );
  }

  // Render no recipe state
  if (!recipe) {
    return (
      <Container maxWidth="lg">
        <Alert 
          severity="info" 
          sx={{ mt: 4 }}
          action={
            <Button color="inherit" onClick={handleGoBack}>
              Go Back
            </Button>
          }
        >
          Recipe not found
        </Alert>
      </Container>
    );
  }

  // Update the instructions section rendering
  const renderInstructions = () => {
    if (!recipe) return null;
    
    if (!recipe.instructions || recipe.instructions === recipe.sourceUrl) {
      // Show different loading/error states based on instructionsStatus
      if (instructionsStatus.status === 'loading') {
        return (
          <Box textAlign="center" my={4} py={4}>
            <CircularProgress size={40} />
            <Typography variant="body1" mt={2}>
              {instructionsStatus.error 
                ? `Loading recipe instructions... ${instructionsStatus.error}` 
                : 'Loading recipe instructions...'}
            </Typography>
            <Typography variant="caption" color="text.secondary" mt={1} display="block">
              First trying to scrape instructions from the recipe website...
              {instructionsStatus.retryCount > 0 && (
                <span> Retry attempt {instructionsStatus.retryCount}...</span>
              )}
            </Typography>
          </Box>
        );
      }
      
      if (instructionsStatus.status === 'failed') {
        return (
          <Box my={4} p={3} border="1px solid" borderColor="error.main" borderRadius={1}>
            <Typography color="error" gutterBottom>
              <ErrorOutline fontSize="small" sx={{ verticalAlign: 'middle', mr: 1 }} />
              {instructionsStatus.error || 'Failed to load cooking instructions'}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1, mb: 2 }}>
              We first tried to scrape instructions from the recipe website, then attempted to 
              generate them with AI, but both methods failed.
            </Typography>
            {recipe.sourceUrl && (
              <Button 
                variant="outlined" 
                color="primary" 
                size="small"
                href={recipe.sourceUrl} 
                target="_blank" 
                rel="noopener noreferrer"
                startIcon={<OpenInNew />}
                sx={{ mt: 1 }}
              >
                View Original Recipe
              </Button>
            )}
            <Button 
              variant="contained" 
              color="primary" 
              size="small"
              onClick={() => {
                setInstructionsStatus({status: 'idle', retryCount: 0});
                const request = recipeInstructionsService.prepareRecipeForInstructionsAPI(recipe);
                recipeInstructionsService.getRecipeInstructions(request, setInstructionsStatus)
                  .then(response => {
                    setRecipe(prev => prev ? { 
                      ...prev, 
                      instructions: response.instructions,
                      source: response.source || 'unknown'
                    } : null);
                    
                    setInstructionsSource(response.source || null);
                  })
                  .catch(err => {
                    console.error('Failed to fetch instructions on retry:', err);
                  });
              }}
              startIcon={<Refresh />}
              sx={{ mt: 1, ml: 1 }}
            >
              Try Again
            </Button>
          </Box>
        );
      }
      
      // Default case - waiting to start fetching
      return (
        <Box textAlign="center" my={4}>
          <CircularProgress size={40} />
          <Typography variant="body1" mt={2}>
            Preparing recipe instructions...
          </Typography>
          <Typography variant="caption" color="text.secondary" mt={1} display="block">
            We'll first try to scrape instructions from the recipe website.
            If that fails, we'll generate them with AI.
          </Typography>
        </Box>
      );
    }
    
    // Use recipe.source if instructionsSource is not set
    const instructionSource = instructionsSource || recipe.source || "unknown";
    
    // Map source values to user-friendly labels
    const getSourceLabel = (source: string) => {
      switch(source) {
        case 'scraped': return 'From Website';
        case 'ai-generated': return 'AI-Generated';
        case 'basic': return 'Basic Template';
        default: return 'Basic Template';
      }
    };
    
    // Map source values to appropriate colors
    const getSourceColor = (source: string) => {
      switch(source) {
        case 'scraped': return 'success';
        case 'ai-generated': return 'secondary';
        case 'basic': 
        default: return 'default';
      }
    };
    
    return (
      <Paper elevation={0} sx={{ p: 4, mt: 4, bgcolor: 'background.paper', borderRadius: 2, boxShadow: '0 2px 10px rgba(0,0,0,0.05)' }}>
        <Typography variant="h5" component="h3" mb={3} sx={{ fontWeight: 600 }}>
          Cooking Instructions
          <Tooltip title={
            instructionSource === 'scraped' 
              ? 'These instructions were scraped directly from the recipe website' 
              : instructionSource === 'ai-generated' 
                ? 'These instructions were generated using AI because we couldn\'t scrape the website' 
                : 'These are basic instructions created as a fallback when other methods failed'
          }>
            <Chip 
              icon={<CodeIcon />} 
              label={getSourceLabel(instructionSource)} 
              size="small" 
              color={getSourceColor(instructionSource)}
              sx={{ ml: 2, height: 24 }}
            />
          </Tooltip>
        </Typography>

        {/* Enhanced styling for recipe instructions with better readability */}
        <Box sx={{ mb: 3 }}>
          {recipe.instructions.split(/\d+\./).filter(Boolean).map((step, index) => (
            <Box 
              key={index} 
              sx={{ 
                display: 'flex', 
                alignItems: 'flex-start', 
                mb: 2,
                p: 2,
                borderRadius: 1,
                bgcolor: index % 2 === 0 ? 'rgba(0,0,0,0.02)' : 'transparent',
                transition: 'all 0.2s ease',
                '&:hover': {
                  bgcolor: 'rgba(0,0,0,0.04)'
                }
              }}
            >
              <Box 
                sx={{ 
                  minWidth: 32, 
                  height: 32, 
                  borderRadius: '50%', 
                  bgcolor: 'primary.main', 
                  color: 'white', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  mr: 2,
                  fontWeight: 'bold'
                }}
              >
                {index + 1}
              </Box>
              <Typography 
                variant="body1" 
                sx={{ 
                  pt: 0.5,
                  lineHeight: 1.6,
                  color: 'text.primary'
                }}
              >
                {step.trim()}
              </Typography>
            </Box>
          ))}
        </Box>

        {recipe.sourceUrl && (
          <Button 
            variant="outlined" 
            color="primary"
            href={recipe.sourceUrl} 
            target="_blank" 
            rel="noopener noreferrer"
            startIcon={<OpenInNew />}
            sx={{ mt: 2 }}
          >
            View Original Recipe
          </Button>
        )}
      </Paper>
    );
  };

  return (
    <Container maxWidth="lg">
      {/* Back button and favorite button */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Button 
          startIcon={<ArrowBackIcon />} 
          onClick={handleGoBack}
          variant="outlined"
        >
          Back to Search
        </Button>
        
        {user && (
          <Tooltip title={recipe.isFavorite ? "Remove from favorites" : "Add to favorites"}>
            <IconButton 
              onClick={handleToggleFavorite}
              color={recipe.isFavorite ? "error" : "default"}
              sx={{ 
                border: '1px solid',
                borderColor: 'divider',
                p: 1.5
              }}
            >
              {recipe.isFavorite ? <FavoriteIcon /> : <FavoriteBorderIcon />}
            </IconButton>
          </Tooltip>
        )}
      </Box>

      {/* Recipe title */}
      <Typography 
        variant="h3" 
        component="h1" 
        gutterBottom
        sx={{ 
          fontWeight: 700,
          mb: 3,
          fontSize: { xs: '2rem', md: '2.5rem' }
        }}
      >
        {recipe.title}
      </Typography>

      <Grid container spacing={4}>
        {/* Left column - Image and quick info */}
        <Grid item xs={12} md={6}>
          {/* Recipe image */}
          {recipe.image ? (
            <RecipeImage
              image={recipe.image}
              title={recipe.title}
            />
          ) : (
            <Box 
              sx={{ 
                height: 400, 
                bgcolor: 'grey.200', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                borderRadius: 4
              }}
            >
              <RestaurantIcon sx={{ fontSize: 80, color: 'grey.400' }} />
            </Box>
          )}

          {/* Quick info */}
          <Box sx={{ mt: 3, display: 'flex', flexWrap: 'wrap', gap: 2 }}>
            {recipe.readyInMinutes && (
              <InfoChip 
                icon={<AccessTimeIcon />} 
                label={`${recipe.readyInMinutes} minutes`}
                color="primary"
                variant="outlined"
              />
            )}
            
            {recipe.servings && (
              <InfoChip 
                icon={<RestaurantIcon />} 
                label={`${recipe.servings} servings`}
                color="primary"
                variant="outlined"
              />
            )}
            
            {recipe.sourceName && (
              <InfoChip 
                label={`Source: ${recipe.sourceName}`}
                variant="outlined"
              />
            )}
          </Box>

          {/* Diets and cuisines */}
          {recipe.diets && recipe.diets.length > 0 && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="h6" gutterBottom>
                Diets
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {recipe.diets.map((diet: string, index: number) => (
                  <Chip 
                    key={index} 
                    label={diet} 
                    color="success"
                    sx={{ textTransform: 'capitalize' }}
                  />
                ))}
              </Box>
            </Box>
          )}
          
          {recipe.cuisines && recipe.cuisines.length > 0 && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="h6" gutterBottom>
                Cuisines
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {recipe.cuisines.map((cuisine: string, index: number) => (
                  <Chip 
                    key={index} 
                    label={cuisine} 
                    color="secondary"
                    sx={{ textTransform: 'capitalize' }}
                  />
                ))}
              </Box>
            </Box>
          )}
        </Grid>

        {/* Right column - Ingredients and instructions */}
        <Grid item xs={12} md={6}>
          {/* Ingredients */}
          <StyledPaper>
            <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
              Ingredients
            </Typography>
            <List>
              {recipe.extendedIngredients ? (
                recipe.extendedIngredients.map((ingredient: any, index: number) => (
                  <ListItem key={index} disableGutters>
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      <FiberManualRecordIcon color="primary" fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary={ingredient.original || `${ingredient.amount} ${ingredient.unit} ${ingredient.name}`} />
                  </ListItem>
                ))
              ) : (
                <ListItem disableGutters>
                  <ListItemText primary="No ingredients information available" />
                </ListItem>
              )}
            </List>

            {/* Divider between Ingredients and Instructions */}
            <Divider sx={{ my: 3 }} />

            {/* Instructions */}
            <Box sx={{ position: 'relative' }}>
              {renderInstructions()}
            </Box>
          </StyledPaper>
        </Grid>
      </Grid>

      {/* Nutrition information with improved visual hierarchy */}
      {recipe.nutrition && recipe.nutrition.nutrients && (
        <StyledPaper sx={{ mt: 4 }}>
          <Box sx={{ 
            borderBottom: '1px solid',
            borderColor: 'divider',
            pb: 1,
            mb: 3
          }}>
            <Typography variant="h5" sx={{ fontWeight: 600 }}>
              Nutrition Information
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Per serving • Values directly from recipe source
            </Typography>
          </Box>
          
          <Box sx={{ mb: 2 }}>
            <Grid container spacing={3}>
              {(() => {
                // Define the exact priority order for nutrients - these will be displayed first if available
                const priorityOrder = [
                  { key: 'calories', label: 'Calories', color: 'primary.main' },
                  { key: 'energy', label: 'Energy', color: 'primary.main' },
                  { key: 'protein', label: 'Protein', color: 'success.main' },
                  { key: 'fat', label: 'Fat', color: 'warning.main' },
                  { key: 'carbs', label: 'Carbs', color: 'secondary.main' },
                  { key: 'carbohydrates', label: 'Carbohydrates', color: 'secondary.main' },
                  { key: 'fiber', label: 'Fiber', color: 'info.main' },
                  { key: 'sugar', label: 'Sugar', color: 'error.light' },
                  { key: 'sugars', label: 'Sugars', color: 'error.light' },
                  { key: 'sodium', label: 'Sodium', color: 'warning.light' },
                  { key: 'cholesterol', label: 'Cholesterol', color: 'warning.light' },
                  { key: 'saturated', label: 'Saturated Fat', color: 'warning.dark' },
                ];
                
                // Define tooltips for specialized nutrition terms
                const tooltips = {
                  'Saturated': 'Saturated fats are fats that have no double bonds between carbon molecules. Diets high in saturated fat may increase cholesterol levels.',
                  'Monounsaturated': 'Monounsaturated fats have one unsaturated carbon bond. They can help reduce bad cholesterol levels and provide nutrients for cell development.',
                  'Polyunsaturated': 'Polyunsaturated fats have more than one unsaturated carbon bond. They include omega-3 and omega-6 fatty acids, which are essential for brain function and cell growth.',
                  'Trans': 'Trans fats are artificially created fats that can increase bad cholesterol, lower good cholesterol, and increase risk of heart disease. They should be limited in your diet.',
                  'Carbohydrates': 'Carbohydrates are the body\'s main source of energy. They include sugars, starches, and fiber.',
                  'Cholesterol': 'Cholesterol is a waxy, fat-like substance found in all cells of the body. While needed for making hormones and digesting fats, high levels can increase heart disease risk.',
                  'Sodium': 'Sodium is an electrolyte that helps maintain fluid balance. Most sodium comes from salt. Too much can increase blood pressure in some people.',
                  'Fiber': 'Fiber is the indigestible part of plant foods that helps with digestion, controls blood sugar, and reduces cholesterol.',
                  'Sugars': 'Sugars are simple carbohydrates that provide quick energy but little nutritional value. They include naturally occurring sugars (like in fruit) and added sugars.',
                };
                
                // Copy nutrients array to avoid modifying the original
                const allNutrients = [...recipe.nutrition.nutrients];
                
                // Create an array to hold the nutrients we'll display
                const displayNutrients = [];
                
                // First, find and add the priority nutrients in their specified order
                for (const priority of priorityOrder) {
                  // Look for exact matches first
                  const exactMatch = allNutrients.find(
                    n => n.name.toLowerCase() === priority.key.toLowerCase()
                  );
                  
                  if (exactMatch) {
                    displayNutrients.push({
                      ...exactMatch,
                      displayName: priority.label,
                      color: priority.color
                    });
                    // Remove from original array to avoid duplicates
                    const index = allNutrients.findIndex(n => n.name === exactMatch.name);
                    if (index !== -1) allNutrients.splice(index, 1);
                    continue;
                  }
                  
                  // If no exact match, look for partial matches
                  const partialMatch = allNutrients.find(
                    n => n.name.toLowerCase().includes(priority.key.toLowerCase())
                  );
                  
                  if (partialMatch) {
                    displayNutrients.push({
                      ...partialMatch,
                      displayName: priority.label,
                      color: priority.color
                    });
                    // Remove from original array to avoid duplicates
                    const index = allNutrients.findIndex(n => n.name === partialMatch.name);
                    if (index !== -1) allNutrients.splice(index, 1);
                  }
                }
                
                // If we don't have 8 nutrients yet, add more common ones
                if (displayNutrients.length < 8 && allNutrients.length > 0) {
                  // Prioritize fat subtypes that may be important
                  const fatSubtypes = allNutrients.filter(n => 
                    n.name.toLowerCase().includes('saturated') ||
                    n.name.toLowerCase().includes('monounsaturated') ||
                    n.name.toLowerCase().includes('polyunsaturated') ||
                    n.name.toLowerCase().includes('trans')
                  );
                  
                  // Add fat subtypes to display nutrients
                  for (const subtype of fatSubtypes) {
                    if (displayNutrients.length < 8) {
                      displayNutrients.push({
                        ...subtype,
                        displayName: subtype.name,
                        color: 'warning.dark'
                      });
                      // Remove from original array to avoid duplicates
                      const index = allNutrients.findIndex(n => n.name === subtype.name);
                      if (index !== -1) allNutrients.splice(index, 1);
                    }
                  }
                  
                  // Fill remaining slots with other nutrients
                  if (displayNutrients.length < 8) {
                    // Sort remaining nutrients by amount (highest first) to show the most significant ones
                    const sortedRemaining = [...allNutrients].sort((a, b) => b.amount - a.amount);
                    for (const nutrient of sortedRemaining) {
                      if (displayNutrients.length < 8) {
                        displayNutrients.push({
                          ...nutrient,
                          displayName: nutrient.name,
                          color: 'text.primary'
                        });
                      }
                    }
                  }
                }
                
                // Render the nutrients
                return displayNutrients.map((nutrient, index) => {
                  // Determine if this nutrient needs a tooltip
                  let needsTooltip = false;
                  let tooltipText = '';
                  
                  // Check for exact tooltip matches
                  if (tooltips[nutrient.name]) {
                    needsTooltip = true;
                    tooltipText = tooltips[nutrient.name];
                  } else {
                    // Check for partial matches in tooltips
                    for (const [key, text] of Object.entries(tooltips)) {
                      if (nutrient.name.includes(key)) {
                        needsTooltip = true;
                        tooltipText = text;
                        break;
                      }
                    }
                  }
                  
                  // Default tooltip for any nutrient
                  if (!needsTooltip) {
                    needsTooltip = true;
                    tooltipText = `${nutrient.name} is an important nutrient tracked in this recipe. The value shown comes directly from the recipe source.`;
                  }
                  
                  // Determine if this is a primary nutrient (calories/energy)
                  const isPrimaryNutrient = 
                    nutrient.name.toLowerCase().includes('calories') || 
                    nutrient.name.toLowerCase().includes('energy');
                  
                  return (
                    <Grid item xs={6} sm={3} key={index}>
                      <Box 
                        sx={{ 
                          textAlign: 'center', 
                          p: 2.5,
                          borderRadius: 2,
                          bgcolor: isPrimaryNutrient ? 'primary.50' : 'background.paper',
                          boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
                          height: '100%',
                          display: 'flex',
                          flexDirection: 'column',
                          justifyContent: 'center',
                          transition: 'all 0.2s ease',
                          '&:hover': {
                            boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                            transform: 'translateY(-2px)'
                          }
                        }}
                      >
                        <Typography 
                          variant={isPrimaryNutrient ? "h5" : "h6"} 
                          color={nutrient.color || "primary"}
                          sx={{ fontWeight: isPrimaryNutrient ? 700 : 600 }}
                        >
                          {Math.round(nutrient.amount)}
                          <Typography component="span" variant="caption" sx={{ ml: 0.5 }}>
                            {nutrient.unit}
                          </Typography>
                        </Typography>
                        
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mt: 1 }}>
                          <Typography 
                            variant="body2" 
                            color="text.secondary"
                            sx={{ fontWeight: isPrimaryNutrient ? 500 : 400 }}
                          >
                            {nutrient.displayName || nutrient.name}
                          </Typography>
                          
                          <Tooltip 
                            title={tooltipText} 
                            arrow 
                            placement="top"
                          >
                            <IconButton size="small" sx={{ p: 0, ml: 0.5 }}>
                              <InfoIcon 
                                fontSize="small"
                                sx={{ 
                                  fontSize: '0.75rem', 
                                  color: 'info.main'
                                }} 
                              />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </Box>
                    </Grid>
                  );
                });
              })()}
            </Grid>
          </Box>
        </StyledPaper>
      )}

      {/* Summary */}
      {recipe.summary && (
        <StyledPaper sx={{ mt: 4 }}>
          <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
            Summary
          </Typography>
          <Box 
            dangerouslySetInnerHTML={{ 
              __html: DOMPurify.sanitize(recipe.summary) 
            }} 
            sx={{ 
              '& a': { color: 'primary.main' }
            }}
          />
        </StyledPaper>
      )}
    </Container>
  );
};

export default RecipeDetails; 