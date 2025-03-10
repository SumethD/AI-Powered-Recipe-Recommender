from flask import jsonify, current_app

def register_error_handlers(app):
    """
    Register error handlers for the Flask application
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(400)
    def bad_request(error):
        app.logger.warning(f'Bad Request: {str(error)}')
        return jsonify({
            'error': 'Bad Request',
            'message': str(error)
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        app.logger.warning(f'Unauthorized: {str(error)}')
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required'
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        app.logger.warning(f'Forbidden: {str(error)}')
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource'
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        app.logger.warning(f'Not Found: {str(error)}')
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        app.logger.warning(f'Method Not Allowed: {str(error)}')
        return jsonify({
            'error': 'Method Not Allowed',
            'message': 'The method is not allowed for the requested URL'
        }), 405
    
    @app.errorhandler(429)
    def too_many_requests(error):
        app.logger.warning(f'Too Many Requests: {str(error)}')
        return jsonify({
            'error': 'Too Many Requests',
            'message': 'Rate limit exceeded'
        }), 429
    
    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.error(f'Server Error: {str(error)}')
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500
    
    @app.errorhandler(503)
    def service_unavailable(error):
        app.logger.error(f'Service Unavailable: {str(error)}')
        return jsonify({
            'error': 'Service Unavailable',
            'message': 'The server is temporarily unable to handle the request'
        }), 503
        
    # Handle API-specific exceptions
    class APIError(Exception):
        """Base class for API exceptions"""
        def __init__(self, message, status_code=400, payload=None):
            super().__init__()
            self.message = message
            self.status_code = status_code
            self.payload = payload
            
        def to_dict(self):
            rv = dict(self.payload or ())
            rv['error'] = self.__class__.__name__
            rv['message'] = self.message
            return rv
    
    class SpoonacularAPIError(APIError):
        """Exception raised for Spoonacular API errors"""
        pass
    
    class OpenAIAPIError(APIError):
        """Exception raised for OpenAI API errors"""
        pass
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        app.logger.error(f'API Error: {error.message}')
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    # Make the custom exceptions available to the app
    app.APIError = APIError
    app.SpoonacularAPIError = SpoonacularAPIError
    app.OpenAIAPIError = OpenAIAPIError 