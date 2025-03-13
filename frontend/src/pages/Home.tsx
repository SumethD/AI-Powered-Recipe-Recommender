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
  useTheme,
} from '@mui/material';
import {
  Search as SearchIcon,
  Chat as ChatIcon,
  Favorite as FavoriteIcon,
  Kitchen as KitchenIcon,
  Assistant as AssistantIcon,
  BookmarkAdd as BookmarkIcon,
  YouTube as YouTubeIcon,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';

// Styled components for enhanced feature cards
const FeatureCard = styled(Paper)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  textAlign: 'center',
  padding: theme.spacing(4),
  borderRadius: 16,
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  position: 'relative',
  overflow: 'hidden',
  boxShadow: '0 6px 20px rgba(0,0,0,0.08)',
  '&:hover': {
    transform: 'translateY(-8px)',
    boxShadow: '0 12px 28px rgba(0,0,0,0.15)',
    '& .feature-icon': {
      transform: 'scale(1.1) translateY(-5px)',
      color: theme.palette.primary.main,
    },
    '& .feature-button': {
      backgroundColor: theme.palette.primary.main,
      color: '#fff',
    },
    '&::after': {
      opacity: 1,
    },
  },
  '&::after': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '5px',
    background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
    opacity: 0,
    transition: 'opacity 0.3s ease',
  },
}));

const IconWrapper = styled(Box)(({ theme }) => ({
  width: 70,
  height: 70,
  borderRadius: '50%',
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  backgroundColor: theme.palette.grey[100],
  marginBottom: theme.spacing(2),
  transition: 'all 0.3s ease',
}));

const FeatureButton = styled(Button)(({ theme }) => ({
  marginTop: 'auto',
  borderRadius: 30,
  padding: '8px 24px',
  transition: 'all 0.3s ease',
  fontWeight: 600,
  '&:hover': {
    transform: 'scale(1.05)',
  },
}));

const Home: React.FC = () => {
  const navigate = useNavigate();
  const theme = useTheme();

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
          Savorly
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
            sx={{
              background: `linear-gradient(45deg, ${theme.palette.primary.main} 30%, ${theme.palette.primary.light} 90%)`,
              boxShadow: '0 8px 16px rgba(103, 58, 183, 0.3)',
              '&:hover': {
                boxShadow: '0 12px 20px rgba(103, 58, 183, 0.4)',
                transform: 'translateY(-2px)',
              },
              transition: 'all 0.3s ease',
            }}
          >
            Search Recipes
          </Button>
          <Button
            variant="outlined"
            size="large"
            startIcon={<ChatIcon />}
            onClick={() => navigate('/chat')}
            sx={{
              borderWidth: 2,
              '&:hover': {
                borderWidth: 2,
                backgroundColor: 'rgba(103, 58, 183, 0.05)',
                transform: 'translateY(-2px)',
              },
              transition: 'all 0.3s ease',
            }}
          >
            Ask AI Assistant
          </Button>
        </Box>
      </Box>

      {/* Features Section */}
      <Box sx={{ mb: 8 }}>
        <Typography 
          variant="h4" 
          gutterBottom 
          sx={{ 
            mb: 4, 
            textAlign: 'center',
            position: 'relative',
            '&::after': {
              content: '""',
              display: 'block',
              width: '60px',
              height: '4px',
              background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
              margin: '16px auto 0',
              borderRadius: '2px',
            }
          }}
        >
          Features
        </Typography>
        <Grid container spacing={4}>
          <Grid item xs={12} md={4}>
            <FeatureCard>
              <IconWrapper className="feature-icon">
                <KitchenIcon sx={{ fontSize: 36, color: theme.palette.text.secondary }} />
              </IconWrapper>
              <Typography variant="h6" gutterBottom fontWeight="bold">
                Search by Ingredients
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                Find recipes based on ingredients you have on hand.
              </Typography>
              <FeatureButton
                variant="outlined"
                color="primary"
                onClick={() => navigate('/search')}
                className="feature-button"
              >
                Try It
              </FeatureButton>
            </FeatureCard>
          </Grid>
          <Grid item xs={12} md={4}>
            <FeatureCard>
              <IconWrapper className="feature-icon">
                <AssistantIcon sx={{ fontSize: 36, color: theme.palette.text.secondary }} />
              </IconWrapper>
              <Typography variant="h6" gutterBottom fontWeight="bold">
                AI Recipe Assistant
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                Get personalized recipe recommendations and cooking advice.
              </Typography>
              <FeatureButton
                variant="outlined"
                color="primary"
                onClick={() => navigate('/chat')}
                className="feature-button"
              >
                Try It
              </FeatureButton>
            </FeatureCard>
          </Grid>
          <Grid item xs={12} md={4}>
            <FeatureCard>
              <IconWrapper className="feature-icon">
                <YouTubeIcon sx={{ fontSize: 36, color: theme.palette.text.secondary }} />
              </IconWrapper>
              <Typography variant="h6" gutterBottom fontWeight="bold">
                Video to Recipe
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                Convert cooking videos into detailed, structured recipes.
              </Typography>
              <FeatureButton
                variant="outlined"
                color="primary"
                onClick={() => navigate('/video-to-recipe')}
                className="feature-button"
              >
                Try It
              </FeatureButton>
            </FeatureCard>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default Home; 