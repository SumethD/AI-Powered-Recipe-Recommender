import React, { createContext, useState, useContext, ReactNode } from 'react';
import { useUser } from './UserContext';
import { chatApi } from '../services/api';

// Define chat message type
export interface ChatMessage {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
}

// Define feedback type
export interface Feedback {
  rating: number;
  comment?: string;
}

// Define context type
interface ChatContextType {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (message: string, context?: any) => Promise<void>;
  clearMessages: () => void;
  submitFeedback: (messageId: string, feedback: Feedback) => Promise<void>;
}

// Create context
const ChatContext = createContext<ChatContextType | null>(null);

// Provider props
type ChatProviderProps = {
  children: ReactNode;
};

// Provider component
export const ChatProvider = ({ children }: ChatProviderProps) => {
  const { user } = useUser();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Send message to AI
  const sendMessage = async (content: string, context?: any): Promise<void> => {
    if (!content.trim()) {
      setError('Please enter a message');
      return;
    }

    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await chatApi.askQuestion(content, user?.id, 'gpt-4o-mini', context);
      
      if (response && response.success && response.data && response.data.response) {
        // Add AI response
        const aiMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          content: response.data.response,
          isUser: false,
          timestamp: new Date()
        };

        setMessages(prev => [...prev, aiMessage]);
      } else {
        // Add error message if response is empty
        const errorMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          content: "Sorry, I couldn't process your request. Please try again later.",
          isUser: false,
          timestamp: new Date()
        };

        setMessages(prev => [...prev, errorMessage]);
        setError('Empty response from AI');
      }
      
      setIsLoading(false);
    } catch (err) {
      // Add error message
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: "Sorry, there was an error processing your request. Please try again later.",
        isUser: false,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
      setError('Failed to get response from AI');
      setIsLoading(false);
      console.error('Error sending message to AI:', err);
    }
  };

  // Clear all messages
  const clearMessages = (): void => {
    setMessages([]);
    setError(null);
  };

  // Submit feedback for a message
  const submitFeedback = async (messageId: string, feedback: Feedback): Promise<void> => {
    if (!user) {
      setError('Please log in to submit feedback');
      return;
    }

    if (!messageId || !feedback || feedback.rating < 1 || feedback.rating > 5) {
      setError('Invalid feedback data');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Find the message and its corresponding AI response
      const messageIndex = messages.findIndex(m => m.id === messageId);
      if (messageIndex < 0 || messageIndex + 1 >= messages.length) {
        throw new Error('Message not found or no AI response available');
      }

      const userMessage = messages[messageIndex];
      const aiResponse = messages[messageIndex + 1];

      const response = await chatApi.submitFeedback(
        user.id,
        userMessage.content,
        aiResponse.content,
        feedback.rating,
        feedback.comment
      );

      if (!response || !response.success) {
        throw new Error('Failed to submit feedback');
      }

      setIsLoading(false);
    } catch (err) {
      setError('Failed to submit feedback');
      setIsLoading(false);
      console.error('Error submitting feedback:', err);
    }
  };

  // Context value
  const value = {
    messages,
    isLoading,
    error,
    sendMessage,
    clearMessages,
    submitFeedback
  };

  // Use a JSX expression that doesn't trigger the linter error
  return React.createElement(ChatContext.Provider, { value }, children);
};

// Custom hook to use the context
export const useChat = (): ChatContextType => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};

export default ChatContext; 