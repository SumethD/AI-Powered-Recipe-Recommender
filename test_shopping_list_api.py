import requests
import json

def test_shopping_list_api():
    url = 'http://localhost:5000/api/shopping-list/generate'
    data = {
        'recipes': [
            {
                'id': 1,
                'extendedIngredients': [
                    {
                        'name': 'olive oil',
                        'amount': 2,
                        'unit': 'tbsp'
                    },
                    {
                        'name': 'onion',
                        'amount': 1,
                        'unit': ''
                    }
                ]
            }
        ]
    }
    
    response = requests.post(url, json=data)
    
    print(f"Status Code: {response.status_code}")
    if response.ok:
        result = response.json()
        print(json.dumps(result, indent=2))
        print(f"Number of items in shopping list: {len(result.get('shopping_list', []))}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_shopping_list_api() 