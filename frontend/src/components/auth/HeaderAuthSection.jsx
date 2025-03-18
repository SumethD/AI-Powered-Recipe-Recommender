import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Avatar,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Divider,
  CircularProgress
} from '@mui/material';
import {
  AccountCircle as AccountCircleIcon,
  Logout as LogoutIcon,
  Person as PersonIcon,
  Favorite as FavoriteIcon,
  ShoppingCart as ShoppingCartIcon
} from '@mui/icons-material';
import { useAuth } from '../../context/AuthContext';
import { signOut } from '../../utils/supabaseClient';

function HeaderAuthSection() {
  const { user, loading } = useAuth();
  const navigate = useNavigate();
  
  // Menu state
  const [anchorEl, setAnchorEl] = useState(null);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  
  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };
  
  const handleLogin = () => {
    navigate('/login');
  };
  
  const handleRegister = () => {
    navigate('/register');
  };
  
  const handleProfile = () => {
    handleClose();
    navigate('/profile');
  };
  
  const handleFavorites = () => {
    handleClose();
    navigate('/favorites');
  };
  
  const handleShoppingList = () => {
    handleClose();
    navigate('/shopping-list');
  };
  
  const handleLogout = async () => {
    handleClose();
    setIsLoggingOut(true);
    
    try {
      const { error } = await signOut();
      
      if (error) throw error;
      
      // Navigate to home page after successful logout
      navigate('/');
    } catch (error) {
      console.error('Error signing out:', error);
    } finally {
      setIsLoggingOut(false);
    }
  };
  
  // Show loading spinner while checking auth state
  if (loading) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center' }}>
        <CircularProgress size={24} color="inherit" />
      </Box>
    );
  }
  
  // User is not logged in
  if (!user) {
    return (
      <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
        <Button 
          variant="outlined" 
          color="inherit" 
          onClick={handleLogin}
          sx={{ borderColor: 'rgba(255, 255, 255, 0.5)' }}
        >
          Sign In
        </Button>
        <Button 
          variant="contained" 
          color="secondary" 
          onClick={handleRegister}
        >
          Sign Up
        </Button>
      </Box>
    );
  }
  
  // User is logged in
  return (
    <Box sx={{ display: 'flex', alignItems: 'center' }}>
      {isLoggingOut ? (
        <CircularProgress size={24} color="inherit" />
      ) : (
        <>
          <Button
            aria-label="account of current user"
            aria-controls="menu-appbar"
            aria-haspopup="true"
            onClick={handleMenu}
            color="inherit"
            startIcon={
              user.user_metadata?.avatar_url ? (
                <Avatar 
                  src={user.user_metadata.avatar_url} 
                  alt={user.user_metadata?.full_name || user.email}
                  sx={{ width: 32, height: 32 }}
                />
              ) : (
                <AccountCircleIcon />
              )
            }
          >
            {user.user_metadata?.full_name?.split(' ')[0] || 'Account'}
          </Button>
          <Menu
            id="menu-appbar"
            anchorEl={anchorEl}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'right',
            }}
            keepMounted
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            open={Boolean(anchorEl)}
            onClose={handleClose}
          >
            <MenuItem onClick={handleProfile}>
              <ListItemIcon>
                <PersonIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>Profile</ListItemText>
            </MenuItem>
            
            <MenuItem onClick={handleFavorites}>
              <ListItemIcon>
                <FavoriteIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>Favorites</ListItemText>
            </MenuItem>
            
            <MenuItem onClick={handleShoppingList}>
              <ListItemIcon>
                <ShoppingCartIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>Shopping List</ListItemText>
            </MenuItem>
            
            <Divider />
            
            <MenuItem onClick={handleLogout}>
              <ListItemIcon>
                <LogoutIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>Sign Out</ListItemText>
            </MenuItem>
          </Menu>
        </>
      )}
    </Box>
  );
}

export default HeaderAuthSection; 