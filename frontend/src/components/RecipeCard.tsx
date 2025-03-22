import React, { useState } from 'react';
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
  styled,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  DialogContentText
} from '@mui/material';
import { Recipe } from '../context/RecipeContext';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import RestaurantIcon from '@mui/icons-material/Restaurant';
import FavoriteIcon from '@mui/icons-material/Favorite';
import FavoriteBorderIcon from '@mui/icons-material/FavoriteBorder';
import DeleteIcon from '@mui/icons-material/Delete';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import { useShoppingList } from '../context/ShoppingListContext';
import { useRecipes } from '../context/RecipeContext';
import { useAuth } from '../context/AuthContext';

interface RecipeCardProps {
  recipe: Recipe;
  apiProvider?: string;
  user?: any; // User object to check if logged in
  toggleFavorite?: (recipe: Recipe, event: React.MouseEvent) => void;
  isFavoritesPage?: boolean; // Flag to indicate if this card is being used on the favorites page
}

// Styled components
const CardContainer = styled(Card)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  height: '100%',
  transition: 'transform 0.3s ease, box-shadow 0.3s ease',
  position: 'relative',
  '&:hover': {
    transform: 'translateY(-5px)',
    boxShadow: theme.shadows[8],
  },
}));

const StyledCardMedia = styled(CardMedia)(({ theme }) => ({
  paddingTop: '56.25%', // 16:9 aspect ratio
  position: 'relative',
}));

const FavoriteButton = styled(IconButton)(({ theme }) => ({
  position: 'absolute',
  top: 12,
  right: 12,
  backgroundColor: 'rgba(255, 255, 255, 0.9)',
  boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
  padding: 8,
  zIndex: 10,
  transition: 'all 0.2s ease',
  '&:hover': {
    backgroundColor: theme.palette.secondary.light,
    transform: 'scale(1.1)',
  },
}));

const DeleteButton = styled(IconButton)(({ theme }) => ({
  position: 'absolute',
  top: 12,
  left: 12,
  backgroundColor: 'rgba(255, 255, 255, 0.9)',
  boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
  padding: 8,
  zIndex: 10,
  transition: 'all 0.2s ease',
  '&:hover': {
    backgroundColor: theme.palette.error.light,
    color: theme.palette.common.white,
    transform: 'scale(1.1)',
  },
}));

const MoreButton = styled(IconButton)(({ theme }) => ({
  position: 'absolute',
  top: 12,
  right: 60,
  backgroundColor: 'rgba(255, 255, 255, 0.9)',
  boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
  padding: 8,
  zIndex: 10,
  transition: 'all 0.2s ease',
  '&:hover': {
    backgroundColor: theme.palette.primary.light,
    color: theme.palette.common.white,
    transform: 'scale(1.1)',
  },
}));

