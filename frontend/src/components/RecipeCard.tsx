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

interface RecipeCardProps {
  recipe: Recipe;
  apiProvider?: string;
  user?: any; // User object to check if logged in
  toggleFavorite?: (recipe: Recipe, event: React.MouseEvent) => void;
  isFavoritesPage?: boolean; // Flag to indicate if this card is being used on the favorites page
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
    background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
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

const FavoriteButton = styled(IconButton)(({ theme }) => ({
  position: 'absolute',
  top: 12,
  left: 12,
  backgroundColor: 'rgba(255, 255, 255, 0.9)',
  boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
  padding: 8,
  zIndex: 10,
  transition: 'all 0.2s ease',
  '&:hover': {
    backgroundColor: 'rgba(255, 255, 255, 1)',
    transform: 'scale(1.1)',
  },
}));

const RecipeCard: React.FC<RecipeCardProps> = ({ 
  recipe, 
  apiProvider, 
  user, 
  toggleFavorite,
  isFavoritesPage = false
}) => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const [loginDialogOpen, setLoginDialogOpen] = useState(false);
  const [menuAnchorEl, setMenuAnchorEl] = useState<null | HTMLElement>(null);
  const { addRecipeToList, isRecipeInList } = useShoppingList();
  const [showAddedMessage, setShowAddedMessage] = useState(false);
  
  const isInShoppingList = isRecipeInList && recipe.id ? isRecipeInList(recipe.id) : false;
  
  // Handle showing the added to shopping list message
  React.useEffect(() => {
    if (showAddedMessage) {
      const timer = setTimeout(() => {
        setShowAddedMessage(false);
      }, 2000);
      
      return () => clearTimeout(timer);
    }
  }, [showAddedMessage]);

  const handleClick = () => {
    // Navigate to recipe details page
    navigate(`/recipe/${recipe.id}`, {
      state: {
        recipe: recipe,
        apiProvider: apiProvider
      }
    });
  };

  const handleFavoriteClick = (event: React.MouseEvent) => {
    event.stopPropagation();
    
    if (!user) {
      // If user is not logged in, show login dialog
      setLoginDialogOpen(true);
    } else if (toggleFavorite) {
      // If user is logged in and toggleFavorite function is provided, call it
      toggleFavorite(recipe, event);
    }
  };
  
