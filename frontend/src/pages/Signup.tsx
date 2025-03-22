import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Container, Typography, Box, TextField, Button, Paper, Link, Alert } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

export default function Signup() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const { signUp } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await signUp(email, password, fullName);
    } catch (err: any) {
      // Handle the case where user is already registered
      if (err.message.toLowerCase().includes('user already registered')) {
        setError('This email is already registered. Please login instead.');
      } else {
        setError(err.message);
      }
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 8, mb: 4 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h4" component="h1" align="center" gutterBottom>
            Sign Up
          </Typography>
          <Typography variant="body1" align="center" color="text.secondary" sx={{ mb: 3 }}>
            Create your account
          </Typography>
          
          {error && (
            <Alert 
              severity={error.includes('already registered') ? "info" : "error"} 
              sx={{ mb: 2 }}
              action={
                error.includes('already registered') && (
                  <Button color="inherit" size="small" component={RouterLink} to="/login">
                    Login
                  </Button>
                )
              }
            >
              {error}
            </Alert>
          )}
          
          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
            <TextField
              margin="normal"
              required
              fullWidth
              label="Full Name"
              name="fullName"
              autoComplete="name"
              autoFocus
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              label="Email Address"
              name="email"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type="password"
              autoComplete="new-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
            >
              Sign Up
            </Button>
            <Box sx={{ textAlign: 'center', mt: 2 }}>
              <Link component={RouterLink} to="/login" variant="body2">
                Already have an account? Login
              </Link>
            </Box>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
}