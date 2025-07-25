from flask import Blueprint, render_template, current_app, redirect, url_for, request, flash
from flask_login import current_user, login_required
from flask_security import auth_required
from app.models import Interaction
from app import db

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@bp.route('/dashboard')
def dashboard():
    """User dashboard showing their stats and recent activity"""
    if not current_user.is_authenticated:
        return redirect(url_for('security.login'))
    
    # Get user stats
    stats = current_user.get_interaction_stats()
    
    # Get recent interactions
    recent_interactions = current_user.interactions.order_by(
        Interaction.created_at.desc()
    ).limit(10).all()
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         recent_interactions=recent_interactions)

@bp.route('/profile')
@auth_required()
def profile():
    """User profile page"""
    return render_template('security/profile.html', user=current_user)

@bp.route('/give-consent', methods=['POST'])
@auth_required()
def give_consent():
    """Enable training/consent for the current user"""
    current_user.consent_given = True
    db.session.commit()
    flash('Training has been enabled for your account.', 'success')
    return redirect(request.referrer or url_for('main.dashboard'))

@bp.route('/revoke-consent', methods=['POST'])
@auth_required()
def revoke_consent():
    """Disable training/consent for the current user"""
    current_user.consent_given = False
    db.session.commit()
    flash('Training has been disabled for your account.', 'info')
    return redirect(request.referrer or url_for('main.dashboard'))

@bp.route('/about')
def about():
    """About page explaining the platform"""
    return render_template('about.html')

@bp.route('/consent')
def consent():
    """Consent page for users to opt-in to simulations"""
    return render_template('consent.html')

@bp.route('/help')
def help():
    """Help and FAQ page"""
    return render_template('help.html') 