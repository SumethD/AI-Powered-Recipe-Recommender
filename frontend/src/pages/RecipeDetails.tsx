import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Grid,
  Paper,
  Box,
  Chip,
  Divider,
  Button,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Card,
  CardContent,
  IconButton,
  Tab,
  Tabs,
  TextField,
  Rating,
} from '@mui/material';
import {
  Timer as TimerIcon,
  Restaurant as RestaurantIcon,
  Favorite as FavoriteIcon,
  FavoriteBorder as FavoriteBorderIcon,
  ArrowBack as ArrowBackIcon,
  LocalDining as LocalDiningIcon,
  Chat as ChatIcon,
  Send as SendIcon,
} from '@mui/icons-material';
import { useRecipes } from '../context/RecipeContext';
import { useUser } from '../context/UserContext';
import { useChat } from '../context/ChatContext';
import DOMPurify from 'dompurify';
import { RecipeParams } from '../types';

const RecipeDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { selectedRecipe, isLoading, error, getRecipeDetails, toggleFavorite } = useRecipes();
  const { user } = useUser();
  const { sendMessage, messages, isLoading: isChatLoading } = useChat();
  const [activeTab, setActiveTab] = useState(0);
  const [modificationQuery, setModificationQuery] = useState('');
  const [isFavorite, setIsFavorite] = useState<boolean>(false);

  useEffect(() => {
    if (id) {
      try {
        const recipeId = parseInt(id, 10);
        if (!isNaN(recipeId)) {
          getRecipeDetails(recipeId);
        } else {
          console.error("Invalid recipe ID:", id);
        }
      } catch (error) {
        console.error("Error parsing recipe ID:", error);
      }
    }
  }, [id, getRecipeDetails]);

  useEffect(() => {
    if (selectedRecipe && user) {
      setIsFavorite(selectedRecipe.isFavorite || false);
    }
  }, [selectedRecipe, user]);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleSendModification = async () => {
    if (!selectedRecipe || !modificationQuery.trim()) return;

    const context = `Recipe: ${selectedRecipe.title}\nIngredients: ${selectedRecipe.extendedIngredients?.map(ing => ing.original).join(', ')}\nInstructions: ${selectedRecipe.instructions}`;
    
    await sendMessage(modificationQuery, context);
    setModificationQuery('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendModification();
    }
  };

  const handleToggleFavorite = async () => {
    if (selectedRecipe) {
      await toggleFavorite(selectedRecipe);
      setIsFavorite(!isFavorite);
    }
  };

  // Handle back button navigation
  const handleBackClick = () => {
    navigate(-1);
  };

  if (isLoading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 8 }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg">
        <Alert severity="error" sx={{ my: 4 }}>
          {error}
        </Alert>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={handleBackClick}
          sx={{ mt: 2 }}
        >
          Go Back
        </Button>
      </Container>
    );
  }

  if (!selectedRecipe) {
    return (
      <Container maxWidth="lg">
        <Alert severity="info" sx={{ my: 4 }}>
          Recipe not found.
        </Alert>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={handleBackClick}
          sx={{ mt: 2 }}
        >
          Go Back
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Button
        startIcon={<ArrowBackIcon />}
        onClick={handleBackClick}
        sx={{ mb: 2 }}
      >
        Back to Search
      </Button>

      {/* Recipe Header */}
      <Paper
        elevation={3}
        sx={{
          p: 3,
          mb: 4,
          borderRadius: 2,
          backgroundImage: `linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.7)), url(${selectedRecipe.image})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          color: 'white',
          position: 'relative',
        }}
      >
        <Box sx={{ position: 'relative', zIndex: 1 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={8}>
              <Typography variant="h4" component="h1" gutterBottom>
                {selectedRecipe.title}
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                {selectedRecipe.dishTypes?.map((type) => (
                  <Chip
                    key={type}
                    label={type}
                    size="small"
                    sx={{ bgcolor: 'rgba(255, 255, 255, 0.2)', color: 'white' }}
                  />
                ))}
              </Box>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
                {selectedRecipe.readyInMinutes && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <TimerIcon fontSize="small" />
                    <Typography variant="body2">
                      {selectedRecipe.readyInMinutes} minutes
                    </Typography>
                  </Box>
                )}
                {selectedRecipe.servings && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <RestaurantIcon fontSize="small" />
                    <Typography variant="body2">
                      {selectedRecipe.servings} servings
                    </Typography>
                  </Box>
                )}
              </Box>
            </Grid>
            <Grid item xs={12} md={4} sx={{ textAlign: 'right' }}>
              {user && (
                <IconButton
                  onClick={handleToggleFavorite}
                  sx={{
                    bgcolor: 'rgba(255, 255, 255, 0.2)',
                    '&:hover': {
                      bgcolor: 'rgba(255, 255, 255, 0.3)',
                    },
                    p: 1.5,
                  }}
                >
                  {isFavorite ? (
                    <FavoriteIcon fontSize="large" sx={{ color: '#ff6d75' }} />
                  ) : (
                    <FavoriteBorderIcon fontSize="large" sx={{ color: 'white' }} />
                  )}
                </IconButton>
              )}
            </Grid>
          </Grid>
        </Box>
      </Paper>

      {/* Recipe Content Tabs */}
      <Paper elevation={2} sx={{ mb: 4 }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
          variant="fullWidth"
        >
          <Tab label="Recipe" icon={<LocalDiningIcon />} />
          <Tab label="Modify Recipe" icon={<ChatIcon />} />
        </Tabs>

        {/* Recipe Tab */}
        {activeTab === 0 && (
          <Box sx={{ p: 3 }}>
            <Grid container spacing={4}>
              {/* Left Column - Ingredients */}
              <Grid item xs={12} md={4}>
                <Typography variant="h6" gutterBottom>
                  Ingredients
                </Typography>
                <Divider sx={{ mb: 2 }} />
                <List>
                  {selectedRecipe.extendedIngredients?.map((ingredient) => (
                    <ListItem key={ingredient.id} disablePadding sx={{ mb: 1 }}>
                      <ListItemIcon sx={{ minWidth: 32 }}>•</ListItemIcon>
                      <ListItemText primary={ingredient.original} />
                    </ListItem>
                  ))}
                </List>

                {/* Nutrition Info */}
                {selectedRecipe.nutrition && (
                  <Box sx={{ mt: 4 }}>
                    <Typography variant="h6" gutterBottom>
                      Nutrition
                    </Typography>
                    <Divider sx={{ mb: 2 }} />
                    <Grid container spacing={1}>
                      {selectedRecipe.nutrition.nutrients?.slice(0, 6).map((nutrient) => (
                        <Grid item xs={6} key={nutrient.name}>
                          <Card variant="outlined" sx={{ mb: 1 }}>
                            <CardContent sx={{ p: 1, '&:last-child': { pb: 1 } }}>
                              <Typography variant="body2" color="text.secondary">
                                {nutrient.name}
                              </Typography>
                              <Typography variant="body1">
                                {nutrient.amount} {nutrient.unit}
                              </Typography>
                            </CardContent>
                          </Card>
                        </Grid>
                      ))}
                    </Grid>
                  </Box>
                )}

                {/* Diets & Allergies */}
                {((selectedRecipe?.diets && selectedRecipe.diets.length > 0) || selectedRecipe?.dairyFree || selectedRecipe?.glutenFree) && (
                  <Box sx={{ mt: 4 }}>
                    <Typography variant="h6" gutterBottom>
                      Dietary Information
                    </Typography>
                    <Divider sx={{ mb: 2 }} />
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {selectedRecipe?.diets?.map((diet) => (
                        <Chip key={diet} label={diet} color="primary" size="small" />
                      ))}
                      {selectedRecipe?.dairyFree && (
                        <Chip label="Dairy Free" color="success" size="small" />
                      )}
                      {selectedRecipe?.glutenFree && (
                        <Chip label="Gluten Free" color="success" size="small" />
                      )}
                    </Box>
                  </Box>
                )}
              </Grid>

              {/* Right Column - Instructions & Summary */}
              <Grid item xs={12} md={8}>
                {/* Summary */}
                {selectedRecipe.summary && (
                  <Box sx={{ mb: 4 }}>
                    <Typography variant="h6" gutterBottom>
                      Summary
                    </Typography>
                    <Divider sx={{ mb: 2 }} />
                    <Typography
                      variant="body1"
                      dangerouslySetInnerHTML={{
                        __html: DOMPurify.sanitize(selectedRecipe.summary),
                      }}
                    />
                  </Box>
                )}

                {/* Instructions */}
                {selectedRecipe.instructions && (
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      Instructions
                    </Typography>
                    <Divider sx={{ mb: 2 }} />
                    <Typography
                      variant="body1"
                      component="div"
                      dangerouslySetInnerHTML={{
                        __html: DOMPurify.sanitize(selectedRecipe.instructions),
                      }}
                    />
                  </Box>
                )}

                {/* Source */}
                {selectedRecipe.sourceUrl && (
                  <Box sx={{ mt: 4 }}>
                    <Typography variant="body2" color="text.secondary">
                      Source:{' '}
                      <a
                        href={selectedRecipe.sourceUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        {selectedRecipe.sourceName || 'Original Recipe'}
                      </a>
                    </Typography>
                  </Box>
                )}
              </Grid>
            </Grid>
          </Box>
        )}

        {/* Modify Recipe Tab */}
        {activeTab === 1 && (
          <Box sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Ask AI to Modify This Recipe
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Ask how to make this recipe healthier, vegetarian, vegan, gluten-free, or any other modification you'd like.
            </Typography>

            <Box sx={{ mb: 3 }}>
              <TextField
                fullWidth
                label="How would you like to modify this recipe?"
                placeholder="E.g., How can I make this recipe healthier? or How can I make this vegetarian?"
                multiline
                rows={2}
                value={modificationQuery}
                onChange={(e) => setModificationQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                InputProps={{
                  endAdornment: (
                    <IconButton
                      onClick={handleSendModification}
                      disabled={!modificationQuery.trim() || isChatLoading}
                      edge="end"
                    >
                      <SendIcon />
                    </IconButton>
                  ),
                }}
              />
            </Box>

            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Suggested Questions:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                <Chip
                  label="Make it healthier"
                  onClick={() => setModificationQuery("How can I make this recipe healthier?")}
                  clickable
                />
                <Chip
                  label="Make it vegetarian"
                  onClick={() => setModificationQuery("How can I make this recipe vegetarian?")}
                  clickable
                />
                <Chip
                  label="Make it low-carb"
                  onClick={() => setModificationQuery("How can I make this recipe low-carb?")}
                  clickable
                />
                <Chip
                  label="Enhance flavor"
                  onClick={() => setModificationQuery("How can I enhance the flavor of this recipe?")}
                  clickable
                />
              </Box>
            </Box>

            <Divider sx={{ my: 3 }} />

            {/* Chat Messages */}
            <Box sx={{ mt: 3 }}>
              {messages.length > 0 ? (
                messages.map((message) => (
                  <Box
                    key={message.id}
                    sx={{
                      display: 'flex',
                      justifyContent: message.isUser ? 'flex-end' : 'flex-start',
                      mb: 2,
                    }}
                  >
                    <Paper
                      elevation={1}
                      sx={{
                        p: 2,
                        maxWidth: '80%',
                        bgcolor: message.isUser ? 'primary.light' : 'grey.100',
                        color: message.isUser ? 'white' : 'text.primary',
                        borderRadius: 2,
                      }}
                    >
                      <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                        {message.content}
                      </Typography>
                    </Paper>
                  </Box>
                ))
              ) : (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body2" color="text.secondary">
                    Ask a question about modifying this recipe to get started.
                  </Typography>
                </Box>
              )}

              {isChatLoading && (
                <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
                  <CircularProgress size={24} />
                </Box>
              )}
            </Box>
          </Box>
        )}
      </Paper>
    </Container>
  );
};

export default RecipeDetails; 