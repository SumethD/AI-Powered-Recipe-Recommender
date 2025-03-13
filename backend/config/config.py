import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class"""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-for-development-only')
    
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    EDAMAM_API_KEY = os.getenv('EDAMAM_API_KEY')
    EDAMAM_APP_ID = os.getenv('EDAMAM_APP_ID')
    
    # API Base URLs
    EDAMAM_BASE_URL = 'https://api.edamam.com'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    # Production-specific settings
    pass

# Dictionary to map environment names to config objects
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}

# Get the current environment or default to development
ENV = os.getenv('FLASK_ENV', 'development')

# Export the active configuration
active_config = config_by_name[ENV] 