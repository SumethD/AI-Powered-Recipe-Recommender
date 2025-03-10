import React, { useState, useRef, useEffect } from 'react';
import {
  Container,
  Typography,
  TextField,
  Button,
  Box,
  Paper,
  IconButton,
  CircularProgress,
  Chip,
  Alert,
  InputAdornment,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Rating,
  Card,
  CardContent,
  useTheme,
  alpha,
  Avatar,
} from '@mui/material';
import {
  Send as SendIcon,
  Delete as DeleteIcon,
  Feedback as FeedbackIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
} from '@mui/icons-material';
import { useChat } from '../context/ChatContext';
import { useUser } from '../context/UserContext';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

// Custom styles for markdown content
const markdownStyles = {
  h1: {
    fontSize: '1.8rem',
    fontWeight: 'bold',
    marginTop: '1rem',
    marginBottom: '0.5rem',
    color: '#1976d2',
  },
  h2: {
    fontSize: '1.5rem',
    fontWeight: 'bold',
    marginTop: '1rem',
    marginBottom: '0.5rem',
    color: '#1976d2',
  },
  h3: {
    fontSize: '1.2rem',
    fontWeight: 'bold',
    marginTop: '0.8rem',
    marginBottom: '0.4rem',
  },
  p: {
    marginBottom: '0.8rem',
  },
  ul: {
    marginLeft: '1.5rem',
    marginBottom: '1rem',
  },
  ol: {
    marginLeft: '1.5rem',
    marginBottom: '1rem',
  },
  li: {
    marginBottom: '0.3rem',
  },
  strong: {
    fontWeight: 'bold',
  },
  em: {
    fontStyle: 'italic',
  },
  code: {
    backgroundColor: '#f5f5f5',
    padding: '0.2rem 0.4rem',
    borderRadius: '3px',
    fontFamily: 'monospace',
  },
};

