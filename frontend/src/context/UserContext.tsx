import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { userApi } from '../services/api';

// Define types
export type UserPreferences = {
  diets: string[];
  intolerances: string[];
  cuisines: string[];
  dietary_restrictions?: string[];
  allergies?: string[];
  favorite_cuisines?: string[];
  cooking_skill?: 'beginner' | 'intermediate' | 'advanced';
};

export type User = {
  id: string;
  name: string;
  preferences: UserPreferences;
};

// Context type
type UserContextType = {
  user: User | null;
  loading: boolean;
  isLoading: boolean;
  error: string | null;
  login: (userId: string) => void;
  logout: () => void;
  setUser: (user: User | null) => void;
  updatePreferences: (preferences: Partial<UserPreferences>) => void;
};

// Create context
const UserContext = createContext<UserContextType | null>(null);

// Provider props
type UserProviderProps = {
  children: ReactNode;
};

// Provider component
export const UserProvider = ({ children }: UserProviderProps) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Check for saved user on mount
  useEffect(() => {
    const savedUserId = localStorage.getItem('userId');
    if (savedUserId) {
      login(savedUserId);
    }
  }, []);

  // Login function
  const login = (userId: string) => {
    if (!userId || userId.trim() === '') {
      setError('Invalid user ID');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      // Save user ID to localStorage for persistence
      localStorage.setItem('userId', userId);
      
      // Load user preferences asynchronously
      loadUserPreferences(userId);
      
      setLoading(false);
    } catch (err) {
      setError('Failed to login');
      setLoading(false);
      console.error('Error logging in:', err);
    }
  };

  // Load user preferences
  const loadUserPreferences = async (userId: string) => {
    if (!userId || userId.trim() === '') {
      console.error('Invalid user ID for loading preferences');
      return;
    }

    try {
      const response = await userApi.getPreferences(userId);
      if (response && response.data) {
        setUser({
          id: userId,
          name: userId, // This will be replaced with actual user data from authentication
          preferences: response.data
        });
      }
    } catch (err) {
      console.error('Error loading user preferences:', err);
      setError('Failed to load user preferences');
    }
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('userId');
    setUser(null);
    setError(null);
  };

  // Update preferences
  const updatePreferences = async (preferences: Partial<UserPreferences>) => {
    if (!user) {
      setError('User not logged in');
      return;
    }
    
    if (!preferences || Object.keys(preferences).length === 0) {
      setError('No preferences provided');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // Update local state immediately for better UX
      const updatedUser = {
        ...user,
        preferences: {
          ...user.preferences,
          ...preferences,
        },
      };
      setUser(updatedUser);
      
      // Send update to backend
      const response = await userApi.updatePreferences(user.id, updatedUser.preferences);
      
      if (!response || !response.success) {
        throw new Error('Failed to update preferences on server');
      }
      
      setLoading(false);
    } catch (err) {
      setError('Failed to update preferences');
      setLoading(false);
      console.error('Error updating preferences:', err);
      
      // Revert to previous state on error
      loadUserPreferences(user.id);
    }
  };

  // Context value
  const value = {
    user,
    loading,
    isLoading: loading,
    error,
    login,
    logout,
    setUser,
    updatePreferences,
  };

  // Use React.createElement to avoid JSX linter errors
  return React.createElement(UserContext.Provider, { value }, children);
};

// Custom hook to use the context
export const useUser = (): UserContextType => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};

export default UserContext; 