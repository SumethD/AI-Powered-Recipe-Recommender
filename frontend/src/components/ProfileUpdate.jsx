import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  CircularProgress,
  Alert,
  Paper,
  Chip,
  Divider,
  Avatar
} from '@mui/material';
import { useAuth } from '../context/AuthContext';
import { getUserProfile, updateUserProfile } from '../utils/userProfile';

function ProfileUpdate() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [profile, setProfile] = useState({
    fullName: '',
    avatarUrl: '',
    dietaryRestrictions: [],
    favoriteCuisines: []
  });
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  
  // Fetch user profile on component mount
  useEffect(() => {
    if (user) {
      fetchUserProfile();
    } else {
      setLoading(false);
    }
  }, [user]);
  
  const fetchUserProfile = async () => {
    try {
      setLoading(true);
      const { data, error } = await getUserProfile(user.id);
      
      if (error) throw error;
      
      if (data) {
        setProfile({
          fullName: data.full_name || '',
          avatarUrl: data.avatar_url || '',
          dietaryRestrictions: data.dietary_restrictions || [],
          favoriteCuisines: data.favorite_cuisines || []
        });
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
      setError('Failed to load profile data');
    } finally {
      setLoading(false);
    }
  };
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setProfile(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);
    setSaving(true);
    
    try {
      const updates = {
        full_name: profile.fullName,
        avatar_url: profile.avatarUrl,
        dietary_restrictions: profile.dietaryRestrictions,
        favorite_cuisines: profile.favoriteCuisines,
        updated_at: new Date()
      };
      
      const { error } = await updateUserProfile(user.id, updates);
      
      if (error) throw error;
      
      setSuccess(true);
    } catch (error) {
      console.error('Error updating profile:', error);
      setError('Failed to update profile');
    } finally {
      setSaving(false);
    }
  };
  
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }
  
  if (!user) {
    return (
      <Alert severity="info">
        Please log in to view and edit your profile.
      </Alert>
    );
  }
  
  return (
    <Paper elevation={0} sx={{ p: 3, border: '1px solid #e0e0e0' }}>
      <Typography variant="h5" gutterBottom>
        Your Profile
      </Typography>
      <Divider sx={{ mb: 3 }} />
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Profile updated successfully!
        </Alert>
      )}
      
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <Avatar
          src={profile.avatarUrl}
          alt={profile.fullName || user.email}
          sx={{ width: 64, height: 64, mr: 2 }}
        />
        <Box>
          <Typography variant="subtitle1">
            {profile.fullName || 'User'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {user.email}
          </Typography>
        </Box>
      </Box>
      
      <Box component="form" onSubmit={handleSubmit} noValidate>
        <TextField
          margin="normal"
          fullWidth
          id="fullName"
          label="Full Name"
          name="fullName"
          value={profile.fullName}
          onChange={handleChange}
          disabled={saving}
        />
        
        <TextField
          margin="normal"
          fullWidth
          id="avatarUrl"
          label="Avatar URL"
          name="avatarUrl"
          value={profile.avatarUrl}
          onChange={handleChange}
          disabled={saving}
          helperText="Enter a URL for your profile picture"
        />
        
        <Box sx={{ mt: 3 }}>
          <Button
            type="submit"
            variant="contained"
            disabled={saving}
            sx={{ mr: 1 }}
          >
            {saving ? <CircularProgress size={24} /> : 'Save Changes'}
          </Button>
          
          <Button
            variant="outlined"
            onClick={fetchUserProfile}
            disabled={saving || loading}
          >
            Reset
          </Button>
        </Box>
      </Box>
    </Paper>
  );
}

export default ProfileUpdate; 