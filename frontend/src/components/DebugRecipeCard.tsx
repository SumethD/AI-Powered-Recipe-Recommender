import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Card, CardActionArea, CardContent, CardMedia, Typography, Box, Chip, Stack } from '@mui/material';
import { Recipe } from '../context/RecipeContext';

interface DebugRecipeCardProps {
  recipe: Recipe;
  apiProvider?: string;
}

const DebugRecipeCard: React.FC<DebugRecipeCardProps> = ({ recipe, apiProvider }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleClick = () => {
    // Log the recipe data for debugging
    console.log("Recipe card clicked:", {
      id: recipe.id,
      title: recipe.title,
      apiProvider: apiProvider
    });

    // Display detailed recipe data in console
    console.log("Debug Recipe Details:", recipe);
    
    // No navigation to recipe details page
  };

  // Ensure we have a valid recipe with required fields
  if (!recipe || !recipe.id || !recipe.title) {
    console.error("Invalid recipe data:", recipe);
    return (
      <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <CardContent>
          <Typography variant="h6" color="error">
            Invalid Recipe Data
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardActionArea onClick={handleClick} sx={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'stretch' }}>
        {recipe.image ? (
          <CardMedia
            component="img"
            height="140"
            image={recipe.image}
            alt={recipe.title}
            sx={{ objectFit: 'cover' }}
          />
        ) : (
          <Box sx={{ height: 140, bgcolor: 'grey.300', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              No image available
            </Typography>
          </Box>
        )}
        <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
          <Typography variant="h6" component="div" gutterBottom>
            {recipe.title}
          </Typography>
          
          <Box sx={{ mt: 'auto' }}>
            {recipe.readyInMinutes && recipe.readyInMinutes > 0 && (
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Ready in {recipe.readyInMinutes} minutes
              </Typography>
            )}
            
            {recipe.sourceName && (
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Source: {recipe.sourceName}
              </Typography>
            )}
            
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1, fontSize: '0.7rem' }}>
              ID: {recipe.id} (Type: {typeof recipe.id})
            </Typography>
            
            {recipe.diets && recipe.diets.length > 0 && (
              <Stack direction="row" spacing={0.5} sx={{ mt: 1, flexWrap: 'wrap', gap: 0.5 }}>
                {recipe.diets.slice(0, 3).map((diet, index) => (
                  <Chip key={index} label={diet} size="small" sx={{ fontSize: '0.6rem' }} />
                ))}
              </Stack>
            )}
          </Box>
        </CardContent>
      </CardActionArea>
    </Card>
  );
};

export default DebugRecipeCard; 