  const handleMenuOpen = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.stopPropagation();
    setMenuAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setMenuAnchorEl(null);
  };

  const handleAddToShoppingList = () => {
    if (recipe && addRecipeToList) {
      addRecipeToList(recipe);
      setShowAddedMessage(true);
      handleMenuClose();
    }
  };

  const handleLoginRedirect = () => {
    setLoginDialogOpen(false);
    navigate('/login');
  };

  const handleSignupRedirect = () => {
    setLoginDialogOpen(false);
    navigate('/signup');
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
    <>
      <StyledCard>
        <CardActionArea onClick={handleClick} sx={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'stretch' }}>
          <ImageContainer>
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
            
            {/* Favorite button positioned on the top left of the image */}
            <FavoriteButton 
              onClick={handleFavoriteClick}
              color={isFavoritesPage ? "error" : "primary"}
              aria-label={isFavoritesPage ? 'Remove from favorites' : (recipe.isFavorite ? 'Remove from favorites' : 'Add to favorites')}
            >
              {isFavoritesPage ? 
                <DeleteIcon /> : 
                (recipe.isFavorite ? 
                  <FavoriteIcon sx={{ color: theme.palette.error.main }} /> : 
                  <FavoriteBorderIcon />)
              }
            </FavoriteButton>
            
            {/* Shopping list notification */}
            {showAddedMessage && (
              <Box 
                sx={{
                  position: 'absolute',
                  bottom: 0,
                  left: 0,
                  right: 0,
                  backgroundColor: 'rgba(0, 0, 0, 0.8)',
                  color: 'white',
                  textAlign: 'center',
                  py: 1,
                  zIndex: 20,
                }}
              >
                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                  Added to Shopping List
                </Typography>
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
                lineHeight: 1.4,
                mb: 1.5,
                minHeight: '3.5rem',
                overflow: 'hidden',
                display: '-webkit-box',
                WebkitLineClamp: 3,
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
                  mb: 1.5,
                  fontStyle: 'italic',
                  fontSize: '0.8rem',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap'
                }}
              >
                Source: {recipe.sourceName}
              </Typography>
            )}
            
            <Box sx={{ 
              mt: 'auto', 
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <Stack 
                direction="row" 
                spacing={0.5} 
                sx={{ 
                  flexWrap: 'wrap', 
                  gap: 0.5,
                  pb: 0.5,
                  flexGrow: 1
                }}
              >
                {recipe.diets && recipe.diets.length > 0 && recipe.diets.slice(0, 3).map((diet, index) => (
                  <Chip 
                    key={index} 
                    label={diet} 
                    size="small" 
                    sx={{ 
                      fontSize: '0.7rem',
                      maxWidth: '100%',
                      bgcolor: theme.palette.primary.light,
                      color: theme.palette.common.white,
                      fontWeight: 500,
                      textTransform: 'capitalize',
                      '& .MuiChip-label': {
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                        maxWidth: '28ch'
                      }
                    }} 
                  />
                ))}
                {recipe.diets && recipe.diets.length > 3 && (
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
              
              {/* Options menu button */}
              <IconButton 
                sx={{ 
                  padding: 4,
                  width: 28,
                  height: 28,
                  minWidth: 28,
                  minHeight: 28,
                  ml: 1,
                  color: theme.palette.text.secondary,
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    backgroundColor: 'rgba(0, 0, 0, 0.04)',
                    color: theme.palette.primary.main,
                    transform: 'rotate(90deg)',
                  },
                }}
                onClick={(e) => {
                  e.stopPropagation();
                  handleMenuOpen(e);
                }}
                size="small"
                aria-label="more options"
              >
                <MoreVertIcon fontSize="small" sx={{ fontSize: 16 }} />
              </IconButton>
            </Box>
          </CardContent>
        </CardActionArea>
      </StyledCard>

      {/* Login/Signup Dialog */}
      <Dialog open={loginDialogOpen} onClose={() => setLoginDialogOpen(false)}>
        <DialogTitle>Login Required</DialogTitle>
        <DialogContent>
          <DialogContentText>
            You need to log in to save recipes to your favorites.
          </DialogContentText>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3, justifyContent: 'center', gap: 2 }}>
          <Button 
            variant="contained" 
            onClick={handleLoginRedirect}
            color="primary"
          >
            Login
          </Button>
          <Button 
            variant="outlined" 
            onClick={handleSignupRedirect}
            color="primary"
          >
            Sign Up
          </Button>
          <Button 
            variant="text" 
            onClick={() => setLoginDialogOpen(false)}
            color="inherit"
          >
            Cancel
          </Button>
        </DialogActions>
      </Dialog>

      {/* Shopping List Menu */}
      <Menu
        anchorEl={menuAnchorEl}
        open={Boolean(menuAnchorEl)}
        onClose={handleMenuClose}
        onClick={(e) => e.stopPropagation()}
        PaperProps={{
          elevation: 3,
          sx: {
            minWidth: 200,
            borderRadius: 2,
            overflow: 'visible',
            boxShadow: '0 8px 20px rgba(0,0,0,0.15)',
          },
        }}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        <MenuItem 
          onClick={handleAddToShoppingList}
          disabled={isInShoppingList}
        >
          <ListItemIcon>
            <ShoppingCartIcon fontSize="small" color={isInShoppingList ? "disabled" : "primary"} />
          </ListItemIcon>
          <ListItemText>
            {isInShoppingList ? "Already in Shopping List" : "Add to Shopping List"}
          </ListItemText>
        </MenuItem>
      </Menu>
    </>
  );
};

export default RecipeCard; 