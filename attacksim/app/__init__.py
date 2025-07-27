import os
import logging
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_security import Security, SQLAlchemyUserDatastore
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect

# Initialize extensions
db = SQLAlchemy()
mail = Mail()
security = Security()
cors = CORS()
limiter = Limiter(key_func=get_remote_address)
csrf = CSRFProtect()

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    from config import config
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    
    # Configure CORS for production
    cors_origins = app.config.get('CORS_ORIGINS', 'http://localhost:3000').split(',')
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": cors_origins,
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    limiter.init_app(app)
    
    # Import models for Flask-Security
    from app.models import User, Role
    
    # Setup Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, user_datastore)
    
    # Add CSRF token and datetime to template context
    @app.context_processor
    def inject_template_vars():
        from flask_wtf.csrf import generate_csrf
        return dict(csrf_token=generate_csrf, now=datetime.now())
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Register blueprints
    from app.routes import main, admin, api, simulations, oauth, tracking
    app.register_blueprint(main.bp)
    app.register_blueprint(admin.bp, url_prefix='/admin')
    app.register_blueprint(api.bp)
    app.register_blueprint(simulations.bp)
    app.register_blueprint(oauth.bp, url_prefix='/oauth')
    app.register_blueprint(tracking.bp)
    
    # Add security headers for production
    @app.after_request
    def security_headers(response):
        if app.config.get('FLASK_ENV') == 'production':
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response
    
    # Configure logging for production
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = logging.FileHandler('logs/attacksim.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('AttackSim startup')
    
    return app 