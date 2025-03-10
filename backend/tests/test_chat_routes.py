import unittest
import json
import sys
import os
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

class TestChatRoutes(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('routes.chat_routes.ask_openai')
    def test_ask_endpoint(self, mock_ask_openai):
        # Mock the service function
        mock_response = "Here's a recipe for pasta carbonara..."
        mock_ask_openai.return_value = mock_response

        # Make the request
        response = self.app.post('/api/chat/ask',
                                json={
                                    'question': 'How do I make pasta carbonara?',
                                    'user_id': 'user123',
                                    'model': 'gpt-4o-mini',
                                    'context': '{"recipeId": 123}'
                                })
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['response'], mock_response)
        
        # Check that the service was called with the right parameters
        mock_ask_openai.assert_called_once()
        args, kwargs = mock_ask_openai.call_args
        self.assertEqual(args[0], 'How do I make pasta carbonara?')
        self.assertEqual(kwargs.get('user_id'), 'user123')
        self.assertEqual(kwargs.get('model'), 'gpt-4o-mini')
        self.assertEqual(kwargs.get('context'), '{"recipeId": 123}')

    @patch('routes.chat_routes.ask_openai')
    def test_ask_endpoint_missing_question(self, mock_ask_openai):
        # Make the request without a question
        response = self.app.post('/api/chat/ask',
                                json={
                                    'user_id': 'user123',
                                    'model': 'gpt-4o-mini'
                                })
        
        # Check the response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        
        # Check that the service was not called
        mock_ask_openai.assert_not_called()

    @patch('routes.chat_routes.ask_openai')
    def test_ask_endpoint_with_user_preferences(self, mock_ask_openai):
        # Mock the service function and user preferences
        mock_response = "Here's a vegetarian recipe for pasta..."
        mock_ask_openai.return_value = mock_response

        # Mock the get_user_preferences function
        with patch('routes.chat_routes.get_user_preferences') as mock_get_prefs:
            mock_get_prefs.return_value = {
                'diets': ['vegetarian'],
                'intolerances': ['gluten'],
                'cuisines': ['italian']
            }

            # Make the request
            response = self.app.post('/api/chat/ask',
                                    json={
                                        'question': 'How do I make pasta?',
                                        'user_id': 'user123',
                                        'model': 'gpt-4o-mini'
                                    })
            
            # Check the response
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data['response'], mock_response)
            
            # Check that the service was called with the right parameters
            mock_ask_openai.assert_called_once()
            mock_get_prefs.assert_called_once_with('user123')

    def test_feedback_endpoint(self):
        # Make the request
        response = self.app.post('/api/chat/feedback',
                                json={
                                    'user_id': 'user123',
                                    'question': 'How do I make pasta?',
                                    'response': 'Here is a recipe...',
                                    'rating': 5,
                                    'feedback': 'Great response!'
                                })
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

    def test_feedback_endpoint_missing_data(self):
        # Make the request without required fields
        response = self.app.post('/api/chat/feedback',
                                json={
                                    'user_id': 'user123'
                                })
        
        # Check the response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

if __name__ == '__main__':
    unittest.main() 