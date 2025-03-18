import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { RecipeProvider } from './context/RecipeContext';
import { ChatProvider } from './context/ChatContext';
import { UserProvider } from './context/UserContext';
import { ShoppingListProvider } from './context/ShoppingListContext';
import { AuthProvider } from './context/AuthContext';
import ErrorBoundary from './components/ErrorBoundary';
// @ts-ignore
import AuthGuard from './components/auth/AuthGuard.jsx';

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
// @ts-ignore
import VideoToRecipe from './pages/VideoToRecipe.jsx';
// @ts-ignore
import ApiDebug from './pages/ApiDebug.jsx';
// @ts-ignore
import ShoppingList from './pages/ShoppingList.jsx';
// @ts-ignore
import Login from './pages/Login.jsx';
// @ts-ignore
import Register from './pages/Register.jsx';

function App(): JSX.Element {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <ErrorBoundary>
        <AuthProvider>
          <UserProvider>
            <RecipeProvider>
              <ChatProvider>
                {/* @ts-ignore - Ignore TS error for ShoppingListProvider */}
                <ShoppingListProvider>
                  <Router>
                    <div className="App">
                      <Header />
                      <main style={{ minHeight: 'calc(100vh - 128px)', padding: '24px' }}>
                        <Routes>
                          <Route path="/" element={<Home />} />
                          <Route path="/search" element={<RecipeSearch />} />
                          <Route path="/recipe/:id" element={<RecipeDetails />} />
                          <Route path="/chat" element={<ChatAssistant />} />
                          <Route 
                            path="/profile" 
                            element={
                              <AuthGuard>
                                <UserProfile />
                              </AuthGuard>
                            } 
                          />
                          <Route 
                            path="/favorites" 
                            element={
                              <AuthGuard>
                                <Favorites />
                              </AuthGuard>
                            } 
                          />
                          <Route path="/video-to-recipe" element={<VideoToRecipe />} />
                          <Route 
                            path="/shopping-list" 
                            element={
                              <AuthGuard>
                                <ShoppingList />
                              </AuthGuard>
                            } 
                          />
                          <Route path="/api-debug" element={<ApiDebug />} />
                          <Route path="/test-recipe-flow" element={<TestRecipeFlow />} />
                          <Route path="/api-test" element={<ApiTest />} />
                          <Route path="/login" element={<Login />} />
                          <Route path="/register" element={<Register />} />
                          <Route path="*" element={<NotFound />} />
                        </Routes>
                      </main>
                      <Footer />
                    </div>
                  </Router>
                </ShoppingListProvider>
              </ChatProvider>
            </RecipeProvider>
          </UserProvider>
        </AuthProvider>
      </ErrorBoundary>
    </ThemeProvider>
  );
}

export default App;
