import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Box,
  useMediaQuery,
  useTheme,
  Avatar,
  Menu,
  MenuItem,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Container,
  Tooltip,
  Divider,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Home as HomeIcon,
  Search as SearchIcon,
  Favorite as FavoriteIcon,
  Person as PersonIcon,
  Chat as ChatIcon,
  Restaurant as RestaurantIcon,
  Logout as LogoutIcon,
} from '@mui/icons-material';
import { useUser } from '../../context/UserContext';

const Header: React.FC = () => {
  const { user, setUser } = useUser();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
  };

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    setUser(null);
    handleProfileMenuClose();
  };

  const handleLogin = () => {
    // For demo purposes, create a mock user
    setUser({
      id: 'test_user_123',
      name: 'Test User',
      preferences: {
        diets: ['vegetarian'],
        intolerances: ['peanuts'],
        cuisines: ['italian', 'mexican', 'thai'],
        dietary_restrictions: ['vegetarian'],
        allergies: ['peanuts'],
        favorite_cuisines: ['italian', 'mexican', 'thai'],
        cooking_skill: 'intermediate',
      },
    });
    handleProfileMenuClose();
  };

  const navItems = [
    { text: 'Home', path: '/', icon: <HomeIcon /> },
    { text: 'Search Recipes', path: '/search', icon: <SearchIcon /> },
    { text: 'Favorites', path: '/favorites', icon: <FavoriteIcon /> },
    { text: 'Chat Assistant', path: '/chat', icon: <ChatIcon /> },
  ];

  const drawer = (
    <Box sx={{ width: 280, pt: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', px: 3, pb: 3 }}>
        <RestaurantIcon sx={{ mr: 1.5, color: theme.palette.primary.main, fontSize: 28 }} />
        <Typography variant="h6" sx={{ fontWeight: 700 }}>
          Recipe Recommender
        </Typography>
      </Box>
      <Divider />
      <List sx={{ pt: 3 }}>
        {navItems.map((item) => (
          <ListItem
            button
            component={Link}
            to={item.path}
            key={item.text}
            selected={location.pathname === item.path}
            sx={{
              borderRadius: 0,
              mr: 0,
              mb: 0,
              py: 2.5,
              px: 3,
              borderLeft: location.pathname === item.path ? `4px solid ${theme.palette.primary.main}` : '4px solid transparent',
              '&.Mui-selected': {
                bgcolor: `${theme.palette.primary.main}08`,
                color: theme.palette.primary.main,
                '& .MuiListItemIcon-root': {
                  color: theme.palette.primary.main,
                },
              },
              '&:hover': {
                bgcolor: `${theme.palette.primary.main}04`,
              },
            }}
          >
            <ListItemIcon sx={{ minWidth: 40 }}>{item.icon}</ListItemIcon>
            <ListItemText 
              primary={item.text} 
              primaryTypographyProps={{ 
                fontWeight: location.pathname === item.path ? 600 : 400 
              }} 
            />
          </ListItem>
        ))}
      </List>
      {user && (
        <>
          <Divider sx={{ mt: 2 }} />
          <Box sx={{ p: 3, display: 'flex', alignItems: 'center' }}>
            <Avatar 
              sx={{ 
                bgcolor: theme.palette.primary.main,
                width: 40,
                height: 40,
                mr: 2
              }}
            >
              {user.name.charAt(0).toUpperCase()}
            </Avatar>
            <Box>
              <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                {user.name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {user.preferences.cooking_skill} cook
              </Typography>
            </Box>
          </Box>
        </>
      )}
    </Box>
  );

  return (
    <>
      <AppBar 
        position="sticky" 
        elevation={0}
        sx={{ 
          background: `linear-gradient(90deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
          borderRadius: 0,
        }}
      >
        <Container maxWidth="lg">
          <Toolbar disableGutters sx={{ py: 2 }}>
            {isMobile && (
              <IconButton
                color="inherit"
                aria-label="open drawer"
                edge="start"
                onClick={handleDrawerToggle}
                sx={{ mr: 2 }}
              >
                <MenuIcon />
              </IconButton>
            )}
            
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <RestaurantIcon sx={{ mr: 1.5, display: { xs: 'none', sm: 'flex' }, fontSize: 28 }} />
              <Typography
                variant="h6"
                component={Link}
                to="/"
                sx={{
                  color: 'white',
                  textDecoration: 'none',
                  fontWeight: 'bold',
                  letterSpacing: '0.5px',
                  fontSize: { xs: '1.1rem', md: '1.25rem' }
                }}
              >
                Recipe Recommender
              </Typography>
            </Box>
            
            <Box sx={{ flexGrow: 1 }} />
            
            {!isMobile && (
              <Box sx={{ display: 'flex' }}>
                {navItems.map((item) => (
                  <Button
                    key={item.text}
                    component={Link}
                    to={item.path}
                    color="inherit"
                    sx={{
                      mx: 1.5,
                      px: 3,
                      py: 2,
                      borderRadius: 0,
                      position: 'relative',
                      fontSize: '1rem',
                      fontWeight: location.pathname === item.path ? 600 : 400,
                      '&::after': {
                        content: '""',
                        position: 'absolute',
                        bottom: 0,
                        left: 0,
                        right: 0,
                        height: '3px',
                        width: '100%',
                        backgroundColor: 'white',
                        transform: location.pathname === item.path ? 'scaleY(1)' : 'scaleY(0)',
                        transformOrigin: 'bottom',
                        transition: 'transform 0.3s ease',
                      },
                      '&:hover::after': {
                        transform: 'scaleY(1)',
                      }
                    }}
                    startIcon={item.icon}
                  >
                    {item.text}
                  </Button>
                ))}
              </Box>
            )}
            
            <Box sx={{ ml: 3 }}>
              {user ? (
                <>
                  <Tooltip title="Account settings">
                    <IconButton
                      onClick={handleProfileMenuOpen}
                      color="inherit"
                      aria-label="account of current user"
                      aria-controls="menu-appbar"
                      aria-haspopup="true"
                      sx={{ 
                        p: 0.5,
                        borderRadius: 0,
                        border: '2px solid rgba(255, 255, 255, 0.3)',
                        '&:hover': {
                          border: '2px solid rgba(255, 255, 255, 0.8)',
                        }
                      }}
                    >
                      <Avatar 
                        sx={{ 
                          bgcolor: theme.palette.secondary.main,
                          color: theme.palette.secondary.contrastText,
                          width: 32,
                          height: 32,
                          fontWeight: 'bold'
                        }}
                      >
                        {user.name.charAt(0).toUpperCase()}
                      </Avatar>
                    </IconButton>
                  </Tooltip>
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
                    onClose={handleProfileMenuClose}
                    PaperProps={{
                      elevation: 2,
                      sx: {
                        mt: 1.5,
                        minWidth: 180,
                        borderRadius: 0,
                        overflow: 'visible',
                        '&:before': {
                          content: '""',
                          display: 'block',
                          position: 'absolute',
                          top: 0,
                          right: 14,
                          width: 10,
                          height: 10,
                          bgcolor: 'background.paper',
                          transform: 'translateY(-50%) rotate(45deg)',
                          zIndex: 0,
                        },
                      },
                    }}
                  >
                    <Box sx={{ px: 3, py: 2 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                        {user.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {user.preferences.cooking_skill} cook
                      </Typography>
                    </Box>
                    <Divider />
                    <MenuItem
                      component={Link}
                      to="/profile"
                      onClick={handleProfileMenuClose}
                      sx={{ py: 2, px: 3 }}
                    >
                      <ListItemIcon>
                        <PersonIcon fontSize="small" color="primary" />
                      </ListItemIcon>
                      <ListItemText>Profile</ListItemText>
                    </MenuItem>
                    <MenuItem onClick={handleLogout} sx={{ py: 2, px: 3 }}>
                      <ListItemIcon>
                        <LogoutIcon fontSize="small" color="error" />
                      </ListItemIcon>
                      <ListItemText>Logout</ListItemText>
                    </MenuItem>
                  </Menu>
                </>
              ) : (
                <Button 
                  color="inherit" 
                  onClick={handleLogin}
                  variant="outlined"
                  size="large"
                  sx={{ 
                    borderRadius: 0,
                    borderColor: 'rgba(255, 255, 255, 0.5)',
                    px: 3,
                    py: 1,
                    '&:hover': {
                      borderColor: 'rgba(255, 255, 255, 0.9)',
                      backgroundColor: 'rgba(255, 255, 255, 0.1)'
                    }
                  }}
                >
                  Login
                </Button>
              )}
            </Box>
          </Toolbar>
        </Container>
      </AppBar>
      <Drawer
        variant="temporary"
        open={drawerOpen}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true, // Better open performance on mobile
        }}
        sx={{
          display: { xs: 'block', md: 'none' },
          '& .MuiDrawer-paper': { boxSizing: 'border-box', width: 280 },
        }}
      >
        {drawer}
      </Drawer>
    </>
  );
};

export default Header; 