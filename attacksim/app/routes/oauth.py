from flask import Blueprint, current_app, url_for, redirect, session, flash
from flask_security import login_user, current_user
from authlib.integrations.flask_client import OAuth
from app import db
from app.models.user import User
from datetime import datetime
import secrets

bp = Blueprint('oauth', __name__)

oauth = OAuth()

def init_oauth(app):
    """Initialize OAuth with the Flask app"""
    oauth.init_app(app)
    
    google = oauth.register(
        name='google',
        client_id=app.config.get('GOOGLE_CLIENT_ID'),
        client_secret=app.config.get('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
    return google

@bp.route('/google')
def google_login():
    """Initiate Google OAuth login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    google = init_oauth(current_app)
    redirect_uri = url_for('oauth.google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@bp.route('/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    google = init_oauth(current_app)
    
    try:
        token = google.authorize_access_token()
        user_info = token.get('userinfo')
        
        if user_info:
            # Check if user already exists
            user = User.query.filter_by(email=user_info['email']).first()
            
            if not user:
                # Create new user from Google account
                from flask_security import hash_password
                user = User(
                    email=user_info['email'],
                    google_id=user_info['sub'],
                    first_name=user_info.get('given_name', ''),
                    last_name=user_info.get('family_name', ''),
                    confirmed_at=datetime.utcnow(),
                    fs_uniquifier=secrets.token_urlsafe(),
                    active=True
                )
                
                # Add default user role
                from flask_security import current_app
                user_datastore = current_app.extensions['security'].datastore
                user_role = user_datastore.find_role('user')
                if user_role:
                    user_datastore.add_role_to_user(user, user_role)
                
                db.session.add(user)
                db.session.commit()
                
                flash(f'Welcome to AttackSim, {user.get_full_name()}! Your account has been created.', 'success')
            else:
                # Update existing user with Google ID if not set
                if not user.google_id:
                    user.google_id = user_info['sub']
                    db.session.commit()
                
                flash(f'Welcome back, {user.get_full_name()}!', 'success')
            
            # Log the user in
            login_user(user)
            return redirect(url_for('main.dashboard'))
        
        else:
            flash('Failed to get user information from Google.', 'error')
            return redirect(url_for('security.login'))
            
    except Exception as e:
        current_app.logger.error(f'OAuth error: {str(e)}')
        flash('Authentication failed. Please try again.', 'error')
        return redirect(url_for('security.login'))

@bp.route('/link-google')
def link_google():
    """Link existing account with Google (for logged-in users)"""
    if not current_user.is_authenticated:
        return redirect(url_for('security.login'))
    
    if current_user.google_id:
        flash('Your account is already linked to Google.', 'info')
        return redirect(url_for('main.dashboard'))
    
    google = init_oauth(current_app)
    redirect_uri = url_for('oauth.link_google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@bp.route('/link-google/callback')
def link_google_callback():
    """Handle Google account linking for existing users"""
    if not current_user.is_authenticated:
        return redirect(url_for('security.login'))
    
    google = init_oauth(current_app)
    
    try:
        token = google.authorize_access_token()
        user_info = token.get('userinfo')
        
        if user_info:
            # Check if this Google account is already linked to another user
            existing_user = User.query.filter_by(google_id=user_info['sub']).first()
            if existing_user and existing_user.id != current_user.id:
                flash('This Google account is already linked to another user.', 'error')
                return redirect(url_for('main.dashboard'))
            
            # Link Google account to current user
            current_user.google_id = user_info['sub']
            db.session.commit()
            
            flash('Your account has been successfully linked to Google!', 'success')
        else:
            flash('Failed to link Google account.', 'error')
            
    except Exception as e:
        current_app.logger.error(f'OAuth linking error: {str(e)}')
        flash('Failed to link Google account. Please try again.', 'error')
    
    return redirect(url_for('main.dashboard'))

@bp.route('/unlink-google', methods=['POST'])
def unlink_google():
    """Unlink Google account from current user"""
    if not current_user.is_authenticated:
        return redirect(url_for('security.login'))
    
    if not current_user.google_id:
        flash('Your account is not linked to Google.', 'info')
        return redirect(url_for('main.dashboard'))
    
    # Only allow unlinking if user has a password set
    if not current_user.password:
        flash('Cannot unlink Google account. Please set a password first.', 'error')
        return redirect(url_for('main.dashboard'))
    
    current_user.google_id = None
    db.session.commit()
    
    flash('Your Google account has been unlinked.', 'success')
    return redirect(url_for('main.dashboard')) 