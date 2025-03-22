import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  Divider,
  TextField,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  OutlinedInput,
  Checkbox,
  ListItemText,
  FormHelperText,
  Alert,
  Snackbar,
  CircularProgress,
} from '@mui/material';
import {
  Save as SaveIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material';
import { useUser } from '../context/UserContext';
import { recipeApi } from '../services/api';

// Define the available options
const CUISINES = [
  'African', 'American', 'British', 'Cajun', 'Caribbean', 'Chinese', 'Eastern European',
  'European', 'French', 'German', 'Greek', 'Indian', 'Irish', 'Italian', 'Japanese',
  'Jewish', 'Korean', 'Latin American', 'Mediterranean', 'Mexican', 'Middle Eastern',
  'Nordic', 'Southern', 'Spanish', 'Thai', 'Vietnamese'
];

const DIETS = [
  'Gluten Free', 'Ketogenic', 'Vegetarian', 'Lacto-Vegetarian', 'Ovo-Vegetarian',
  'Vegan', 'Pescetarian', 'Paleo', 'Primal', 'Low FODMAP', 'Whole30'
];

const ALLERGIES = [
  'Dairy', 'Egg', 'Gluten', 'Grain', 'Peanut', 'Seafood', 'Sesame',
  'Shellfish', 'Soy', 'Sulfite', 'Tree Nut', 'Wheat'
];

const COOKING_SKILLS = ['beginner', 'intermediate', 'advanced'];

const UserProfile: React.FC = () => {
  const navigate = useNavigate();
  const { user, updatePreferences, isLoading } = useUser();
  
  const [cuisines, setCuisines] = useState<string[]>([]);
  const [diets, setDiets] = useState<string[]>([]);
  const [intolerances, setIntolerances] = useState<string[]>([]);
  const [isFiltersLoading, setIsFiltersLoading] = useState<boolean>(false);
  
  const [selectedDiets, setSelectedDiets] = useState<string[]>([]);
  const [selectedAllergies, setSelectedAllergies] = useState<string[]>([]);
  const [selectedCuisines, setSelectedCuisines] = useState<string[]>([]);
  const [cookingSkill, setCookingSkill] = useState<string>('');
  
  const [success, setSuccess] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Load filters data on mount
  useEffect(() => {
    const loadFilters = async () => {
      setIsFiltersLoading(true);
      try {
        const [cuisinesRes, dietsRes, intolerancesRes] = await Promise.all([
          recipeApi.getCuisines(),
          recipeApi.getDiets(),
          recipeApi.getIntolerances(),
        ]);
        
        if (cuisinesRes.success) {
          setCuisines(cuisinesRes.cuisines);
        }
        
        if (dietsRes.success) {
          setDiets(dietsRes.diets);
        }
        
        if (intolerancesRes.success) {
          setIntolerances(intolerancesRes.intolerances);
        }
      } catch (error) {
        console.error('Error loading filters:', error);
        setError('Failed to load preferences options. Please try again later.');
      } finally {
        setIsFiltersLoading(false);
      }
    };
    
    loadFilters();
  }, []);

  // Load user preferences
  useEffect(() => {
    if (user && user.preferences) {
      setSelectedDiets(user.preferences.diets || []);
      setSelectedAllergies(user.preferences.intolerances || []);
      setSelectedCuisines(user.preferences.cuisines || []);
      setCookingSkill(user.preferences.cooking_skill || '');
    }
  }, [user]);

  const handleSavePreferences = async () => {
    if (!user) {
      setError('You must be logged in to save preferences');
      return;
    }

    try {
      setError(null);
      await updatePreferences({
        diets: selectedDiets,
        intolerances: selectedAllergies,
        cuisines: selectedCuisines,
        cooking_skill: cookingSkill as 'beginner' | 'intermediate' | 'advanced',
      });
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError('Failed to update preferences');
    }
  };

  const handleCancel = () => {
    if (user && user.preferences) {
      setSelectedDiets(user.preferences.diets || []);
      setSelectedAllergies(user.preferences.intolerances || []);
      setSelectedCuisines(user.preferences.cuisines || []);
      setCookingSkill(user.preferences.cooking_skill || '');
    }
  };

  const handleCloseSnackbar = () => {
    setSuccess(false);
  };

  if (!user) {
    return (
      <Container maxWidth="md">
        <Paper elevation={3} sx={{ p: 4, mt: 4, textAlign: 'center' }}>
          <Typography variant="h5" gutterBottom>
            Please Log In to View Your Profile
          </Typography>
          <Typography variant="body1" paragraph>
            You need to be logged in to view and edit your profile.
          </Typography>
          <Button
            variant="contained"
            color="primary"
            onClick={() => navigate('/')}
            sx={{ mt: 2 }}
          >
            Go to Home
          </Button>
        </Paper>
      </Container>
    );
  }

  return (
    <Container maxWidth="md">
      <Typography variant="h4" component="h1" gutterBottom>
        User Profile
      </Typography>

      <Paper elevation={3} sx={{ p: 4, mb: 4 }}>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h5" gutterBottom>
            Account Information
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="User ID"
                value={user.id}
                disabled
                variant="outlined"
              />
            </Grid>
          </Grid>
        </Box>

        <Box>
          <Typography variant="h5" gutterBottom>
            Dietary Preferences
          </Typography>
          <Divider sx={{ mb: 2 }} />
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel id="cooking-skill-label">Cooking Skill</InputLabel>
                <Select
                  labelId="cooking-skill-label"
                  value={cookingSkill}
                  onChange={(e) => setCookingSkill(e.target.value)}
                  label="Cooking Skill"
                >
                  {COOKING_SKILLS.map((skill) => (
                    <MenuItem key={skill} value={skill}>
                      {skill.charAt(0).toUpperCase() + skill.slice(1)}
                    </MenuItem>
                  ))}
                </Select>
                <FormHelperText>Select your cooking experience level</FormHelperText>
              </FormControl>
            </Grid>

            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel id="cuisines-label">Favorite Cuisines</InputLabel>
                <Select
                  labelId="cuisines-label"
                  multiple
                  value={selectedCuisines}
                  onChange={(e) => setSelectedCuisines(typeof e.target.value === 'string' ? e.target.value.split(',') : e.target.value)}
                  input={<OutlinedInput label="Favorite Cuisines" />}
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((value) => (
                        <Chip key={value} label={value} />
                      ))}
                    </Box>
                  )}
                >
                  {CUISINES.map((cuisine) => (
                    <MenuItem key={cuisine} value={cuisine}>
                      {cuisine}
                    </MenuItem>
                  ))}
                </Select>
                <FormHelperText>Select your favorite cuisines</FormHelperText>
              </FormControl>
            </Grid>

            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel id="diets-label">Dietary Restrictions</InputLabel>
                <Select
                  labelId="diets-label"
                  multiple
                  value={selectedDiets}
                  onChange={(e) => setSelectedDiets(typeof e.target.value === 'string' ? e.target.value.split(',') : e.target.value)}
                  input={<OutlinedInput label="Dietary Restrictions" />}
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((value) => (
                        <Chip key={value} label={value} />
                      ))}
                    </Box>
                  )}
                >
                  {DIETS.map((diet) => (
                    <MenuItem key={diet} value={diet}>
                      {diet}
                    </MenuItem>
                  ))}
                </Select>
                <FormHelperText>Select any dietary restrictions you have</FormHelperText>
              </FormControl>
            </Grid>

            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel id="allergies-label">Allergies/Intolerances</InputLabel>
                <Select
                  labelId="allergies-label"
                  multiple
                  value={selectedAllergies}
                  onChange={(e) => setSelectedAllergies(typeof e.target.value === 'string' ? e.target.value.split(',') : e.target.value)}
                  input={<OutlinedInput label="Allergies/Intolerances" />}
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((value) => (
                        <Chip key={value} label={value} />
                      ))}
                    </Box>
                  )}
                >
                  {ALLERGIES.map((allergy) => (
                    <MenuItem key={allergy} value={allergy}>
                      {allergy}
                    </MenuItem>
                  ))}
                </Select>
                <FormHelperText>Select any food allergies or intolerances you have</FormHelperText>
              </FormControl>
            </Grid>
          </Grid>
          
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3, gap: 2 }}>
            <Button
              variant="outlined"
              startIcon={<CancelIcon />}
              onClick={handleCancel}
              disabled={isLoading}
            >
              Reset
            </Button>
            <Button
              variant="contained"
              color="primary"
              startIcon={isLoading ? <CircularProgress size={24} /> : <SaveIcon />}
              onClick={handleSavePreferences}
              disabled={isLoading}
            >
              Save Preferences
            </Button>
          </Box>
        </Box>
      </Paper>
      
      <Snackbar
        open={success}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseSnackbar} severity="success" sx={{ width: '100%' }}>
          Preferences saved successfully!
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default UserProfile; 