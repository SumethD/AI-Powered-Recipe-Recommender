import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { RecipeProvider } from './context/RecipeContext';
import { ChatProvider } from './context/ChatContext';
import { UserProvider } from './context/UserContext';
import { ShoppingListProvider } from './context/ShoppingListContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import { testConnection } from './services/supabase';
import ErrorBoundary from './components/ErrorBoundary';

// Import fonts
import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';
import '@fontsource/poppins/300.css';
import '@fontsource/poppins/400.css';
import '@fontsource/poppins/500.css';
import '@fontsource/poppins/600.css';
import '@fontsource/poppins/700.css';
import '@fontsource/inter/300.css';
import '@fontsource/inter/400.css';
import '@fontsource/inter/500.css';
import '@fontsource/inter/600.css';
import '@fontsource/inter/700.css';

// Import custom theme
import theme from './theme';

// Import layout components
import Header from './components/layout/Header';
import Footer from './components/layout/Footer';

// Import pages
import Home from './pages/Home';
import RecipeSearch from './pages/RecipeSearch';
import RecipeDetails from './pages/RecipeDetails';
import ChatAssistant from './pages/ChatAssistant';
import UserProfile from './pages/UserProfile';
import Favorites from './pages/Favorites';
import NotFound from './pages/NotFound';
import TestRecipeFlow from './components/TestRecipeFlow';
import ApiTest from './components/ApiTest';
import VideoToRecipe from './pages/VideoToRecipe.jsx';
import ApiDebug from './pages/ApiDebug.jsx';
import ShoppingList from './pages/ShoppingList.jsx';
import Login from './pages/Login';
import Signup from './pages/Signup';

// Protected Route component to restrict access to authenticated users
function ProtectedRoute({ children }: { children: JSX.Element }) {
  const { user, loading } = useAuth();
  if (loading) return <div>Loading...</div>;
  return user ? children : <Navigate to="/login" />;
}

// Public Route component to redirect logged-in users away from login/signup
function PublicRoute({ children }: { children: JSX.Element }) {
  const { user, loading } = useAuth();
  if (loading) return <div>Loading...</div>;
  return user ? <Navigate to="/" /> : children;
}

function AppContent() {
  // Test Supabase connection on app load
  useEffect(() => {
    const checkConnection = async () => {
      await testConnection();
    };
    checkConnection();
  }, []);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <UserProvider>
          <RecipeProvider>
            <ChatProvider>
              <ShoppingListProvider>
                <div className="App">
                  <Header />
                  <main style={{ minHeight: 'calc(100vh - 128px)', padding: '24px' }}>
                    <Routes>
                      {/* Public routes */}
                      <Route path="/" element={<Home />} />
                      <Route path="/search" element={<RecipeSearch />} />
                      <Route path="/recipe/:id" element={<RecipeDetails />} />
                      <Route path="/chat" element={<ChatAssistant />} />
                      <Route path="/video-to-recipe" element={<VideoToRecipe />} />
                      <Route path="/api-debug" element={<ApiDebug />} />
                      <Route path="/test-recipe-flow" element={<TestRecipeFlow />} />
                      <Route path="/api-test" element={<ApiTest />} />
                      <Route path="/shopping-list" element={<ShoppingList />} />

                      {/* Auth routes */}
                      <Route
                        path="/login"
                        element={
                          <PublicRoute>
                            <Login />
                          </PublicRoute>
                        }
                      />
                      <Route
                        path="/signup"
                        element={
                          <PublicRoute>
                            <Signup />
                          </PublicRoute>
                        }
                      />

                      {/* Protected routes */}
                      <Route
                        path="/profile"
                        element={
                          <ProtectedRoute>
                            <UserProfile />
                          </ProtectedRoute>
                        }
                      />
                      <Route
                        path="/favorites"
                        element={
                          <ProtectedRoute>
                            <Favorites />
                          </ProtectedRoute>
                        }
                      />

                      {/* Fallback route */}
                      <Route path="*" element={<NotFound />} />
                    </Routes>
                  </main>
                  <Footer />
                </div>
              </ShoppingListProvider>
            </ChatProvider>
          </RecipeProvider>
        </UserProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}