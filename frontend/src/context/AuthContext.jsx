import React, { createContext, useState, useContext, useEffect } from 'react';
import { supabase, getCurrentUser, getSession, signOut } from '../utils/supabaseClient';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check active session
    const checkSession = async () => {
      try {
        setLoading(true);
        const { data: sessionData } = await getSession();
        setSession(sessionData.session);
        
        if (sessionData?.session) {
          const { data: userData } = await getCurrentUser();
          setUser(userData?.user || null);
        }
      } catch (error) {
        console.error('Error checking session:', error);
      } finally {
        setLoading(false);
      }
    };

    checkSession();

    // Listen for auth changes
    const { data: authListener } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        setSession(session);
        setUser(session?.user || null);
        setLoading(false);
      }
    );

    return () => {
      if (authListener?.subscription) {
        authListener.subscription.unsubscribe();
      }
    };
  }, []);

  // Logout function
  const logout = async () => {
    try {
      const { error } = await signOut();
      if (error) throw error;
      
      // Clear user and session state
      setUser(null);
      setSession(null);
      
      return { error: null };
    } catch (error) {
      console.error('Error logging out:', error);
      return { error };
    }
  };

  const value = {
    user,
    session,
    loading,
    logout,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext; 