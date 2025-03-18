import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';
import { UserProvider } from './context/UserContext';

// Mock the AuthContext
jest.mock('./context/AuthContext', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  useAuth: () => ({
    user: null,
    loading: false,
    logout: jest.fn(),
    isAuthenticated: false
  })
}));

// Mock the RecipeContext
jest.mock('./context/RecipeContext', () => ({
  RecipeProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  useRecipes: () => ({})
}));

// Mock the ChatContext
jest.mock('./context/ChatContext', () => ({
  ChatProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  useChat: () => ({})
}));

// Mock the ShoppingListContext
jest.mock('./context/ShoppingListContext', () => ({
  ShoppingListProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  useShoppingList: () => ({
    selectedRecipes: []
  })
}));

test('renders without crashing', () => {
  render(
    <UserProvider>
      <App />
    </UserProvider>
  );
  
  // Just check if the app renders without crashing
  // Use getByTestId instead of direct DOM access
  const appElement = screen.getByRole('main');
  expect(appElement).toBeInTheDocument();
});
