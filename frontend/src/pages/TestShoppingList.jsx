import React, { useState, useEffect } from 'react';
import { Box, Typography, Button, CircularProgress, Paper, List } from '@mui/material';

function TestShoppingList() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchShoppingList = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Example recipe data
      const data = {
        recipes: [
          {
            id: 1,
            extendedIngredients: [
              { name: 'olive oil', amount: 2, unit: 'tbsp' },
              { name: 'onion', amount: 1, unit: '' }
            ]
          }
        ]
      };
      
      // Call API
      const response = await fetch('http://localhost:5000/api/shopping-list/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch shopping list');
      }
      
      const result = await response.json();
      setItems(result.shopping_list);
      console.log('API response:', result);
    } catch (err) {
      setError(err.message);
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 4, maxWidth: 800, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom align="center">
        Test Shopping List
      </Typography>
      
      <Button 
        variant="contained" 
        onClick={fetchShoppingList}
        disabled={loading}
        sx={{ mb: 3 }}
      >
        {loading ? 'Loading...' : 'Generate Test List'}
      </Button>
      
      {loading && <CircularProgress sx={{ display: 'block', mx: 'auto', mb: 2 }} />}
      
      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          Error: {error}
        </Typography>
      )}
      
      {items.length > 0 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Shopping List Items
          </Typography>
          
          <List>
            {items.map((item, index) => (
              <Box key={index} sx={{ mb: 2 }}>
                <Typography>
                  <strong>Item {index + 1}:</strong> {item.amount} {item.unit} {item.name}
                </Typography>
                
                <Typography variant="body2" color="text.secondary">
                  <strong>Category:</strong> {item.category}
                </Typography>
                
                <Typography variant="body2" color="text.secondary">
                  <strong>Recipe IDs:</strong> {item.recipeIds.join(', ')}
                </Typography>
                
                <Typography variant="body2" color="text.secondary">
                  <strong>Standardized Display:</strong> {item.standardizedDisplay}
                </Typography>
              </Box>
            ))}
          </List>
        </Paper>
      )}
    </Box>
  );
}

export default TestShoppingList; 