import requests
import json

# Test with simplified recipe data
data = {
    'recipes': [
        {
            'id': 1,
            'extendedIngredients': [
                {'name': 'olive oil', 'amount': 2, 'unit': 'tbsp'},
                {'name': 'onion', 'amount': 1, 'unit': ''}
            ]
        }
    ]
}

# Send request to API
response = requests.post('http://localhost:5000/api/shopping-list/generate', json=data)

# Print response
print('Response status:', response.status_code)
print('API Response:')
print(json.dumps(response.json(), indent=2)) 