import unittest
import json
import sys
import os
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

class TestRecipeRoutes(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('routes.recipe_routes.get_recipes_by_ingredients')
    def test_find_recipes_by_ingredients(self, mock_get_recipes):
        # Mock the service function
        mock_recipes = [
            {'id': 1, 'title': 'Chicken Rice', 'image': 'chicken.jpg'},
            {'id': 2, 'title': 'Beef Rice', 'image': 'beef.jpg'}
        ]
        mock_get_recipes.return_value = mock_recipes

        # Make the request
        response = self.app.post('/api/recipes/by-ingredients',
                                json={'ingredients': ['chicken', 'rice']})
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['title'], 'Chicken Rice')
        
        # Check that the service was called with the right parameters
        mock_get_recipes.assert_called_once_with(['chicken', 'rice'])

    @patch('routes.recipe_routes.search_recipes')
    def test_search_recipes_endpoint(self, mock_search):
        # Mock the service function
        mock_recipes = [
            {'id': 1, 'title': 'Pasta Carbonara', 'image': 'pasta.jpg'},
            {'id': 2, 'title': 'Pasta Bolognese', 'image': 'pasta2.jpg'}
        ]
        mock_search.return_value = mock_recipes

        # Make the request
        response = self.app.get('/api/recipes/search?query=pasta&cuisine=italian')
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['title'], 'Pasta Carbonara')
        
        # Check that the service was called with the right parameters
        mock_search.assert_called_once_with('pasta', 'italian', '', '')

    @patch('routes.recipe_routes.get_recipe_details')
    def test_get_recipe(self, mock_get_details):
        # Mock the service function
        mock_recipe = {
            'id': 123,
            'title': 'Pasta Carbonara',
            'image': 'pasta.jpg',
            'instructions': 'Cook the pasta...'
        }
        mock_get_details.return_value = mock_recipe

        # Make the request
        response = self.app.get('/api/recipes/123')
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['id'], 123)
        self.assertEqual(data['title'], 'Pasta Carbonara')
        
        # Check that the service was called with the right parameters
        mock_get_details.assert_called_once_with(123)

    @patch('routes.recipe_routes.get_random_recipes')
    def test_get_random_recipes_endpoint(self, mock_random):
        # Mock the service function
        mock_recipes = [
            {'id': 1, 'title': 'Random Recipe 1', 'image': 'random1.jpg'},
            {'id': 2, 'title': 'Random Recipe 2', 'image': 'random2.jpg'}
        ]
        mock_random.return_value = mock_recipes

        # Make the request
        response = self.app.get('/api/recipes/random?tags=vegetarian')
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['title'], 'Random Recipe 1')
        
        # Check that the service was called with the right parameters
        mock_random.assert_called_once_with('vegetarian')

    @patch('routes.recipe_routes.get_user_favorites')
    def test_get_favorites_endpoint(self, mock_favorites):
        # Mock the service function
        mock_recipes = [
            {'id': 1, 'title': 'Favorite 1', 'image': 'fav1.jpg'},
            {'id': 2, 'title': 'Favorite 2', 'image': 'fav2.jpg'}
        ]
        mock_favorites.return_value = mock_recipes

        # Make the request
        response = self.app.get('/api/recipes/favorites?user_id=user123')
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['title'], 'Favorite 1')
        
        # Check that the service was called with the right parameters
        mock_favorites.assert_called_once()
        args, kwargs = mock_favorites.call_args
        self.assertEqual(args[0], 'user123')

    @patch('routes.recipe_routes.add_favorite')
    def test_add_favorite_endpoint(self, mock_add):
        # Mock the service function
        mock_add.return_value = True

        # Make the request
        recipe = {'id': 123, 'title': 'Test Recipe', 'image': 'test.jpg'}
        response = self.app.post('/api/recipes/favorites',
                                json={'user_id': 'user123', 'recipe': recipe})
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
        # Check that the service was called with the right parameters
        mock_add.assert_called_once_with('user123', recipe)

    @patch('routes.recipe_routes.remove_favorite')
    def test_remove_favorite_endpoint(self, mock_remove):
        # Mock the service function
        mock_remove.return_value = True

        # Make the request
        response = self.app.delete('/api/recipes/favorites/123?user_id=user123')
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
        # Check that the service was called with the right parameters
        mock_remove.assert_called_once_with('user123', 123)

if __name__ == '__main__':
    unittest.main() 