const ChatAssistant: React.FC = () => {
  const { messages, sendMessage, clearMessages, isLoading, error, submitFeedback } = useChat();
  const { user } = useUser();
  const [message, setMessage] = useState('');
  const [feedbackOpen, setFeedbackOpen] = useState(false);
  const [selectedMessageId, setSelectedMessageId] = useState<string | null>(null);
  const [rating, setRating] = useState<number | null>(null);
  const [feedbackText, setFeedbackText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const theme = useTheme();

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async () => {
    if (message.trim() === '') return;
    
    try {
      await sendMessage(message);
      setMessage('');
    } catch (err) {
      console.error('Error sending message:', err);
      // Error is handled in the ChatContext
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleOpenFeedback = (messageId: string) => {
    setSelectedMessageId(messageId);
    setRating(null);
    setFeedbackText('');
    setFeedbackOpen(true);
  };

  const handleCloseFeedback = () => {
    setFeedbackOpen(false);
  };

  const handleSubmitFeedback = async () => {
    if (!selectedMessageId || rating === null) {
      return;
    }
    
    try {
      await submitFeedback(selectedMessageId, {
        rating,
        comment: feedbackText,
      });
      
      handleCloseFeedback();
    } catch (err) {
      console.error('Error submitting feedback:', err);
      // Error is handled in the ChatContext
    }
  };

  const handleClearChat = () => {
    if (window.confirm('Are you sure you want to clear all messages?')) {
      clearMessages();
    }
  };

  const suggestedQuestions = [
    "How can I make a quick dinner with chicken and vegetables?",
    "What are some healthy substitutes for butter in baking?",
    "How do I make a vegetarian version of lasagna?",
    "What's a good recipe for a beginner cook?",
    "How can I reduce the sodium in my cooking?",
    "What are some gluten-free alternatives to pasta?",
  ];

  return (
    <Container maxWidth="md" sx={{ pb: 4 }}>
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 700, color: theme.palette.primary.main }}>
          AI Recipe Assistant
        </Typography>
        <Typography variant="body1" paragraph sx={{ maxWidth: '700px', mx: 'auto', color: theme.palette.text.secondary }}>
          Ask questions about recipes, cooking techniques, ingredient substitutions, or any other food-related topics.
        </Typography>
      </Box>

      {/* Suggested Questions */}
      {messages.length === 0 && (
        <Card variant="outlined" sx={{ mb: 4, borderColor: alpha(theme.palette.primary.main, 0.2), bgcolor: alpha(theme.palette.primary.main, 0.03) }}>
          <CardContent>
            <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600, color: theme.palette.primary.main }}>
              Suggested Questions:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {suggestedQuestions.map((question) => (
                <Chip
                  key={question}
                  label={question}
                  onClick={() => {
                    setMessage(question);
                    // Optional: automatically send the message
                    // sendMessage(question);
                  }}
                  clickable
                  sx={{ 
                    borderRadius: '16px',
                    py: 2.5,
                    bgcolor: alpha(theme.palette.primary.main, 0.1),
                    color: theme.palette.primary.dark,
                    fontWeight: 500,
                    '&:hover': {
                      bgcolor: alpha(theme.palette.primary.main, 0.2),
                    }
                  }}
                />
              ))}
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Chat Messages */}
      <Paper 
        elevation={0} 
        variant="outlined"
        sx={{ 
          p: 3, 
          mb: 3, 
          minHeight: '400px', 
          maxHeight: '60vh', 
          overflow: 'auto',
          borderRadius: 3,
          borderColor: theme.palette.divider,
        }}
      >
        {messages.length === 0 ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', minHeight: '300px', flexDirection: 'column' }}>
            <BotIcon sx={{ fontSize: 60, color: alpha(theme.palette.primary.main, 0.2), mb: 2 }} />
            <Typography variant="body1" color="text.secondary" align="center">
              Ask any cooking or recipe-related question to get started.
            </Typography>
          </Box>
        ) : (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            {messages.map((msg) => (
              <Box
                key={msg.id}
                sx={{
                  display: 'flex',
                  justifyContent: msg.isUser ? 'flex-end' : 'flex-start',
                  position: 'relative',
                }}
              >
                {!msg.isUser && (
                  <Avatar 
                    sx={{ 
                      bgcolor: theme.palette.primary.main, 
                      width: 36, 
                      height: 36, 
                      mr: 1.5,
                      mt: 0.5
                    }}
                  >
                    <BotIcon fontSize="small" />
                  </Avatar>
                )}
                
                <Paper
                  elevation={0}
                  sx={{
                    p: 2,
                    maxWidth: '85%',
                    bgcolor: msg.isUser 
                      ? alpha(theme.palette.primary.main, 0.9)
                      : alpha(theme.palette.background.paper, 1),
                    color: msg.isUser ? 'white' : 'text.primary',
                    borderRadius: msg.isUser ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
                    position: 'relative',
                    border: msg.isUser ? 'none' : `1px solid ${theme.palette.divider}`,
                    boxShadow: msg.isUser 
                      ? `0 2px 8px ${alpha(theme.palette.primary.main, 0.3)}`
                      : `0 2px 8px ${alpha(theme.palette.common.black, 0.05)}`,
                  }}
                >
                  {msg.isUser ? (
                    <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                      {msg.content}
                    </Typography>
                  ) : (
                    <Box sx={{ color: 'text.primary' }}>
                      <ReactMarkdown 
                        remarkPlugins={[remarkGfm]}
                        components={{
                          h1: ({children}) => <Typography component="h1" variant="h4" sx={markdownStyles.h1}>{children}</Typography>,
                          h2: ({children}) => <Typography component="h2" variant="h5" sx={markdownStyles.h2}>{children}</Typography>,
                          h3: ({children}) => <Typography component="h3" variant="h6" sx={markdownStyles.h3}>{children}</Typography>,
                          p: ({children}) => <Typography component="p" variant="body1" sx={markdownStyles.p}>{children}</Typography>,
                          ul: ({children}) => <ul style={markdownStyles.ul}>{children}</ul>,
                          ol: ({children}) => <ol style={markdownStyles.ol}>{children}</ol>,
                          li: ({children}) => <li style={markdownStyles.li}>{children}</li>,
                          strong: ({children}) => <strong style={markdownStyles.strong}>{children}</strong>,
                          em: ({children}) => <em style={markdownStyles.em}>{children}</em>,
                          code: ({children}) => <code style={markdownStyles.code}>{children}</code>,
                        }}
                      >
                        {msg.content}
                      </ReactMarkdown>
                    </Box>
                  )}
                  
                  {!msg.isUser && user && (
                    <IconButton
                      size="small"
                      sx={{
                        position: 'absolute',
                        bottom: 2,
                        right: 2,
                        opacity: 0.6,
                        '&:hover': { opacity: 1 },
                      }}
                      onClick={() => handleOpenFeedback(msg.id)}
                    >
                      <FeedbackIcon fontSize="small" />
                    </IconButton>
                  )}
                </Paper>
                
                {msg.isUser && (
                  <Avatar 
                    sx={{ 
                      bgcolor: theme.palette.secondary.main, 
                      width: 36, 
                      height: 36, 
                      ml: 1.5,
                      mt: 0.5
                    }}
                  >
                    <PersonIcon fontSize="small" />
                  </Avatar>
                )}
              </Box>
            ))}
            <div ref={messagesEndRef} />
          </Box>
        )}
        
        {/* Loading indicator */}
        {isLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
            <CircularProgress size={24} />
          </Box>
        )}
        
        {/* Error message */}
        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
      </Paper>

      {/* Message Input */}
      <Box sx={{ display: 'flex', gap: 1, mb: 4 }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Ask a question about cooking or recipes..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          multiline
          maxRows={4}
          disabled={isLoading}
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: '24px',
              pr: 1,
              pl: 2,
              py: 1,
              backgroundColor: theme.palette.background.paper,
            }
          }}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  onClick={handleSendMessage}
                  disabled={isLoading || message.trim() === ''}
                  color="primary"
                  sx={{ 
                    bgcolor: theme.palette.primary.main,
                    color: 'white',
                    '&:hover': {
                      bgcolor: theme.palette.primary.dark,
                    },
                    '&.Mui-disabled': {
                      bgcolor: alpha(theme.palette.primary.main, 0.3),
                      color: 'white',
                    }
                  }}
                >
                  <SendIcon />
                </IconButton>
              </InputAdornment>
            ),
          }}
        />
        
        <Button
          variant="outlined"
          color="error"
          onClick={handleClearChat}
          disabled={messages.length === 0 || isLoading}
          startIcon={<DeleteIcon />}
          sx={{ 
            borderRadius: '24px',
            px: 3,
            whiteSpace: 'nowrap',
            display: { xs: 'none', sm: 'flex' }
          }}
        >
          Clear
        </Button>
        
        <IconButton
          color="error"
          onClick={handleClearChat}
          disabled={messages.length === 0 || isLoading}
          sx={{ 
            display: { xs: 'flex', sm: 'none' },
            border: `1px solid ${theme.palette.error.main}`,
            '&:hover': {
              bgcolor: alpha(theme.palette.error.main, 0.1),
            }
          }}
        >
          <DeleteIcon />
        </IconButton>
      </Box>

      {/* Feedback Dialog */}
      <Dialog 
        open={feedbackOpen} 
        onClose={handleCloseFeedback}
        PaperProps={{
          sx: {
            borderRadius: 3,
            maxWidth: '400px',
            width: '100%',
          }
        }}
      >
        <DialogTitle sx={{ pb: 1, pt: 3, textAlign: 'center' }}>
          <Typography variant="h5" sx={{ fontWeight: 600 }}>
            Rate this response
          </Typography>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, minWidth: '300px', p: 1 }}>
            <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
              <Rating
                value={rating}
                onChange={(_, newValue) => setRating(newValue)}
                size="large"
                sx={{
                  '& .MuiRating-iconFilled': {
                    color: theme.palette.primary.main,
                  },
                }}
              />
            </Box>
            
            <TextField
              label="Additional feedback (optional)"
              multiline
              rows={4}
              fullWidth
              value={feedbackText}
              onChange={(e) => setFeedbackText(e.target.value)}
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                }
              }}
            />
          </Box>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button 
            onClick={handleCloseFeedback}
            variant="outlined"
            sx={{ borderRadius: 2, px: 3 }}
          >
            Cancel
          </Button>
          <Button 
            onClick={handleSubmitFeedback} 
            color="primary"
            variant="contained"
            disabled={rating === null}
            sx={{ borderRadius: 2, px: 3 }}
          >
            Submit
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ChatAssistant; 