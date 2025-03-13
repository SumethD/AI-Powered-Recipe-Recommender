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
  Badge,
  Collapse,
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
  VideoCall as VideoCallIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  MoreVert as MoreVertIcon,
} from '@mui/icons-material';
import { useUser } from '../../context/UserContext';

const Header: React.FC = () => {
  const { user, setUser } = useUser();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'));
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [moreMenuAnchorEl, setMoreMenuAnchorEl] = useState<null | HTMLElement>(null);
  const [expandedSection, setExpandedSection] = useState<string | null>(null);

  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
  };

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const handleMoreMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setMoreMenuAnchorEl(event.currentTarget);
  };

  const handleMoreMenuClose = () => {
    setMoreMenuAnchorEl(null);
  };

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section);
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

  // Primary navigation items that always show in the main bar
  const primaryNavItems = [
    { text: 'Home', path: '/', icon: <HomeIcon /> },
    { text: 'Search', path: '/search', icon: <SearchIcon /> },
    { text: 'Favorites', path: '/favorites', icon: <FavoriteIcon /> },
  ];

  // Secondary navigation items that go in the "More" dropdown on desktop
  const secondaryNavItems = [
    { text: 'Chat Assistant', path: '/chat', icon: <ChatIcon /> },
    { text: 'Video-to-Recipe', path: '/video-to-recipe', icon: <VideoCallIcon /> },
  ];

  // All nav items for mobile drawer
  const allNavItems = [...primaryNavItems, ...secondaryNavItems];

  const drawer = (
    <Box sx={{ width: 280, bgcolor: '#FFFEF8' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', p: 2, bgcolor: theme.palette.primary.main }}>
        <RestaurantIcon sx={{ mr: 1.5, color: '#F8F4E3', fontSize: 28 }} />
        <Typography variant="h6" sx={{ fontWeight: 700, color: '#F8F4E3' }}>
          Savorly
        </Typography>
      </Box>
      <Divider />
      <List sx={{ py: 1 }}>
        {allNavItems.map((item) => (
          <ListItem
            button
            component={Link}
            to={item.path}
            key={item.text}
            selected={location.pathname === item.path}
            onClick={() => setDrawerOpen(false)}
            sx={{
              py: 1.5,
              px: 2,
              borderLeft: location.pathname === item.path ? `4px solid ${theme.palette.primary.main}` : '4px solid transparent',
              '&.Mui-selected': {
                backgroundColor: `${theme.palette.primary.main}15`,
                color: theme.palette.primary.main,
                '& .MuiListItemIcon-root': {
                  color: theme.palette.primary.main,
                },
              },
              '&:hover': {
                backgroundColor: `${theme.palette.primary.main}08`,
              },
            }}
          >
            <ListItemIcon sx={{ minWidth: 40, color: location.pathname === item.path ? theme.palette.primary.main : '#697A63' }}>
              {item.icon}
            </ListItemIcon>
            <ListItemText 
              primary={item.text} 
              primaryTypographyProps={{ 
                fontWeight: location.pathname === item.path ? 600 : 400,
                color: location.pathname === item.path ? theme.palette.primary.main : '#3a3a3a'
              }} 
            />
          </ListItem>
        ))}
      </List>
      {user && (
        <>
          <Divider />
          <Box sx={{ p: 2, display: 'flex', alignItems: 'center', bgcolor: '#F8F4E3' }}>
            <Avatar 
              sx={{ 
                bgcolor: theme.palette.secondary.main,
                width: 40,
                height: 40,
                mr: 2
              }}
            >
              {user.name.charAt(0).toUpperCase()}
            </Avatar>
            <Box>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#3a3a3a' }}>
                {user.name}
              </Typography>
              <Typography variant="body2" sx={{ color: '#5a5a5a' }}>
                {user.preferences.cooking_skill} cook
              </Typography>
            </Box>
          </Box>
          <List>
            <ListItem 
              button 
              component={Link} 
              to="/profile"
              onClick={() => setDrawerOpen(false)}
            >
              <ListItemIcon>
                <PersonIcon sx={{ color: theme.palette.primary.main }} />
              </ListItemIcon>
              <ListItemText primary="Profile" primaryTypographyProps={{ color: '#3a3a3a' }} />
            </ListItem>
            <ListItem button onClick={handleLogout}>
              <ListItemIcon>
                <LogoutIcon sx={{ color: theme.palette.error.main }} />
              </ListItemIcon>
              <ListItemText primary="Logout" primaryTypographyProps={{ color: '#3a3a3a' }} />
            </ListItem>
          </List>
        </>
      )}
    </Box>
  );

  return (
    <>
      <AppBar 
        position="sticky" 
        elevation={2}
        sx={{ 
          background: 'linear-gradient(135deg, #8BA872 0%, #697A63 100%)',
          borderRadius: 0,
        }}
      >
        <Container maxWidth="lg">
          <Toolbar disableGutters sx={{ py: { xs: 1, md: 1.5 }, height: { xs: 64, md: 70 } }}>
            {isSmallScreen && (
              <IconButton
                color="inherit"
                aria-label="open drawer"
                edge="start"
                onClick={handleDrawerToggle}
                sx={{ mr: 1 }}
                size="medium"
              >
                <MenuIcon />
              </IconButton>
            )}
            
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <RestaurantIcon sx={{ mr: 1, display: { xs: 'none', sm: 'flex' }, fontSize: 28, color: '#F8F4E3' }} />
              <Typography
                variant="h6"
                component={Link}
                to="/"
                sx={{
                  color: '#F8F4E3',
                  textDecoration: 'none',
                  fontWeight: 'bold',
                  letterSpacing: '0.5px',
                  fontSize: { xs: '1rem', md: '1.25rem' },
                  display: 'flex',
                  alignItems: 'center',
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    transform: 'scale(1.02)',
                  }
                }}
              >
                Savorly
              </Typography>
            </Box>
            
            <Box sx={{ flexGrow: 1 }} />
            
            {!isSmallScreen && (
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                {primaryNavItems.map((item) => (
                  <Button
                    key={item.text}
                    component={Link}
                    to={item.path}
                    color="inherit"
                    sx={{
                      mx: { sm: 0.5, md: 1 },
                      px: { sm: 1.5, md: 2 },
                      py: 1,
                      borderRadius: 1,
                      fontSize: '0.9rem',
                      fontWeight: location.pathname === item.path ? 600 : 400,
                      backgroundColor: location.pathname === item.path ? 'rgba(248, 244, 227, 0.15)' : 'transparent',
                      color: '#F8F4E3',
                      '&:hover': {
                        backgroundColor: 'rgba(248, 244, 227, 0.25)',
                      },
                      transition: 'all 0.2s ease',
                    }}
                    startIcon={item.icon}
                  >
                    {item.text}
                  </Button>
                ))}
                
                {/* More menu for secondary navigation items */}
                <Button
                  color="inherit"
                  onClick={handleMoreMenuOpen}
                  sx={{
                    mx: { sm: 0.5, md: 1 },
                    px: { sm: 1.5, md: 2 },
                    py: 1,
                    borderRadius: 1,
                    fontSize: '0.9rem',
                    color: '#F8F4E3',
                    '&:hover': {
                      backgroundColor: 'rgba(248, 244, 227, 0.25)',
                    },
                  }}
                  endIcon={<MoreVertIcon />}
                >
                  More
                </Button>
                <Menu
                  anchorEl={moreMenuAnchorEl}
                  open={Boolean(moreMenuAnchorEl)}
                  onClose={handleMoreMenuClose}
                  anchorOrigin={{
                    vertical: 'bottom',
                    horizontal: 'right',
                  }}
                  transformOrigin={{
                    vertical: 'top',
                    horizontal: 'right',
                  }}
                  PaperProps={{
                    elevation: 3,
                    sx: {
                      mt: 1,
                      borderRadius: 1,
                      minWidth: 180,
                    },
                  }}
                >
                  {secondaryNavItems.map((item) => (
                    <MenuItem
                      key={item.text}
                      component={Link}
                      to={item.path}
                      onClick={handleMoreMenuClose}
                      sx={{
                        py: 1.5,
                        px: 2,
                        backgroundColor: location.pathname === item.path ? `${theme.palette.primary.main}15` : 'transparent',
                        '&:hover': {
                          backgroundColor: `${theme.palette.primary.main}08`,
                        },
                      }}
                    >
                      <ListItemIcon sx={{ 
                        minWidth: 35, 
                        color: location.pathname === item.path ? theme.palette.primary.main : 'inherit'
                      }}>
                        {item.icon}
                      </ListItemIcon>
                      <ListItemText 
                        primary={item.text} 
                        primaryTypographyProps={{
                          fontWeight: location.pathname === item.path ? 600 : 400,
                          color: location.pathname === item.path ? theme.palette.primary.main : 'inherit'
                        }}
                      />
                    </MenuItem>
                  ))}
                </Menu>
              </Box>
            )}
            
            {/* Login button or user profile */}
            <Box sx={{ ml: { xs: 1, sm: 2 } }}>
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
                        borderRadius: 1,
                        border: '2px solid rgba(248, 244, 227, 0.3)',
                        transition: 'all 0.2s ease',
                        '&:hover': {
                          border: '2px solid rgba(248, 244, 227, 0.8)',
                          transform: 'scale(1.05)',
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
                      elevation: 3,
                      sx: {
                        mt: 1,
                        borderRadius: 1,
                        minWidth: 200,
                        overflow: 'visible',
                      },
                    }}
                  >
                    <Box sx={{ px: 2, py: 1.5 }}>
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
                      sx={{ py: 1.5, px: 2 }}
                    >
                      <ListItemIcon>
                        <PersonIcon fontSize="small" color="primary" />
                      </ListItemIcon>
                      <ListItemText>Profile</ListItemText>
                    </MenuItem>
                    <MenuItem onClick={handleLogout} sx={{ py: 1.5, px: 2 }}>
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
                  sx={{ 
                    borderRadius: 1,
                    borderColor: 'rgba(248, 244, 227, 0.5)',
                    px: { xs: 2, sm: 3 },
                    py: 0.8,
                    minWidth: { xs: 70, sm: 85 },
                    fontSize: { xs: '0.85rem', sm: '0.9rem' },
                    color: '#F8F4E3',
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      borderColor: 'rgba(248, 244, 227, 0.9)',
                      backgroundColor: 'rgba(248, 244, 227, 0.15)',
                      transform: 'scale(1.05)',
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