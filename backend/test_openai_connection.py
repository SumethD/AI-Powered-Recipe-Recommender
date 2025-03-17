#!/usr/bin/env python
import os
import sys
from dotenv import load_dotenv
import requests
import json

# Load environment variables from .env file
load_dotenv()

# Get OpenAI API key
api_key = os.environ.get('OPENAI_API_KEY')

def test_openai_connection():
    """Test the connection to OpenAI API."""
    if not api_key:
        print("ERROR: OPENAI_API_KEY not found in environment variables.")
        print("Make sure you have a .env file in the backend directory with your OpenAI API key.")
        print("Example: OPENAI_API_KEY=sk-your-key-here")
        return False
        
    # Simple API call to test connection
    try:
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are a helpful assistant.'
                    },
                    {
                        'role': 'user',
                        'content': 'Hello! This is a test message to verify API connectivity.'
                    }
                ],
                'max_tokens': 50
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ OpenAI API connection successful!")
            print("Response sample:", result['choices'][0]['message']['content'][:50] + "...")
            return True
        else:
            print(f"❌ Error connecting to OpenAI API. Status code: {response.status_code}")
            print("Response:", response.text)
            return False
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing OpenAI API connection...")
    success = test_openai_connection()
    if success:
        print("\nYour environment is correctly set up for AI-powered ingredient consolidation!")
    else:
        print("\nPlease check your OpenAI API key and try again.")
    
    sys.exit(0 if success else 1) 