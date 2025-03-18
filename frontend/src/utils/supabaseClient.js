import { createClient } from '@supabase/supabase-js';

// Get environment variables
const supabaseUrl = process.env.REACT_APP_SUPABASE_URL;
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY;

// Validate required environment variables
if (!supabaseUrl || !supabaseAnonKey) {
  console.error('Missing Supabase credentials. Check your .env file for REACT_APP_SUPABASE_URL and REACT_APP_SUPABASE_ANON_KEY');
}

// Initialize Supabase client
export const supabase = createClient(supabaseUrl, supabaseAnonKey);

/**
 * Register a new user with email and password
 * @param {string} email - User's email address
 * @param {string} password - User's password
 * @param {Object} options - Additional options like metadata
 * @returns {Promise<{data, error}>} - Registration result
 */
export const signUp = async (email, password, options = {}) => {
  try {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options
    });
    
    if (error) throw error;
    
    // Notify backend about new user registration
    if (data?.user) {
      try {
        await fetch('/api/auth/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: data.user.id,
            email: data.user.email,
            metadata: options.data || {}
          }),
        });
      } catch (backendError) {
        console.error('Error notifying backend about registration:', backendError);
        // Continue with registration process despite backend notification failure
      }
    }
    
    return { data, error: null };
  } catch (error) {
    console.error('Registration error:', error.message);
    return { data: null, error };
  }
};

/**
 * Sign in a user with email and password
 * @param {string} email - User's email address
 * @param {string} password - User's password
 * @returns {Promise<{data, error}>} - Login result
 */
export const signIn = async (email, password) => {
  try {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });
    
    if (error) throw error;
    
    // Notify backend about user login
    if (data?.user) {
      try {
        await fetch('/api/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${data.session.access_token}`
          },
          body: JSON.stringify({
            user_id: data.user.id
          }),
        });
      } catch (backendError) {
        console.error('Error notifying backend about login:', backendError);
        // Continue with login process despite backend notification failure
      }
    }
    
    return { data, error: null };
  } catch (error) {
    console.error('Login error:', error.message);
    return { data: null, error };
  }
};

/**
 * Sign out the current user
 * @returns {Promise<{data, error}>} - Sign out result
 */
export const signOut = async () => {
  try {
    const { error } = await supabase.auth.signOut();
    
    if (error) throw error;
    
    // Notify backend about user logout
    try {
      await fetch('/api/auth/logout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });
    } catch (backendError) {
      console.error('Error notifying backend about logout:', backendError);
      // Continue with logout process despite backend notification failure
    }
    
    return { data: true, error: null };
  } catch (error) {
    console.error('Logout error:', error.message);
    return { data: null, error };
  }
};

/**
 * Get current authenticated user
 * @returns {Promise<{data, error}>} - Current user data
 */
export const getCurrentUser = async () => {
  try {
    const { data, error } = await supabase.auth.getUser();
    if (error) throw error;
    return { data, error: null };
  } catch (error) {
    console.error('Error getting current user:', error.message);
    return { data: null, error };
  }
};

/**
 * Get current session
 * @returns {Promise<{data, error}>} - Current session data
 */
export const getSession = async () => {
  try {
    const { data, error } = await supabase.auth.getSession();
    if (error) throw error;
    return { data, error: null };
  } catch (error) {
    console.error('Error getting session:', error.message);
    return { data: null, error };
  }
};

/**
 * Update user data
 * @param {Object} userData - User data to update
 * @returns {Promise<{data, error}>} - Update result
 */
export const updateUserData = async (userData) => {
  try {
    const { data, error } = await supabase.auth.updateUser(userData);
    if (error) throw error;
    return { data, error: null };
  } catch (error) {
    console.error('Error updating user data:', error.message);
    return { data: null, error };
  }
};

export default supabase; 