import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { RecipeProvider } from './context/RecipeContext';
import { ChatProvider } from './context/ChatContext';
import { UserProvider } from './context/UserContext';
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

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <UserProvider>
        <RecipeProvider>
          <ChatProvider>
            <Router>
              <div className="App">
                <Header />
                <main style={{ minHeight: 'calc(100vh - 128px)', padding: '24px' }}>
                  <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/search" element={<RecipeSearch />} />
                    <Route path="/recipe/:id" element={<RecipeDetails />} />
                    <Route path="/chat" element={<ChatAssistant />} />
                    <Route path="/profile" element={<UserProfile />} />
                    <Route path="/favorites" element={<Favorites />} />
                    <Route path="/test-recipe-flow" element={<TestRecipeFlow />} />
                    <Route path="/api-test" element={<ApiTest />} />
                    <Route path="*" element={<NotFound />} />
                  </Routes>
                </main>
                <Footer />
              </div>
            </Router>
          </ChatProvider>
        </RecipeProvider>
      </UserProvider>
    </ThemeProvider>
  );
}

export default App;
