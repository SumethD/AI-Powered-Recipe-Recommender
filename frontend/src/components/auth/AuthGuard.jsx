import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Box, CircularProgress, Typography } from '@mui/material';

/**
 * AuthGuard component to protect routes that require authentication
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Child components to render if authorized
 * @param {boolean} [props.adminOnly=false] - Whether the route requires admin privileges
 * @returns {JSX.Element} - Rendered component
 */
const AuthGuard = ({ children, adminOnly = false }) => {
  const { user, loading } = useAuth();
  const location = useLocation();

  // Show loading state while checking authentication
  if (loading) {
    return (
      <Box 
        sx={{ 
          display: 'flex', 
          flexDirection: 'column',
          alignItems: 'center', 
          justifyContent: 'center', 
          minHeight: '50vh' 
        }}
      >
        <CircularProgress size={40} />
        <Typography variant="body1" sx={{ mt: 2 }}>
          Verifying authentication...
        </Typography>
      </Box>
    );
  }

  // If not authenticated, redirect to login
  if (!user) {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  }

  // If adminOnly and user is not admin, redirect to home
  if (adminOnly && (!user.app_metadata || !user.app_metadata.roles || !user.app_metadata.roles.includes('admin'))) {
    return <Navigate to="/" replace />;
  }

  // If authenticated and passes role requirements, render children
  return children;
};

export default AuthGuard; 