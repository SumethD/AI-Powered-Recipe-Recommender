import React from 'react';
import { Box, Container, Typography, Link, Divider, Grid, IconButton, useTheme } from '@mui/material';
import { GitHub as GitHubIcon, Twitter as TwitterIcon, Instagram as InstagramIcon, Restaurant as RestaurantIcon } from '@mui/icons-material';

const Footer: React.FC = () => {
  const theme = useTheme();
  
  return (
    <Box
      component="footer"
      sx={{
        py: 4,
        backgroundColor: theme.palette.background.default,
        borderTop: `1px solid ${theme.palette.divider}`,
        mt: 'auto',
      }}
    >
      <Container maxWidth="lg">
        <Grid container spacing={4}>
          <Grid item xs={12} md={4}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <RestaurantIcon sx={{ mr: 1, color: theme.palette.primary.main }} />
              <Typography variant="h6" sx={{ fontWeight: 700 }}>
                Savorly
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Discover delicious recipes tailored to your preferences, dietary needs, and available ingredients.
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <IconButton size="small" aria-label="github" sx={{ color: 'text.secondary' }}>
                <GitHubIcon fontSize="small" />
              </IconButton>
              <IconButton size="small" aria-label="twitter" sx={{ color: 'text.secondary' }}>
                <TwitterIcon fontSize="small" />
              </IconButton>
              <IconButton size="small" aria-label="instagram" sx={{ color: 'text.secondary' }}>
                <InstagramIcon fontSize="small" />
              </IconButton>
            </Box>
          </Grid>
          
          <Grid item xs={12} md={2}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 2 }}>
              Features
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Link href="/search" underline="hover" color="text.secondary">
                Recipe Search
              </Link>
              <Link href="/chat" underline="hover" color="text.secondary">
                AI Assistant
              </Link>
              <Link href="/favorites" underline="hover" color="text.secondary">
                Favorites
              </Link>
            </Box>
          </Grid>
          
          <Grid item xs={12} md={2}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 2 }}>
              Resources
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Link href="#" underline="hover" color="text.secondary">
                Blog
              </Link>
              <Link href="#" underline="hover" color="text.secondary">
                Cooking Tips
              </Link>
              <Link href="#" underline="hover" color="text.secondary">
                FAQ
              </Link>
            </Box>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 2 }}>
              Powered By
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Link href="https://openai.com/" target="_blank" rel="noopener" underline="hover" color="text.secondary">
                OpenAI
              </Link>
              <Link href="https://www.edamam.com/" target="_blank" rel="noopener" underline="hover" color="text.secondary">
                Edamam API
              </Link>
            </Box>
          </Grid>
        </Grid>
        
        <Divider sx={{ my: 3 }} />
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap' }}>
          <Typography variant="body2" color="text.secondary">
            © {new Date().getFullYear()} Savorly. All rights reserved.
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, mt: { xs: 2, sm: 0 } }}>
            <Link href="#" underline="hover" color="text.secondary" variant="body2">
              Privacy Policy
            </Link>
            <Link href="#" underline="hover" color="text.secondary" variant="body2">
              Terms of Service
            </Link>
          </Box>
        </Box>
      </Container>
    </Box>
  );
};

export default Footer; 