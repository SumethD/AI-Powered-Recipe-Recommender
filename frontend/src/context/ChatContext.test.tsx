import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import { ChatProvider, useChat } from './ChatContext';
import { UserProvider } from './UserContext';
import { chatApi } from '../services/api';

// Mock the API services
jest.mock('../services/api', () => ({
  chatApi: {
    askQuestion: jest.fn(),
    submitFeedback: jest.fn(),
  },
}));

// Test component that uses the ChatContext
const TestComponent = () => {
  const { 
    messages, 
    isLoading, 
    error, 
    sendMessage,
    clearMessages,
    submitFeedback
  } = useChat();

  return (
    <div>
      <div data-testid="loading">{isLoading ? 'Loading...' : 'Not loading'}</div>
      <div data-testid="error">{error || 'No error'}</div>
      <div data-testid="messages-count">{messages.length}</div>
      <div data-testid="messages">
        {messages.map((msg, index) => (
          <div key={msg.id} data-testid={`message-${index}`}>
            {msg.isUser ? 'User: ' : 'AI: '}{msg.content}
          </div>
        ))}
      </div>
      <button data-testid="send-message" onClick={() => sendMessage('Hello, AI!')}>
        Send Message
      </button>
      <button data-testid="clear-messages" onClick={() => clearMessages()}>
        Clear Messages
      </button>
      <button 
        data-testid="submit-feedback" 
        onClick={() => {
          if (messages.length >= 2) {
            submitFeedback(messages[0].id, { rating: 5, comment: 'Great response!' });
          }
        }}
      >
        Submit Feedback
      </button>
    </div>
  );
};

// Wrap the test component with providers
const renderWithProviders = () => {
  return render(
    <UserProvider>
      <ChatProvider>
        <TestComponent />
      </ChatProvider>
    </UserProvider>
  );
};

describe('ChatContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('should send a message and receive a response', async () => {
    // Mock the API response
    (chatApi.askQuestion as jest.Mock).mockResolvedValue({
      data: { response: 'Hello, human!' }
    });

    renderWithProviders();

    // Initial state
    expect(screen.getByTestId('loading')).toHaveTextContent('Not loading');
    expect(screen.getByTestId('messages-count')).toHaveTextContent('0');

    // Click the send message button
    await act(async () => {
      screen.getByTestId('send-message').click();
    });

    // Should show loading state
    expect(screen.getByTestId('loading')).toHaveTextContent('Loading...');

    // Wait for the API call to resolve
    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('Not loading');
    });

    // Should have two messages (user message and AI response)
    expect(screen.getByTestId('messages-count')).toHaveTextContent('2');
    expect(screen.getByTestId('message-0')).toHaveTextContent('User: Hello, AI!');
    expect(screen.getByTestId('message-1')).toHaveTextContent('AI: Hello, human!');
    expect(chatApi.askQuestion).toHaveBeenCalledWith('Hello, AI!', undefined, 'gpt-4o-mini', undefined);
  });

  test('should show error state when API call fails', async () => {
    // Mock the API error
    (chatApi.askQuestion as jest.Mock).mockRejectedValue(new Error('API error'));

    renderWithProviders();

    // Initial state
    expect(screen.getByTestId('error')).toHaveTextContent('No error');

    // Click the send message button
    await act(async () => {
      screen.getByTestId('send-message').click();
    });

    // Wait for the API call to reject
    await waitFor(() => {
      expect(screen.getByTestId('error')).toHaveTextContent('Failed to get response from AI');
    });
  });

  test('should clear messages', async () => {
    // Mock the API response
    (chatApi.askQuestion as jest.Mock).mockResolvedValue({
      data: { response: 'Hello, human!' }
    });

    renderWithProviders();

    // Send a message first
    await act(async () => {
      screen.getByTestId('send-message').click();
    });

    // Wait for the API call to resolve
    await waitFor(() => {
      expect(screen.getByTestId('messages-count')).toHaveTextContent('2');
    });

    // Clear messages
    await act(async () => {
      screen.getByTestId('clear-messages').click();
    });

    // Should have no messages
    expect(screen.getByTestId('messages-count')).toHaveTextContent('0');
  });

  test('should submit feedback', async () => {
    // Mock the API responses
    (chatApi.askQuestion as jest.Mock).mockResolvedValue({
      data: { response: 'Hello, human!' }
    });
    (chatApi.submitFeedback as jest.Mock).mockResolvedValue({
      data: { success: true }
    });

    renderWithProviders();

    // Send a message first
    await act(async () => {
      screen.getByTestId('send-message').click();
    });

    // Wait for the API call to resolve
    await waitFor(() => {
      expect(screen.getByTestId('messages-count')).toHaveTextContent('2');
    });

    // Submit feedback
    await act(async () => {
      screen.getByTestId('submit-feedback').click();
    });

    // Should call the submitFeedback API
    await waitFor(() => {
      expect(chatApi.submitFeedback).toHaveBeenCalled();
    });
  });
}); 