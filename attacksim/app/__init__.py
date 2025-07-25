import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import config

# Initialize extensions
db = SQLAlchemy()
mail = Mail()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)
security = Security()

def create_app(config_name=None):
    """Application factory function"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    
    # Setup Flask-Security-Too
    from app.models.user import User, Role
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, user_datastore)
    
    # Configure logging
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
    
    # Register blueprints
    from app.routes.oauth import bp as oauth_bp
    app.register_blueprint(oauth_bp, url_prefix='/oauth')
    
    from app.routes.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    from app.routes.simulations import bp as simulations_bp
    app.register_blueprint(simulations_bp, url_prefix='/sim')
    
    from app.routes.tracking import bp as tracking_bp
    app.register_blueprint(tracking_bp)
    
    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    # Template context processors
    @app.context_processor
    def inject_now():
        from datetime import datetime
        return {'now': datetime.utcnow()}
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create default roles if they don't exist (only if tables exist)
        try:
            if not user_datastore.find_role('admin'):
                user_datastore.create_role(name='admin', description='Administrator')
            if not user_datastore.find_role('user'):
                user_datastore.create_role(name='user', description='Regular User')
            db.session.commit()
        except Exception:
            # Tables don't exist yet, skip role creation
            pass
    
    return app 