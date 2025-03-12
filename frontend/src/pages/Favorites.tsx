import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardMedia,
  CardActionArea,
  Box,
  Chip,
  IconButton,
  CircularProgress,
  Alert,
  Button,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  TextField,
  InputAdornment,
  SelectChangeEvent,
} from '@mui/material';
import {
  Favorite as FavoriteIcon,
  FavoriteBorder as FavoriteBorderIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  Clear as ClearIcon,
  Sort as SortIcon,
} from '@mui/icons-material';
import { useRecipes } from '../context/RecipeContext';
import { Recipe } from '../context/RecipeContext';
import { useUser } from '../context/UserContext';
import RecipeCard from '../components/RecipeCard';
import { styled } from '@mui/material/styles';

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

const Favorites: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useUser();
  const { favorites, isLoading, error, toggleFavorite, loadFavorites } = useRecipes();
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<string>('added_at');
  const [sortDirection, setSortDirection] = useState('desc');
  const [filteredFavorites, setFilteredFavorites] = useState(favorites);

  useEffect(() => {
    if (user) {
      loadFavorites();
    }
  }, [user, loadFavorites]);

  useEffect(() => {
    // Filter favorites based on search term
    const filtered = favorites.filter((recipe) =>
      recipe.title.toLowerCase().includes(searchTerm.toLowerCase())
    );

    // Sort favorites
    const sorted = [...filtered].sort((a, b) => {
      if (sortBy === 'title') {
        return sortDirection === 'asc'
          ? a.title.localeCompare(b.title)
          : b.title.localeCompare(a.title);
      } else if (sortBy === 'readyInMinutes') {
        const aTime = a.readyInMinutes || 0;
        const bTime = b.readyInMinutes || 0;
        return sortDirection === 'asc' ? aTime - bTime : bTime - aTime;
      } else {
        // Default sort by added_at
        const aDate = new Date(a.created_at || 0).getTime();
        const bDate = new Date(b.created_at || 0).getTime();
        return sortDirection === 'asc' ? aDate - bDate : bDate - aDate;
      }
    });

    setFilteredFavorites(sorted);
  }, [favorites, searchTerm, sortBy, sortDirection]);

  const handleRecipeClick = (recipeId: number | string) => {
    // Find the recipe in favorites
    const recipe = favorites.find(r => r.id === recipeId);
    if (recipe) {
      navigate(`/recipe/${recipeId}`, {
        state: {
          recipe: recipe
        }
      });
    }
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  };

  const handleClearSearch = () => {
    setSearchTerm('');
  };

  const handleSortChange = (event: SelectChangeEvent) => {
    setSortBy(event.target.value);
  };

  const handleSortDirectionChange = () => {
    setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
  };

  const handleRemoveFavorite = (recipe: Recipe, event: React.MouseEvent) => {
    event.stopPropagation();
    toggleFavorite(recipe);
  };

  if (!user) {
    return (
      <Container maxWidth="md">
        <Paper sx={{ p: 4, textAlign: 'center', my: 4 }}>
          <Typography variant="h5" gutterBottom>
            Please Log In
          </Typography>
          <Typography variant="body1" paragraph>
            You need to be logged in to view your favorites.
          </Typography>
          <Button
            variant="contained"
            color="primary"
            onClick={() => navigate('/')}
          >
            Go to Home
          </Button>
        </Paper>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" component="h1" gutterBottom>
        My Favorite Recipes
      </Typography>

      {/* Search and Sort Controls */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Search favorites"
              value={searchTerm}
              onChange={handleSearchChange}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
                endAdornment: searchTerm && (
                  <InputAdornment position="end">
                    <IconButton onClick={handleClearSearch} edge="end">
                      <ClearIcon />
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <FormControl fullWidth>
                <InputLabel>Sort By</InputLabel>
                <Select
                  value={sortBy}
                  label="Sort By"
                  onChange={handleSortChange}
                >
                  <MenuItem value="added_at">Date Added</MenuItem>
                  <MenuItem value="title">Title</MenuItem>
                  <MenuItem value="readyInMinutes">Cooking Time</MenuItem>
                </Select>
              </FormControl>
              <IconButton onClick={handleSortDirectionChange}>
                <SortIcon
                  sx={{
                    transform: sortDirection === 'desc' ? 'rotate(0deg)' : 'rotate(180deg)',
                  }}
                />
              </IconButton>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Results */}
      {isLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error" sx={{ my: 2 }}>
          {error}
        </Alert>
      ) : filteredFavorites.length > 0 ? (
        <Grid container spacing={3}>
          {filteredFavorites.map((recipe) => (
            <Grid item key={recipe.id} xs={12} sm={6} md={4}>
              <RecipeCard 
                recipe={recipe} 
                user={user}
                toggleFavorite={toggleFavorite}
                isFavoritesPage={true}
              />
            </Grid>
          ))}
        </Grid>
      ) : (
        <Paper sx={{ p: 4, textAlign: 'center', my: 4 }}>
          <Typography variant="h6" gutterBottom>
            No favorites yet
          </Typography>
          <Typography variant="body1" paragraph>
            Start exploring recipes and save your favorites!
          </Typography>
          <Button
            variant="contained"
            color="primary"
            onClick={() => navigate('/search')}
          >
            Find Recipes
          </Button>
        </Paper>
      )}
    </Container>
  );
};

export default Favorites; 