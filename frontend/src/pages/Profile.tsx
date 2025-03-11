import React from 'react';
import { Container, Typography, Box, Paper, Avatar, Divider, Button, Grid, TextField } from '@mui/material';
import { Person as PersonIcon } from '@mui/icons-material';

const Profile: React.FC = () => {
  return (
    <Container maxWidth="md">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 4 }}>
            <Avatar sx={{ width: 80, height: 80, mr: 3, bgcolor: 'primary.main' }}>
              <PersonIcon fontSize="large" />
            </Avatar>
            <Box>
              <Typography variant="h4" component="h1">
                User Profile
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Manage your account information
              </Typography>
            </Box>
          </Box>
          
          <Divider sx={{ mb: 4 }} />
          
          <Box component="form">
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="First Name"
                  defaultValue="John"
                  variant="outlined"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Last Name"
                  defaultValue="Doe"
                  variant="outlined"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Email Address"
                  defaultValue="john.doe@example.com"
                  variant="outlined"
                  disabled
                />
              </Grid>
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  Dietary Preferences
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  These preferences will be used to customize your recipe recommendations
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Favorite Cuisine"
                  defaultValue="Italian"
                  variant="outlined"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Diet Type"
                  defaultValue="Vegetarian"
                  variant="outlined"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Food Allergies"
                  defaultValue="Peanuts, Shellfish"
                  variant="outlined"
                  multiline
                  rows={2}
                />
              </Grid>
              <Grid item xs={12}>
                <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
                  <Button variant="contained" color="primary">
                    Save Changes
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default Profile; 