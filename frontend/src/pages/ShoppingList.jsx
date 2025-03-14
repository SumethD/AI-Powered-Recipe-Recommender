import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Button,
  Paper,
  List,
  ListItem,
  ListItemText,
  IconButton,
  TextField,
  Grid,
  Divider,
  Checkbox,
  Card,
  CardContent,
  CardMedia,
  CardActions,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Tooltip,
  CircularProgress,
  Alert,
  Collapse,
  Stack,
  Snackbar,
  useTheme,
  FormControlLabel,
  Switch
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Add as AddIcon,
  ShoppingCart as ShoppingCartIcon,
  Print as PrintIcon,
  Share as ShareIcon,
  ContentCopy as ContentCopyIcon,
  Kitchen as KitchenIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Edit as EditIcon,
  Clear as ClearIcon,
  Download as DownloadIcon,
  Restaurant as RestaurantIcon
} from '@mui/icons-material';
import { useShoppingList } from '../context/ShoppingListContext';

function ShoppingList() {
  const theme = useTheme();
  const navigate = useNavigate();
  const {
    selectedRecipes,
    shoppingList,
    removeRecipeFromList,
    clearShoppingList,
    generateShoppingList,
    toggleItemChecked,
    updateItemAmount,
    removeItemFromList
  } = useShoppingList();
  
  const [editItem, setEditItem] = useState(null);
  const [editAmount, setEditAmount] = useState('');
  const [showMessage, setShowMessage] = useState(false);
  const [message, setMessage] = useState('');
  const [expandedCategory, setExpandedCategory] = useState({});
  const [showConfirmClear, setShowConfirmClear] = useState(false);
  const [showStandardized, setShowStandardized] = useState(true);
  
  // Initialize all categories as expanded
  useEffect(() => {
    if (shoppingList.length > 0) {
      const categories = [...new Set(shoppingList.map(item => item.category))];
      const initialExpanded = {};
      categories.forEach(category => {
        initialExpanded[category] = true;
      });
      setExpandedCategory(initialExpanded);
    }
  }, [shoppingList]);
  
  // Generate shopping list on page load if we have recipes but no list
  useEffect(() => {
    if (selectedRecipes.length > 0 && shoppingList.length === 0) {
      generateShoppingList();
    }
  }, [selectedRecipes, shoppingList, generateShoppingList]);
  
  // Handle toggling category expansion
  const toggleCategory = (category) => {
    setExpandedCategory(prev => ({
      ...prev,
      [category]: !prev[category]
    }));
  };
  
  // Edit an item
  const startEditItem = (item) => {
    setEditItem(item);
    setEditAmount(item.amount.toString());
  };
  
  // Save edited item
  const saveEditItem = () => {
    const amount = parseFloat(editAmount);
    if (!isNaN(amount) && amount > 0) {
      updateItemAmount(editItem.id, amount);
      setEditItem(null);
      setMessage('Item updated');
      setShowMessage(true);
    }
  };
  
  // Cancel editing
  const cancelEdit = () => {
    setEditItem(null);
  };
  
  // Copy shopping list to clipboard
  const copyToClipboard = () => {
    // Group items by category
    const categoryGroups = {};
    shoppingList.forEach(item => {
      if (!categoryGroups[item.category]) {
        categoryGroups[item.category] = [];
      }
      categoryGroups[item.category].push(item);
    });
    
    // Format text
    let text = "SHOPPING LIST\n\n";
    
    Object.keys(categoryGroups).sort().forEach(category => {
      text += `${category.toUpperCase()}\n`;
      categoryGroups[category].forEach(item => {
        const amount = item.amount % 1 === 0 ? item.amount.toString() : item.amount.toFixed(2);
        text += `- ${amount} ${item.unit ? item.unit + ' ' : ''}${item.name}`;
        if (showStandardized && item.standardizedDisplay) {
          text += ` (${item.standardizedDisplay})`;
        }
        text += '\n';
      });
      text += '\n';
    });
    
    navigator.clipboard.writeText(text)
      .then(() => {
        setMessage('Shopping list copied to clipboard');
        setShowMessage(true);
      })
      .catch(err => {
        console.error('Error copying to clipboard:', err);
        setMessage('Failed to copy to clipboard');
        setShowMessage(true);
      });
  };
  
  // Print shopping list
  const printList = () => {
    const printWindow = window.open('', '_blank');
    
    if (!printWindow) {
      setMessage('Please allow pop-ups to print');
      setShowMessage(true);
      return;
    }
    
    // Group items by category
    const categoryGroups = {};
    shoppingList.forEach(item => {
      if (!categoryGroups[item.category]) {
        categoryGroups[item.category] = [];
      }
      categoryGroups[item.category].push(item);
    });
    
    // Create HTML
    let html = `
      <html>
      <head>
        <title>Shopping List</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
          }
          h1 {
            text-align: center;
            margin-bottom: 20px;
          }
          h2 {
            margin-top: 20px;
            border-bottom: 1px solid #ccc;
            padding-bottom: 5px;
          }
          ul {
            list-style-type: none;
            padding-left: 10px;
          }
          li {
            padding: 6px 0;
          }
          .standardized {
            font-size: 0.85em;
            color: #666;
            font-style: italic;
            margin-left: 22px;
          }
          .recipes {
            margin-top: 40px;
            font-size: 14px;
            color: #666;
          }
          @media print {
            .no-print {
              display: none;
            }
            body {
              font-size: 12pt;
            }
          }
        </style>
      </head>
      <body>
        <h1>Shopping List</h1>
        <div class="no-print">
          <button onclick="window.print()">Print</button>
          <button onclick="window.close()">Close</button>
        </div>
    `;
    
    Object.keys(categoryGroups).sort().forEach(category => {
      html += `<h2>${category}</h2>`;
      html += '<ul>';
      categoryGroups[category].forEach(item => {
        const amount = item.amount % 1 === 0 ? item.amount.toString() : item.amount.toFixed(2);
        html += `<li><input type="checkbox"> ${amount} ${item.unit ? item.unit + ' ' : ''}${item.name}`;
        if (showStandardized && item.standardizedDisplay) {
          html += `<div class="standardized">Standardized: ${item.standardizedDisplay}</div>`;
        }
        html += `</li>`;
      });
      html += '</ul>';
    });
    
    // Add recipe names at the bottom
    html += '<div class="recipes">';
    html += '<h3>Recipes:</h3>';
    html += '<ul>';
    selectedRecipes.forEach(recipe => {
      html += `<li>${recipe.title}</li>`;
    });
    html += '</ul>';
    html += '</div>';
    
    html += `
        <script>
          window.onload = function() {
            setTimeout(function() {
              document.querySelector('.no-print').style.display = 'none';
            }, 1000);
          }
        </script>
      </body>
      </html>
    `;
    
    printWindow.document.open();
    printWindow.document.write(html);
    printWindow.document.close();
  };
  
  // Download as text file
  const downloadAsTxt = () => {
    // Group items by category
    const categoryGroups = {};
    shoppingList.forEach(item => {
      if (!categoryGroups[item.category]) {
        categoryGroups[item.category] = [];
      }
      categoryGroups[item.category].push(item);
    });
    
    // Format text
    let text = "SHOPPING LIST\n\n";
    
    Object.keys(categoryGroups).sort().forEach(category => {
      text += `${category.toUpperCase()}\n`;
      categoryGroups[category].forEach(item => {
        const amount = item.amount % 1 === 0 ? item.amount.toString() : item.amount.toFixed(2);
        text += `- ${amount} ${item.unit ? item.unit + ' ' : ''}${item.name}`;
        if (showStandardized && item.standardizedDisplay) {
          text += ` (${item.standardizedDisplay})`;
        }
        text += '\n';
      });
      text += '\n';
    });
    
    // Add recipe names at the bottom
    text += 'RECIPES:\n';
    selectedRecipes.forEach(recipe => {
      text += `- ${recipe.title}\n`;
    });
    
    // Create and download the file
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'shopping-list.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    setMessage('Shopping list downloaded');
    setShowMessage(true);
  };
  
  // Handle confirmation to clear the list
  const handleClearList = () => {
    setShowConfirmClear(true);
  };
  
  // Confirm clearing the list
  const confirmClear = () => {
    clearShoppingList();
    setShowConfirmClear(false);
    setMessage('Shopping list cleared');
    setShowMessage(true);
  };
  
  // Calculate completion percentage
  const calculateCompletionPercentage = () => {
    if (shoppingList.length === 0) return 0;
    const checkedItems = shoppingList.filter(item => item.checked).length;
    return (checkedItems / shoppingList.length) * 100;
  };
  
  // Add this function to handle toggling display preference
  const toggleStandardizedDisplay = () => {
    setShowStandardized(prev => !prev);
    setMessage(`${!showStandardized ? 'Standardized' : 'Original'} measurements will be displayed`);
    setShowMessage(true);
  };
  
  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center" sx={{ fontWeight: 700 }}>
          Shopping List Generator
        </Typography>
        
        <Typography variant="subtitle1" color="text.secondary" align="center" sx={{ mb: 2 }}>
          Automatically create a shopping list from your selected recipes
        </Typography>
        
        <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
          <FormControlLabel
            control={
              <Switch
                checked={showStandardized}
                onChange={toggleStandardizedDisplay}
                color="primary"
              />
            }
            label={
              <Typography variant="body2">
                Show {showStandardized ? 'both original and standardized' : 'only original'} measurements
              </Typography>
            }
          />
        </Box>
        
        {/* Main container with two columns */}
        <Grid container spacing={4}>
          {/* Left column - Selected Recipes */}
          <Grid item xs={12} md={4}>
            <Paper 
              elevation={0}
              sx={{ 
                p: 3,
                borderRadius: 2,
                border: `1px solid ${theme.palette.divider}`,
                height: '100%'
              }}
            >
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center' }}>
                  <RestaurantIcon sx={{ mr: 1, color: theme.palette.primary.main }} />
                  Selected Recipes
                </Typography>
                <Box>
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={<AddIcon />}
                    onClick={() => navigate('/search')}
                    sx={{ mr: 1 }}
                  >
                    Add
                  </Button>
                  <IconButton 
                    size="small" 
                    color="error" 
                    onClick={handleClearList}
                    disabled={selectedRecipes.length === 0}
                  >
                    <ClearIcon />
                  </IconButton>
                </Box>
              </Box>
              
              {selectedRecipes.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <KitchenIcon sx={{ fontSize: 48, color: theme.palette.text.secondary, opacity: 0.4, mb: 2 }} />
                  <Typography variant="body1" color="text.secondary">
                    No recipes selected yet
                  </Typography>
                  <Button
                    variant="contained"
                    size="large"
                    startIcon={<AddIcon />}
                    onClick={() => navigate('/search')}
                    sx={{ mt: 2 }}
                  >
                    Add Recipes
                  </Button>
                </Box>
              ) : (
                <Box>
                  <List sx={{ maxHeight: 300, overflow: 'auto', mb: 2 }}>
                    {selectedRecipes.map(recipe => (
                      <Card key={recipe.id} sx={{ mb: 2, borderRadius: 2, overflow: 'hidden' }}>
                        <Box sx={{ display: 'flex' }}>
                          <CardMedia
                            component="img"
                            sx={{ width: 80, height: 80, objectFit: 'cover' }}
                            image={recipe.image}
                            alt={recipe.title}
                          />
                          <Box sx={{ display: 'flex', flexDirection: 'column', flexGrow: 1 }}>
                            <CardContent sx={{ p: 1, pb: '6px!important' }}>
                              <Typography variant="subtitle2" sx={{ fontWeight: 600, lineHeight: 1.2 }}>
                                {recipe.title}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {recipe.extendedIngredients?.length || 0} ingredients
                              </Typography>
                            </CardContent>
                            <CardActions sx={{ px: 1, pt: 0, justifyContent: 'flex-end' }}>
                              <IconButton 
                                size="small" 
                                color="error"
                                onClick={() => removeRecipeFromList(recipe.id)}
                              >
                                <DeleteIcon fontSize="small" />
                              </IconButton>
                            </CardActions>
                          </Box>
                        </Box>
                      </Card>
                    ))}
                  </List>
                  
                  <Button
                    variant="contained"
                    fullWidth
                    size="large"
                    startIcon={<ShoppingCartIcon />}
                    onClick={generateShoppingList}
                    sx={{ mt: 2 }}
                  >
                    Generate Shopping List
                  </Button>
                </Box>
              )}
            </Paper>
          </Grid>
          
          {/* Right column - Shopping List */}
          <Grid item xs={12} md={8}>
            <Paper 
              elevation={0}
              sx={{ 
                p: 3,
                borderRadius: 2,
                border: `1px solid ${theme.palette.divider}`,
              }}
            >
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center' }}>
                  <ShoppingCartIcon sx={{ mr: 1, color: theme.palette.primary.main }} />
                  Shopping List
                </Typography>
                
                {shoppingList.length > 0 && (
                  <Box>
                    <Tooltip title="Copy to clipboard">
                      <IconButton 
                        size="small" 
                        onClick={copyToClipboard}
                        sx={{ mr: 1 }}
                      >
                        <ContentCopyIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Print list">
                      <IconButton 
                        size="small" 
                        onClick={printList}
                        sx={{ mr: 1 }}
                      >
                        <PrintIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Download as text">
                      <IconButton 
                        size="small" 
                        onClick={downloadAsTxt}
                      >
                        <DownloadIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </Box>
                )}
              </Box>
              
              {shoppingList.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 6 }}>
                  {selectedRecipes.length === 0 ? (
                    <>
                      <ShoppingCartIcon sx={{ fontSize: 48, color: theme.palette.text.secondary, opacity: 0.4, mb: 2 }} />
                      <Typography variant="body1" color="text.secondary">
                        Add recipes to generate a shopping list
                      </Typography>
                    </>
                  ) : (
                    <>
                      <ShoppingCartIcon sx={{ fontSize: 48, color: theme.palette.text.secondary, opacity: 0.4, mb: 2 }} />
                      <Typography variant="body1" color="text.secondary">
                        Click "Generate Shopping List" to create your list
                      </Typography>
                      <Button
                        variant="contained"
                        size="large"
                        startIcon={<ShoppingCartIcon />}
                        onClick={generateShoppingList}
                        sx={{ mt: 2 }}
                      >
                        Generate Shopping List
                      </Button>
                    </>
                  )}
                </Box>
              ) : (
                <Box>
                  {/* Progress bar */}
                  <Box sx={{ mb: 3, display: 'flex', alignItems: 'center' }}>
                    <Box sx={{ position: 'relative', display: 'inline-flex', mr: 2 }}>
                      <CircularProgress
                        variant="determinate"
                        value={calculateCompletionPercentage()}
                        size={40}
                        thickness={5}
                      />
                      <Box
                        sx={{
                          top: 0,
                          left: 0,
                          bottom: 0,
                          right: 0,
                          position: 'absolute',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                        }}
                      >
                        <Typography
                          variant="caption"
                          component="div"
                          color="text.secondary"
                          fontWeight="bold"
                        >
                          {Math.round(calculateCompletionPercentage())}%
                        </Typography>
                      </Box>
                    </Box>
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography variant="body2" color="text.secondary">
                        {shoppingList.filter(item => item.checked).length} of {shoppingList.length} items checked
                      </Typography>
                    </Box>
                  </Box>
                  
                  {/* Shopping list by category */}
                  <Box sx={{ maxHeight: 'calc(100vh - 300px)', overflow: 'auto' }}>
                    {Object.entries(
                      shoppingList.reduce((acc, item) => {
                        if (!acc[item.category]) {
                          acc[item.category] = [];
                        }
                        acc[item.category].push(item);
                        return acc;
                      }, {})
                    )
                      .sort(([categoryA], [categoryB]) => categoryA.localeCompare(categoryB))
                      .map(([category, items]) => (
                        <Box key={category} sx={{ mb: 2 }}>
                          <Box 
                            sx={{ 
                              display: 'flex', 
                              alignItems: 'center', 
                              bgcolor: theme.palette.background.default,
                              py: 1,
                              px: 2,
                              borderRadius: 1,
                              cursor: 'pointer'
                            }}
                            onClick={() => toggleCategory(category)}
                          >
                            <Typography variant="subtitle1" sx={{ fontWeight: 600, flexGrow: 1 }}>
                              {category} ({items.length})
                            </Typography>
                            {expandedCategory[category] ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                          </Box>
                          
                          <Collapse in={expandedCategory[category] || false}>
                            <List disablePadding>
                              {items.map(item => (
                                <ListItem
                                  key={item.id}
                                  disablePadding
                                  sx={{ 
                                    py: 0.5, 
                                    bgcolor: item.checked ? 'rgba(0,0,0,0.03)' : 'transparent',
                                    borderRadius: 1,
                                    my: 0.5,
                                  }}
                                  secondaryAction={
                                    editItem?.id === item.id ? (
                                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                        <TextField
                                          value={editAmount}
                                          onChange={(e) => setEditAmount(e.target.value)}
                                          size="small"
                                          type="number"
                                          inputProps={{ min: 0.1, step: 0.1 }}
                                          sx={{ width: 80, mr: 1 }}
                                          autoFocus
                                        />
                                        <IconButton 
                                          edge="end" 
                                          onClick={saveEditItem}
                                          color="primary"
                                          size="small"
                                        >
                                          <AddIcon />
                                        </IconButton>
                                        <IconButton 
                                          edge="end" 
                                          onClick={cancelEdit}
                                          size="small"
                                          sx={{ ml: 0.5 }}
                                        >
                                          <ClearIcon />
                                        </IconButton>
                                      </Box>
                                    ) : (
                                      <Box>
                                        <IconButton 
                                          edge="end" 
                                          onClick={() => startEditItem(item)}
                                          size="small"
                                        >
                                          <EditIcon fontSize="small" />
                                        </IconButton>
                                        <IconButton 
                                          edge="end" 
                                          onClick={() => removeItemFromList(item.id)}
                                          size="small"
                                          sx={{ ml: 0.5 }}
                                        >
                                          <DeleteIcon fontSize="small" />
                                        </IconButton>
                                      </Box>
                                    )
                                  }
                                >
                                  <ListItemText
                                    primary={
                                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                        <Checkbox
                                          edge="start"
                                          checked={item.checked}
                                          onChange={() => toggleItemChecked(item.id)}
                                          sx={{ mr: 1, ml: -1 }}
                                        />
                                        <Box>
                                          <Typography
                                            variant="body1"
                                            sx={{
                                              textDecoration: item.checked ? 'line-through' : 'none',
                                              color: item.checked ? 'text.secondary' : 'text.primary',
                                            }}
                                          >
                                            {item.amount % 1 === 0 ? item.amount : item.amount.toFixed(2)}{' '}
                                            {item.unit && `${item.unit} `}{item.name}
                                          </Typography>
                                          {showStandardized && item.standardizedDisplay && (
                                            <Typography
                                              variant="caption"
                                              color="text.secondary"
                                              sx={{ 
                                                display: 'block',
                                                fontStyle: 'italic',
                                                mt: 0.5 
                                              }}
                                            >
                                              Standardized: {item.standardizedDisplay}
                                            </Typography>
                                          )}
                                        </Box>
                                      </Box>
                                    }
                                  />
                                </ListItem>
                              ))}
                            </List>
                          </Collapse>
                        </Box>
                      ))}
                  </Box>
                </Box>
              )}
            </Paper>
          </Grid>
        </Grid>
      </Box>
      
      {/* Snackbar for messages */}
      <Snackbar
        open={showMessage}
        autoHideDuration={3000}
        onClose={() => setShowMessage(false)}
        message={message}
      />
      
      {/* Confirmation dialog for clearing the list */}
      <Dialog
        open={showConfirmClear}
        onClose={() => setShowConfirmClear(false)}
      >
        <DialogTitle>Clear Shopping List?</DialogTitle>
        <DialogContent>
          <DialogContentText>
            This will remove all selected recipes and clear your shopping list. This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowConfirmClear(false)}>Cancel</Button>
          <Button onClick={confirmClear} color="error">Clear List</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}

export default ShoppingList; 