from flask import Blueprint, request, jsonify
import jwt
import os
from datetime import datetime
import logging

# Initialize logger
logger = logging.getLogger(__name__)

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# User store - in a real application, use a database
# This is just a temporary in-memory store until we connect to the database
users = {}

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        user_id = data.get('user_id')
        email = data.get('email')
        metadata = data.get('metadata', {})
        
        if not user_id or not email:
            return jsonify({
                'success': False,
                'message': 'User ID and email are required'
            }), 400
            
        # In a real application, you would store this in a database
        users[user_id] = {
            'email': email,
            'metadata': metadata,
            'created_at': datetime.now().isoformat(),
            'last_login': None
        }
        
        logger.info(f"User registered: {email}")
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Error in register: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred during registration'
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Process user login."""
    try:
        # Get authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': 'Invalid or missing authentication token'
            }), 401
        
        # Extract token
        token = auth_header.split(' ')[1]
        
        # In a production app, you would verify this token against Supabase
        # For now, we'll just extract the user ID from the request body
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'User ID is required'
            }), 400
        
        # Update user's last login time
        if user_id in users:
            users[user_id]['last_login'] = datetime.now().isoformat()
            logger.info(f"User logged in: {users[user_id]['email']}")
        else:
            # This could happen if the user was created in Supabase but not in our system
            logger.warning(f"Login for unknown user ID: {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Login processed successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in login: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred during login processing'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Process user logout."""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'User ID is required'
            }), 400
        
        # In a real application, you might update the user's session
        if user_id in users:
            logger.info(f"User logged out: {users[user_id]['email']}")
        
        return jsonify({
            'success': True,
            'message': 'Logout processed successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in logout: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred during logout processing'
        }), 500

@auth_bp.route('/verify', methods=['GET'])
def verify_token():
    """Verify a JWT token."""
    try:
        # Get authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': 'Invalid or missing authentication token'
            }), 401
        
        # Extract token
        token = auth_header.split(' ')[1]
        
        # In a real application, you would verify this token with Supabase
        # This would involve making an API call to Supabase or using their SDK
        # For now, return a success response
        return jsonify({
            'success': True,
            'message': 'Token is valid'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in verify_token: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred during token verification'
        }), 500

@auth_bp.route('/user', methods=['GET'])
def get_user():
    """Get user information."""
    try:
        # Get authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': 'Invalid or missing authentication token'
            }), 401
        
        # Extract token
        token = auth_header.split(' ')[1]
        
        # Extract user ID from query parameters
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'User ID is required'
            }), 400
        
        # Get user information
        if user_id in users:
            # Don't return sensitive information
            user_info = {
                'email': users[user_id]['email'],
                'metadata': users[user_id]['metadata'],
                'created_at': users[user_id]['created_at'],
                'last_login': users[user_id]['last_login']
            }
            
            return jsonify({
                'success': True,
                'user': user_info
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
    except Exception as e:
        logger.error(f"Error in get_user: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while retrieving user information'
        }), 500 