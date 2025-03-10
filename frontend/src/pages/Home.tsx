import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Button,
  Box,
  Grid,
  Paper,
  Card,
  CardContent,
  CardMedia,
  CardActionArea,
} from '@mui/material';
import {
  Search as SearchIcon,
  Chat as ChatIcon,
} from '@mui/icons-material';

const Home: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Container maxWidth="lg">
      {/* Hero Section */}
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          textAlign: 'center',
          py: 8,
        }}
      >
        <Typography variant="h2" component="h1" gutterBottom>
          AI-Powered Recipe Recommender
        </Typography>
        <Typography variant="h5" color="text.secondary" paragraph>
          Find, modify, and create recipes based on your preferences and available ingredients.
        </Typography>
        <Box
          sx={{
            display: 'flex',
            flexDirection: { xs: 'column', md: 'row' },
            gap: 2,
            mt: 4,
          }}
        >
          <Button
            variant="contained"
            size="large"
            startIcon={<SearchIcon />}
            onClick={() => navigate('/search')}
          >
            Search Recipes
          </Button>
          <Button
            variant="outlined"
            size="large"
            startIcon={<ChatIcon />}
            onClick={() => navigate('/chat')}
          >
            Ask AI Assistant
          </Button>
        </Box>
      </Box>

      {/* Features Section */}
      <Box sx={{ mb: 6 }}>
        <Typography variant="h4" gutterBottom>
          Features
        </Typography>
        <Grid container spacing={4}>
          <Grid item xs={12} md={4}>
            <Paper
              elevation={2}
              sx={{
                p: 3,
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                textAlign: 'center',
              }}
            >
              <Typography variant="h6" gutterBottom>
                Search by Ingredients
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Find recipes based on ingredients you have on hand.
              </Typography>
              <Button
                variant="text"
                color="primary"
                onClick={() => navigate('/search')}
                sx={{ mt: 'auto' }}
              >
                Try It
              </Button>
            </Paper>
          </Grid>
          <Grid item xs={12} md={4}>
            <Paper
              elevation={2}
              sx={{
                p: 3,
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                textAlign: 'center',
              }}
            >
              <Typography variant="h6" gutterBottom>
                AI Recipe Assistant
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Get personalized recipe recommendations and cooking advice.
              </Typography>
              <Button
                variant="text"
                color="primary"
                onClick={() => navigate('/chat')}
                sx={{ mt: 'auto' }}
              >
                Try It
              </Button>
            </Paper>
          </Grid>
          <Grid item xs={12} md={4}>
            <Paper
              elevation={2}
              sx={{
                p: 3,
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                textAlign: 'center',
              }}
            >
              <Typography variant="h6" gutterBottom>
                Save Favorites
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Save your favorite recipes for easy access later.
              </Typography>
              <Button
                variant="text"
                color="primary"
                onClick={() => navigate('/favorites')}
                sx={{ mt: 'auto' }}
              >
                Try It
              </Button>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default Home; 