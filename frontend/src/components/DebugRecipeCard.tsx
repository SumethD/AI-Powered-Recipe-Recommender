import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  Card, 
  CardActionArea, 
  CardContent, 
  CardMedia, 
  Typography, 
  Box, 
  Chip, 
  Stack,
  useTheme,
  styled
} from '@mui/material';
import { Recipe } from '../context/RecipeContext';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import RestaurantIcon from '@mui/icons-material/Restaurant';
import BugReportIcon from '@mui/icons-material/BugReport';

interface DebugRecipeCardProps {
  recipe: Recipe;
  apiProvider?: string;
}

// Styled components for enhanced recipe cards
const StyledCard = styled(Card)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  borderRadius: 16,
  overflow: 'hidden',
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  boxShadow: '0 6px 16px rgba(0,0,0,0.08)',
  position: 'relative',
  '&:hover': {
    transform: 'translateY(-8px)',
    boxShadow: '0 12px 28px rgba(0,0,0,0.15)',
    '& .recipe-image': {
      transform: 'scale(1.05)',
    },
    '& .recipe-overlay': {
      opacity: 0.7,
    },
  },
  '&::after': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '4px',
    background: `linear-gradient(90deg, ${theme.palette.secondary.main}, ${theme.palette.primary.main})`,
  },
}));

const ImageContainer = styled(Box)({
  position: 'relative',
  overflow: 'hidden',
});

const StyledCardMedia = styled(CardMedia)({
  height: 180,
  transition: 'transform 0.5s ease',
  backgroundSize: 'cover',
});

const ImageOverlay = styled(Box)(({ theme }) => ({
  position: 'absolute',
  top: 0,
  left: 0,
  width: '100%',
  height: '100%',
  background: `linear-gradient(to bottom, transparent 50%, ${theme.palette.common.black} 100%)`,
  opacity: 0.5,
  transition: 'opacity 0.3s ease',
}));

const InfoChip = styled(Chip)(({ theme }) => ({
  fontWeight: 600,
  fontSize: '0.75rem',
  borderRadius: 12,
  boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  '& .MuiChip-icon': {
    fontSize: '1rem',
  },
}));

const DebugBadge = styled(Box)(({ theme }) => ({
  position: 'absolute',
  top: 12,
  left: 12,
  backgroundColor: theme.palette.secondary.main,
  color: theme.palette.common.white,
  padding: '4px 8px',
  borderRadius: 12,
  fontSize: '0.7rem',
  fontWeight: 600,
  display: 'flex',
  alignItems: 'center',
  gap: 4,
  zIndex: 2,
  boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
}));

const DebugRecipeCard: React.FC<DebugRecipeCardProps> = ({ recipe, apiProvider }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();

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
      <StyledCard>
        <CardContent>
          <Typography variant="h6" color="error">
            Invalid Recipe Data
          </Typography>
        </CardContent>
      </StyledCard>
    );
  }

  return (
    <StyledCard>
      <CardActionArea onClick={handleClick} sx={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'stretch' }}>
        <ImageContainer>
          <DebugBadge>
            <BugReportIcon sx={{ fontSize: 16 }} />
            Debug
          </DebugBadge>
          
          {recipe.image ? (
            <>
              <StyledCardMedia
                image={recipe.image}
                title={recipe.title}
                className="recipe-image"
              />
              <ImageOverlay className="recipe-overlay" />
            </>
          ) : (
            <Box sx={{ 
              height: 180, 
              bgcolor: 'grey.200', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              position: 'relative'
            }}>
              <RestaurantIcon sx={{ fontSize: 48, color: 'grey.400' }} />
              <ImageOverlay className="recipe-overlay" />
            </Box>
          )}
          
          {/* Time chip positioned on the image */}
          {recipe.readyInMinutes && recipe.readyInMinutes > 0 && (
            <Box sx={{ position: 'absolute', top: 12, right: 12 }}>
              <InfoChip
                icon={<AccessTimeIcon />}
                label={`${recipe.readyInMinutes} min`}
                size="small"
                sx={{ 
                  bgcolor: 'rgba(255, 255, 255, 0.9)',
                  color: theme.palette.primary.main,
                  fontWeight: 600
                }}
              />
            </Box>
          )}
        </ImageContainer>
        
        <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', p: 2 }}>
          <Typography 
            variant="h6" 
            component="div" 
            gutterBottom
            sx={{ 
              fontWeight: 600,
              fontSize: '1.1rem',
              lineHeight: 1.3,
              mb: 1.5,
              height: '2.6rem',
              overflow: 'hidden',
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              textOverflow: 'ellipsis'
            }}
          >
            {recipe.title}
          </Typography>
          
          {recipe.sourceName && (
            <Typography 
              variant="body2" 
              color="text.secondary" 
              sx={{ 
                mb: 1,
                fontStyle: 'italic',
                fontSize: '0.8rem'
              }}
            >
              Source: {recipe.sourceName}
            </Typography>
          )}
          
          <Typography 
            variant="caption" 
            color="text.secondary" 
            sx={{ 
              display: 'block', 
              mb: 1, 
              fontSize: '0.7rem',
              bgcolor: theme.palette.grey[100],
              p: 0.5,
              borderRadius: 1
            }}
          >
            ID: {recipe.id} (Type: {typeof recipe.id})
          </Typography>
          
          {recipe.diets && recipe.diets.length > 0 && (
            <Stack 
              direction="row" 
              spacing={0.5} 
              sx={{ 
                mt: 'auto', 
                flexWrap: 'wrap', 
                gap: 0.5 
              }}
            >
              {recipe.diets.slice(0, 3).map((diet, index) => (
                <Chip 
                  key={index} 
                  label={diet} 
                  size="small" 
                  sx={{ 
                    fontSize: '0.7rem',
                    bgcolor: theme.palette.primary.light,
                    color: theme.palette.common.white,
                    fontWeight: 500,
                    textTransform: 'capitalize'
                  }} 
                />
              ))}
              {recipe.diets.length > 3 && (
                <Chip 
                  label={`+${recipe.diets.length - 3}`} 
                  size="small" 
                  sx={{ 
                    fontSize: '0.7rem',
                    bgcolor: theme.palette.grey[300],
                    fontWeight: 500
                  }} 
                />
              )}
            </Stack>
          )}
        </CardContent>
      </CardActionArea>
    </StyledCard>
  );
};

export default DebugRecipeCard; 