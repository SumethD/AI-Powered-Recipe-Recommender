import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import { UserProvider, useUser } from './UserContext';
import { userApi } from '../services/api';

// Mock the API services
jest.mock('../services/api', () => ({
  userApi: {
    getPreferences: jest.fn(),
    updatePreferences: jest.fn(),
  },
}));

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: jest.fn((key: string) => store[key] || null),
    setItem: jest.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: jest.fn((key: string) => {
      delete store[key];
    }),
    clear: jest.fn(() => {
      store = {};
    }),
  };
})();
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

// Test component that uses the UserContext
const TestComponent = () => {
  const { 
    user, 
    isLoading, 
    error, 
    login,
    logout,
    updatePreferences
  } = useUser();

  return (
    <div>
      <div data-testid="loading">{isLoading ? 'Loading...' : 'Not loading'}</div>
      <div data-testid="error">{error || 'No error'}</div>
      <div data-testid="user-status">{user ? 'Logged in' : 'Not logged in'}</div>
      {user && (
        <div data-testid="user-id">{user.id}</div>
      )}
      <button data-testid="login" onClick={() => login('test-user-123')}>
        Login
      </button>
      <button data-testid="logout" onClick={() => logout()}>
        Logout
      </button>
      <button 
        data-testid="update-preferences" 
        onClick={() => updatePreferences({ diets: ['vegetarian'] })}
      >
        Update Preferences
      </button>
    </div>
  );
};

// Wrap the test component with providers
const renderWithProviders = () => {
  return render(
    <UserProvider>
      <TestComponent />
    </UserProvider>
  );
};

describe('UserContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.clear();
  });

  test('should login a user', async () => {
    // Mock the API response
    (userApi.getPreferences as jest.Mock).mockResolvedValue({
      data: {
        diets: ['vegetarian'],
        intolerances: ['gluten'],
        cuisines: ['italian'],
      }
    });

    renderWithProviders();

    // Initial state
    expect(screen.getByTestId('user-status')).toHaveTextContent('Not logged in');

    // Click the login button
    await act(async () => {
      screen.getByTestId('login').click();
    });

    // Should be logged in
    expect(screen.getByTestId('user-status')).toHaveTextContent('Logged in');
    expect(screen.getByTestId('user-id')).toHaveTextContent('test-user-123');
    expect(localStorageMock.setItem).toHaveBeenCalledWith('userId', 'test-user-123');
    expect(userApi.getPreferences).toHaveBeenCalledWith('test-user-123');
  });

  test('should logout a user', async () => {
    renderWithProviders();

    // Login first
    await act(async () => {
      screen.getByTestId('login').click();
    });

    // Should be logged in
    expect(screen.getByTestId('user-status')).toHaveTextContent('Logged in');

    // Click the logout button
    await act(async () => {
      screen.getByTestId('logout').click();
    });

    // Should be logged out
    expect(screen.getByTestId('user-status')).toHaveTextContent('Not logged in');
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('userId');
  });

  test('should update user preferences', async () => {
    // Mock the API response
    (userApi.updatePreferences as jest.Mock).mockResolvedValue({
      data: { success: true }
    });

    renderWithProviders();

    // Login first
    await act(async () => {
      screen.getByTestId('login').click();
    });

    // Should be logged in
    expect(screen.getByTestId('user-status')).toHaveTextContent('Logged in');

    // Click the update preferences button
    await act(async () => {
      screen.getByTestId('update-preferences').click();
    });

    // Should call the updatePreferences API
    expect(userApi.updatePreferences).toHaveBeenCalled();
    const updateCall = (userApi.updatePreferences as jest.Mock).mock.calls[0];
    expect(updateCall[0]).toBe('test-user-123');
    expect(updateCall[1].diets).toContain('vegetarian');
  });

  test('should load user from localStorage on mount', async () => {
    // Set user ID in localStorage
    localStorageMock.setItem('userId', 'saved-user-123');
    
    // Mock the API response
    (userApi.getPreferences as jest.Mock).mockResolvedValue({
      data: {
        diets: ['vegetarian'],
        intolerances: ['gluten'],
        cuisines: ['italian'],
      }
    });

    renderWithProviders();

    // Should automatically login
    await waitFor(() => {
      expect(screen.getByTestId('user-status')).toHaveTextContent('Logged in');
    });
    expect(screen.getByTestId('user-id')).toHaveTextContent('saved-user-123');
    expect(userApi.getPreferences).toHaveBeenCalledWith('saved-user-123');
  });
}); 