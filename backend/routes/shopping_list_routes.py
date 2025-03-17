import os
import json
import re
import requests
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv

from utils.ingredient_parser import parse_ingredient, normalize_ingredient_name, normalize_unit, categorize_ingredient

# Load environment variables from .env file
load_dotenv()

shopping_list_bp = Blueprint('shopping_list', __name__)

# Get OpenAI API key from environment variable
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY') 