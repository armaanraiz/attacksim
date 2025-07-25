import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'it.help.service.alerts@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # You'll need to set this as environment variable
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'it.help.service.alerts@gmail.com'
    
    # Flask-Security-Too Configuration
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or 'your-security-password-salt'
    SECURITY_REGISTERABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_TRACKABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_CONFIRMABLE = False  # Set to True if you want email confirmation
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_POST_LOGIN_REDIRECT_ENDPOINT = 'main.dashboard'
    SECURITY_POST_LOGOUT_REDIRECT_ENDPOINT = 'main.index'
    SECURITY_POST_REGISTER_REDIRECT_ENDPOINT = 'main.dashboard'
    SECURITY_EMAIL_SENDER = os.environ.get('SECURITY_EMAIL_SENDER') or 'it.help.service.alerts@gmail.com'
    
    # OAuth Configuration (Google)
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    OAUTH_CREDENTIALS = {
        'google': {
            'id': GOOGLE_CLIENT_ID,
            'secret': GOOGLE_CLIENT_SECRET
        }
    }
    
    # Security settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    WTF_CSRF_ENABLED = True
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379'
    
    # Celery configuration
    CELERY_BROKER_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Application settings
    ATTACKSIM_CONSENT_REQUIRED = True
    ATTACKSIM_LOG_LEVEL = 'INFO'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
    TESTING = False
    
    # Development mail settings (use console for testing)
    MAIL_SUPPRESS_SEND = False
    MAIL_DEBUG = True
    
    # Development OAuth settings (use localhost callback)
    GOOGLE_OAUTH_REDIRECT_URI = 'http://localhost:5000/oauth/google/callback'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://user:password@localhost/attacksim'
    TESTING = False
    
    # Production security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Production OAuth settings
    GOOGLE_OAUTH_REDIRECT_URI = os.environ.get('GOOGLE_OAUTH_REDIRECT_URI')

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    MAIL_SUPPRESS_SEND = True
    SECRET_KEY = 'testing-secret-key'
    SECURITY_PASSWORD_SALT = 'testing-salt'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 