const RecipeCard: React.FC<RecipeCardProps> = ({ 
  recipe, 
  apiProvider,
  user,
  toggleFavorite,
  isFavoritesPage
}) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const { addToShoppingList } = useShoppingList();
  const { isFavorite, toggleFavorite: contextToggleFavorite } = useRecipes();
  const { user: authUser } = useAuth();
  
  const handleClick = () => {
    navigate(`/recipe/${recipe.id}`, {
      state: { recipe, apiProvider }
    });
  };

  const handleToggleFavorite = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (toggleFavorite) {
      toggleFavorite(recipe, e);
    } else {
      contextToggleFavorite(recipe);
    }
  };

  const handleMoreClick = (event: React.MouseEvent<HTMLElement>) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = (event: React.MouseEvent) => {
    event.stopPropagation();
    setAnchorEl(null);
  };

  const handleAddToShoppingList = (event: React.MouseEvent) => {
    event.stopPropagation();
    if (recipe.extendedIngredients && recipe.extendedIngredients.length > 0) {
      addToShoppingList(recipe);
    }
    setAnchorEl(null);
  };

  const handleDeleteConfirmOpen = (event: React.MouseEvent) => {
    event.stopPropagation();
    setAnchorEl(null);
    setConfirmDialogOpen(true);
  };

  const handleDeleteConfirm = (event: React.MouseEvent) => {
    event.stopPropagation();
    if (toggleFavorite) {
      toggleFavorite(recipe, event);
    } else {
      contextToggleFavorite(recipe);
    }
    setConfirmDialogOpen(false);
  };

  const handleDeleteCancel = (event: React.MouseEvent) => {
    event.stopPropagation();
    setConfirmDialogOpen(false);
  };

  const recipeIsFavorite = recipe.isFavorite !== undefined 
    ? recipe.isFavorite 
    : isFavorite(recipe.id);

  return (
    <>
      <CardContainer>
        <CardActionArea onClick={handleClick} sx={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'stretch' }}>
          <Box sx={{ position: 'relative' }}>
            <StyledCardMedia
              image={recipe.image || '/placeholder-recipe.jpg'}
              title={recipe.title}
            />
            
            {user && authUser && (
              <>
                {isFavoritesPage ? (
                  <DeleteButton 
                    onClick={(e) => {
                      e.stopPropagation();
                      setConfirmDialogOpen(true);
                    }}
                    size="small"
                    aria-label="remove from favorites"
                  >
                    <DeleteIcon />
                  </DeleteButton>
                ) : (
                  <FavoriteButton 
                    onClick={handleToggleFavorite}
                    size="small"
                    aria-label={recipeIsFavorite ? "remove from favorites" : "add to favorites"}
                    color={recipeIsFavorite ? "secondary" : "default"}
                  >
                    {recipeIsFavorite ? <FavoriteIcon /> : <FavoriteBorderIcon />}
                  </FavoriteButton>
                )}
                
                <MoreButton
                  onClick={handleMoreClick}
                  size="small"
                  aria-label="more options"
                >
                  <MoreVertIcon />
                </MoreButton>
              </>
            )}
          </Box>
          
          <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
            <Typography 
              variant="h6" 
              component="h2" 
              gutterBottom
              sx={{ 
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                display: '-webkit-box',
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical',
                lineHeight: 1.4,
                height: '2.8em'
              }}
            >
              {recipe.title}
            </Typography>
            
            <Box sx={{ mt: 'auto', pt: 1 }}>
              <Stack direction="row" spacing={2} alignItems="center">
                {recipe.readyInMinutes && (
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <AccessTimeIcon fontSize="small" sx={{ mr: 0.5, color: theme.palette.text.secondary }} />
                    <Typography variant="body2" color="text.secondary">
                      {recipe.readyInMinutes} min
                    </Typography>
                  </Box>
                )}
                
                {recipe.servings && (
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <RestaurantIcon fontSize="small" sx={{ mr: 0.5, color: theme.palette.text.secondary }} />
                    <Typography variant="body2" color="text.secondary">
                      {recipe.servings} {recipe.servings === 1 ? 'serving' : 'servings'}
                    </Typography>
                  </Box>
                )}
              </Stack>
              
              {recipe.diets && recipe.diets.length > 0 && (
                <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {recipe.diets.slice(0, 2).map((diet, index) => (
                    <Chip
                      key={index}
                      label={diet}
                      size="small"
                      sx={{
                        background: theme.palette.primary.light,
                        color: theme.palette.primary.contrastText,
                        fontSize: '0.7rem'
                      }}
                    />
                  ))}
                  {recipe.diets.length > 2 && (
                    <Chip
                      label={`+${recipe.diets.length - 2}`}
                      size="small"
                      sx={{
                        background: theme.palette.grey[300],
                        color: theme.palette.text.primary,
                        fontSize: '0.7rem'
                      }}
                    />
                  )}
                </Box>
              )}
            </Box>
          </CardContent>
        </CardActionArea>
      </CardContainer>
      
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleAddToShoppingList}>
          <ListItemIcon>
            <ShoppingCartIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Add to Shopping List</ListItemText>
        </MenuItem>
        
        {isFavoritesPage && (
          <MenuItem onClick={handleDeleteConfirmOpen}>
            <ListItemIcon>
              <DeleteIcon fontSize="small" color="error" />
            </ListItemIcon>
            <ListItemText>Remove from Favorites</ListItemText>
          </MenuItem>
        )}
      </Menu>
      
      <Dialog
        open={confirmDialogOpen}
        onClose={handleDeleteCancel}
        onClick={(e) => e.stopPropagation()}
      >
        <DialogTitle>Remove from Favorites?</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to remove "{recipe.title}" from your favorites?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteCancel} color="primary">
            Cancel
          </Button>
          <Button onClick={handleDeleteConfirm} color="error">
            Remove
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default RecipeCard; 