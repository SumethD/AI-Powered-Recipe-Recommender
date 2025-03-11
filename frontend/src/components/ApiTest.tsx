import React, { useState, useEffect } from 'react';
import { Box, Button, Typography, CircularProgress, Paper, Container } from '@mui/material';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const ApiTest: React.FC = () => {
  const [testResult, setTestResult] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const testApi = async (endpoint: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_BASE_URL}${endpoint}`);
      console.log('API Response:', response.data);
      setTestResult(response.data);
    } catch (err) {
      console.error('API Error:', err);
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Paper sx={{ p: 3, my: 3 }}>
        <Typography variant="h4" gutterBottom>
          API Connection Test
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
          <Button 
            variant="contained" 
            onClick={() => testApi('/test-edamam')}
            disabled={loading}
          >
            Test Edamam Connection
          </Button>
          
          <Button 
            variant="contained" 
            onClick={() => testApi('/recipes/random?limit=1')}
            disabled={loading}
          >
            Get Random Recipe
          </Button>
          
          <Button 
            variant="contained" 
            onClick={() => testApi('/recipes/search?query=pasta&limit=1')}
            disabled={loading}
          >
            Search Pasta Recipe
          </Button>
        </Box>
        
        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
            <CircularProgress />
          </Box>
        )}
        
        {error && (
          <Typography color="error" sx={{ my: 2 }}>
            Error: {error}
          </Typography>
        )}
        
        {testResult && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Response:
            </Typography>
            <Paper 
              variant="outlined" 
              sx={{ 
                p: 2, 
                maxHeight: '400px', 
                overflow: 'auto',
                bgcolor: '#f5f5f5',
                fontFamily: 'monospace',
                fontSize: '0.875rem'
              }}
            >
              <pre>{JSON.stringify(testResult, null, 2)}</pre>
            </Paper>
          </Box>
        )}
      </Paper>
    </Container>
  );
};

export default ApiTest; 