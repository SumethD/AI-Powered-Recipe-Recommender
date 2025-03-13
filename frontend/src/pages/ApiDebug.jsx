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
  Container,
  Stack,
  Divider
} from '@mui/material';

function ApiDebug() {
  const [youtubeUrl, setYoutubeUrl] = useState('https://www.youtube.com/watch?v=dQw4w9WgXcQ');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [response, setResponse] = useState(null);
  
  // Handle URL change
  const handleUrlChange = (e) => {
    setYoutubeUrl(e.target.value);
    setError(null);
  };
  
  // Test backend health
  const testBackendHealth = async () => {
    setLoading(true);
    setError(null);
    setResponse(null);
    
    try {
      console.log('Testing backend health at http://localhost:5000/api/health');
      
      const response = await axios.get('http://localhost:5000/api/health', {
        headers: {
          'Accept': 'application/json'
        }
      });
      
      console.log('Backend health response:', response);
      setResponse(JSON.stringify(response.data, null, 2));
    } catch (err) {
      console.error('Health check error:', err);
      setError(`Health check error: ${err.message}`);
      
      if (err.response) {
        console.error('Error response data:', err.response.data);
        console.error('Error status:', err.response.status);
      }
    } finally {
      setLoading(false);
    }
  };
  
  // Test direct connection with full URL
  const testDirectConnection = async () => {
    setLoading(true);
    setError(null);
    setResponse(null);
    
    try {
      console.log('Testing direct connection to http://localhost:5000/api/videos/to-recipe');
      
      const response = await axios.post('http://localhost:5000/api/videos/to-recipe', {
        youtube_url: youtubeUrl
      }, {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });
      
      console.log('Direct connection response:', response);
      setResponse(JSON.stringify(response.data, null, 2));
    } catch (err) {
      console.error('Direct connection error:', err);
      setError(`Direct connection error: ${err.message}`);
      
      if (err.response) {
        console.error('Error response data:', err.response.data);
        console.error('Error status:', err.response.status);
      }
    } finally {
      setLoading(false);
    }
  };
  
  // Test proxy connection
  const testProxyConnection = async () => {
    setLoading(true);
    setError(null);
    setResponse(null);
    
    try {
      console.log('Testing proxy connection to /api/videos/to-recipe');
      
      const response = await axios.post('/api/videos/to-recipe', {
        youtube_url: youtubeUrl
      }, {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });
      
      console.log('Proxy connection response:', response);
      setResponse(JSON.stringify(response.data, null, 2));
    } catch (err) {
      console.error('Proxy connection error:', err);
      setError(`Proxy connection error: ${err.message}`);
      
      if (err.response) {
        console.error('Error response data:', err.response.data);
        console.error('Error status:', err.response.status);
      }
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <Container maxWidth="md">
      <Box sx={{ py: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          API Debug Tool
        </Typography>
        
        <Paper sx={{ p: 4, mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            1. Check Backend Health
          </Typography>
          
          <Button
            fullWidth
            variant="contained"
            color="success"
            onClick={testBackendHealth}
            disabled={loading}
            sx={{ mb: 4 }}
          >
            Test Backend Health
          </Button>
          
          <Divider sx={{ my: 3 }} />
          
          <Typography variant="h6" gutterBottom>
            2. Test Video-to-Recipe API
          </Typography>
          
          <TextField
            fullWidth
            label="YouTube URL"
            variant="outlined"
            value={youtubeUrl}
            onChange={handleUrlChange}
            sx={{ mb: 3 }}
          />
          
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mb: 3 }}>
            <Button
              fullWidth
              variant="contained"
              color="primary"
              onClick={testDirectConnection}
              disabled={loading}
            >
              Test Direct Connection
            </Button>
            
            <Button
              fullWidth
              variant="contained"
              color="secondary"
              onClick={testProxyConnection}
              disabled={loading}
            >
              Test Proxy Connection
            </Button>
          </Stack>
          
          {loading && (
            <Box sx={{ display: 'flex', justifyContent: 'center', my: 3 }}>
              <CircularProgress />
            </Box>
          )}
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          {response && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="h6">Response:</Typography>
              <Paper sx={{ p: 2, bgcolor: '#f5f5f5', maxHeight: '400px', overflow: 'auto' }}>
                <pre>{response}</pre>
              </Paper>
            </Box>
          )}
        </Paper>
      </Box>
    </Container>
  );
}

export default ApiDebug; 