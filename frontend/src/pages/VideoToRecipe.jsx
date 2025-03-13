import React, { useState } from 'react';
import axios from 'axios';
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  CircularProgress,
  Alert,
  Grid,
  Container,
  Card,
  CardMedia,
  IconButton,
  Tooltip,
  useTheme
} from '@mui/material';
import { ContentCopy as ContentCopyIcon, Bookmark as BookmarkIcon } from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import { useUser } from '../context/UserContext';

function VideoToRecipe() {
  const theme = useTheme();
  const { user } = useUser();
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [recipe, setRecipe] = useState(null);
  const [videoId, setVideoId] = useState(null);
  const [savedToFavorites, setSavedToFavorites] = useState(false);
  
  // Form validation
  const [urlError, setUrlError] = useState(null);
  
  // Handle URL change
  const handleUrlChange = (e) => {
    setYoutubeUrl(e.target.value);
    setUrlError(null);
    setError(null);
  };
  
  // Validate YouTube URL
  const validateUrl = (url) => {
    // Basic validation for YouTube URLs
    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$/;
    if (!youtubeRegex.test(url)) {
      setUrlError('Please enter a valid YouTube URL');
      return false;
    }
    return true;
  };
  
  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Reset states
    setError(null);
    setRecipe(null);
    setVideoId(null);
    setSavedToFavorites(false);
    
    // Validate input
    if (!youtubeUrl.trim()) {
      setUrlError('Please enter a YouTube URL');
      return;
    }
    
    if (!validateUrl(youtubeUrl)) {
      return;
    }
    
    // Start loading
    setLoading(true);
    
    try {
      console.log('Sending request to backend with URL:', youtubeUrl);
      
      // Call the API to convert video to recipe
      const response = await axios.post('/api/videos/to-recipe', {
        youtube_url: youtubeUrl
      }, {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });
      
      console.log('Response from backend:', response);
      
      if (response.data.success) {
        setRecipe(response.data.recipe);
        setVideoId(response.data.video_id);
      } else {
        setError(response.data.error || 'Failed to extract recipe from video');
      }
    } catch (err) {
      console.error('Error processing video:', err);
      console.error('Full error object:', JSON.stringify(err, null, 2));
      
      // More detailed error handling
      if (err.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        console.error('Error response data:', err.response.data);
        console.error('Error response status:', err.response.status);
        console.error('Error response headers:', err.response.headers);
        setError(`Server error (${err.response.status}): ${err.response.data.error || err.response.data}`);
      } else if (err.request) {
        // The request was made but no response was received
        console.error('Error request:', err.request);
        setError('No response received from server. The server might be down or unreachable.');
      } else {
        // Something happened in setting up the request that triggered an Error
        setError(`Error: ${err.message}`);
      }
    } finally {
      setLoading(false);
    }
  };
  
  // Copy recipe to clipboard
  const copyToClipboard = () => {
    if (recipe) {
      navigator.clipboard.writeText(recipe)
        .then(() => {
          alert('Recipe copied to clipboard!');
        })
        .catch(err => {
          console.error('Failed to copy recipe:', err);
        });
    }
  };
  
  // Save recipe to favorites
  const saveToFavorites = async () => {
    if (!user) {
      setError('Please log in to save recipes to favorites');
      return;
    }
    
    if (recipe && videoId) {
      try {
        // Extract title from the recipe markdown (assuming it starts with # Title)
        const titleMatch = recipe.match(/^# (.+)$/m);
        const title = titleMatch ? titleMatch[1] : 'YouTube Recipe';
        
        // Create a simplified recipe object
        const recipeData = {
          id: `youtube_${videoId}`,
          title: title,
          image: `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`,
          sourceUrl: `https://www.youtube.com/watch?v=${videoId}`,
          instructions: recipe,
          summary: recipe.split('\n').slice(0, 3).join(' ').substring(0, 200) + '...',
          extendedIngredients: [],
          readyInMinutes: 0,
          servings: 0,
          veryPopular: false,
          weightWatcherSmartPoints: 0,
          cuisines: [],
          dishTypes: [],
          diets: []
        };
        
        // Save to favorites
        await axios.post('/api/recipes/favorites', {
          user_id: user.id,
          recipe: recipeData
        });
        
        setSavedToFavorites(true);
      } catch (err) {
        console.error('Error saving to favorites:', err);
        setError(err.response?.data?.error || 'Failed to save recipe to favorites');
      }
    }
  };
  
  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center" sx={{ fontWeight: 700 }}>
          Video to Recipe Converter
        </Typography>
        
        <Typography variant="subtitle1" color="text.secondary" align="center" sx={{ mb: 4 }}>
          Convert any cooking YouTube video into a detailed, structured recipe
        </Typography>
        
        <Paper 
          elevation={0} 
          sx={{ 
            p: 4, 
            mb: 4, 
            borderRadius: 2,
            border: `1px solid ${theme.palette.divider}`,
            backgroundColor: theme.palette.background.paper
          }}
        >
          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="YouTube Video URL"
              variant="outlined"
              value={youtubeUrl}
              onChange={handleUrlChange}
              error={!!urlError}
              helperText={urlError}
              placeholder="https://www.youtube.com/watch?v=..."
              sx={{ mb: 3 }}
            />
            
            <Button
              type="submit"
              variant="contained"
              color="primary"
              size="large"
              disabled={loading}
              sx={{ 
                minWidth: 150,
                py: 1.5,
                px: 4, 
                borderRadius: '8px',
                fontWeight: 600
              }}
            >
              {loading ? <CircularProgress size={24} color="inherit" /> : 'Convert to Recipe'}
            </Button>
          </form>
        </Paper>
        
        {error && (
          <Alert severity="error" sx={{ mb: 4 }}>
            {error}
          </Alert>
        )}
        
        {recipe && videoId && (
          <Grid container spacing={4}>
            <Grid item xs={12} md={5}>
              <Card sx={{ mb: 3, borderRadius: 2, overflow: 'hidden' }}>
                <CardMedia
                  component="img"
                  image={`https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`}
                  alt="Video thumbnail"
                  height={300}
                />
              </Card>
              
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Button
                  variant="outlined"
                  startIcon={<ContentCopyIcon />}
                  onClick={copyToClipboard}
                  sx={{ borderRadius: '8px' }}
                >
                  Copy Recipe
                </Button>
                
                <Tooltip title={savedToFavorites ? "Saved to favorites" : "Save to favorites"}>
                  <IconButton 
                    color={savedToFavorites ? "primary" : "default"} 
                    onClick={saveToFavorites}
                    disabled={savedToFavorites || !user}
                  >
                    <BookmarkIcon />
                  </IconButton>
                </Tooltip>
              </Box>
              
              <Box sx={{ mt: 4 }}>
                <Typography variant="body2" color="text.secondary">
                  Source: <a href={`https://www.youtube.com/watch?v=${videoId}`} target="_blank" rel="noopener noreferrer">
                    YouTube Video
                  </a>
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={7}>
              <Paper 
                elevation={0} 
                sx={{ 
                  p: 4, 
                  borderRadius: 2,
                  border: `1px solid ${theme.palette.divider}`,
                  backgroundColor: theme.palette.background.paper,
                  minHeight: '500px',
                  overflowY: 'auto',
                  maxHeight: '800px'
                }}
              >
                {recipe && <ReactMarkdown>{recipe}</ReactMarkdown>}
              </Paper>
            </Grid>
          </Grid>
        )}
        
        {!recipe && !loading && !error && (
          <Box sx={{ mt: 6, p: 4, bgcolor: 'rgba(0,0,0,0.02)', borderRadius: 2 }}>
            <Typography variant="h6" gutterBottom>
              How it works:
            </Typography>
            
            <Grid container spacing={3} sx={{ mt: 2 }}>
              <Grid item xs={12} md={4}>
                <Box sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h6" color="primary" gutterBottom>
                    1. Paste YouTube URL
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Copy and paste the URL of any cooking video from YouTube
                  </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={12} md={4}>
                <Box sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h6" color="primary" gutterBottom>
                    2. AI Transcription
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Our AI automatically transcribes the video and extracts the recipe information
                  </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={12} md={4}>
                <Box sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h6" color="primary" gutterBottom>
                    3. Get Structured Recipe
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Receive a detailed, formatted recipe you can save, print, or share
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Box>
        )}
      </Box>
    </Container>
  );
}

export default VideoToRecipe; 