from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from functools import wraps
from werkzeug.utils import secure_filename
from app import db
from app.models import User, Scenario, Interaction, Group, EmailCampaign, EmailRecipient
from app.models.scenario import ScenarioType, ScenarioStatus
from app.models.interaction import InteractionResult
from app.models.email_campaign import CampaignStatus
from app.utils.email_sender import PhishingEmailSender
import json
import os
import uuid

bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin privileges required.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# Image upload configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_campaign_image(file):
    """Save uploaded image and return the URL"""
    try:
        if not file or not allowed_file(file.filename):
            return None
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{uuid.uuid4()}{ext}"
        
        # Save to static/images/campaigns
        upload_dir = os.path.join(current_app.root_path, 'static', 'images', 'campaigns')
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        return f"/static/images/campaigns/{unique_filename}"
    except Exception as e:
        current_app.logger.error(f"Error saving image: {str(e)}")
        return None

@bp.route('/')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with overview statistics"""
    # Get overall statistics
    total_users = User.query.count()
    total_scenarios = Scenario.query.count()
    total_interactions = Interaction.query.count()
    consented_users = User.query.filter_by(consent_given=True).count()
    
    # Get recent activity
    recent_interactions = Interaction.query.order_by(
        Interaction.created_at.desc()
    ).limit(10).all()
    
    # Get scenario statistics
    active_scenarios = Scenario.query.filter_by(status=ScenarioStatus.ACTIVE).count()
    
    # Calculate detection rates
    successful_detections = Interaction.query.filter_by(detected_threat=True).count()
    detection_rate = 0
    if total_interactions > 0:
        detection_rate = round((successful_detections / total_interactions) * 100, 1)
    
    stats = {
        'total_users': total_users,
        'consented_users': consented_users,
        'total_scenarios': total_scenarios,
        'active_scenarios': active_scenarios,
        'total_interactions': total_interactions,
        'successful_detections': successful_detections,
        'detection_rate': detection_rate
    }
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         recent_interactions=recent_interactions)

@bp.route('/scenarios')
@login_required
@admin_required
def scenarios():
    """List all scenarios"""
    scenarios = Scenario.query.order_by(Scenario.created_at.desc()).all()
    return render_template('admin/scenarios.html', scenarios=scenarios)

@bp.route('/scenarios/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_scenario():
    """Create new attack scenario"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        scenario_type = request.form.get('scenario_type')
        difficulty_level = int(request.form.get('difficulty_level', 1))
        
        if not all([name, scenario_type]):
            flash('Name and scenario type are required.', 'error')
            return render_template('admin/create_scenario.html', scenario_types=ScenarioType)
        
        scenario = Scenario(
            name=name,
            description=description,
            scenario_type=ScenarioType(scenario_type),
            difficulty_level=difficulty_level,
            created_by=current_user.id
        )
        
        # Add scenario-specific fields
        if scenario.scenario_type == ScenarioType.PHISHING_EMAIL:
            scenario.email_subject = request.form.get('email_subject')
            scenario.email_body = request.form.get('email_body')
            scenario.sender_name = request.form.get('sender_name')
            scenario.sender_email = request.form.get('sender_email')
        elif scenario.scenario_type == ScenarioType.FAKE_LOGIN:
            scenario.target_website = request.form.get('target_website')
            scenario.login_template = request.form.get('login_template')
        elif scenario.scenario_type == ScenarioType.SUSPICIOUS_LINK:
            scenario.malicious_url = request.form.get('malicious_url')
            scenario.link_text = request.form.get('link_text')
        
        # Educational content
        scenario.educational_message = request.form.get('educational_message')
        scenario.learning_objectives = request.form.get('learning_objectives')
        scenario.warning_signs = request.form.get('warning_signs')
        
        db.session.add(scenario)
        db.session.commit()
        
        flash('Scenario created successfully!', 'success')
        return redirect(url_for('admin.scenarios'))
    
    return render_template('admin/create_scenario.html', scenario_types=ScenarioType)

@bp.route('/scenarios/<int:scenario_id>')
@login_required
@admin_required
def view_scenario(scenario_id):
    """View scenario details and analytics"""
    scenario = Scenario.query.get_or_404(scenario_id)
    
    # Get scenario interactions
    interactions = scenario.interactions.order_by(Interaction.created_at.desc()).all()
    
    # Calculate detailed statistics
    total_interactions = len(interactions)
    successful_detections = sum(1 for i in interactions if i.detected_threat)
    failed_detections = total_interactions - successful_detections
    
    # Response time statistics
    response_times = [i.response_time for i in interactions if i.response_time]
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    detailed_stats = {
        'total_interactions': total_interactions,
        'successful_detections': successful_detections,
        'failed_detections': failed_detections,
        'avg_response_time': round(avg_response_time, 1)
    }
    
    return render_template('admin/view_scenario.html', 
                         scenario=scenario, 
                         interactions=interactions,
                         stats=detailed_stats)

@bp.route('/scenarios/<int:scenario_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_scenario(scenario_id):
    """Edit existing scenario"""
    scenario = Scenario.query.get_or_404(scenario_id)
    
    if request.method == 'POST':
        scenario.name = request.form.get('name')
        scenario.description = request.form.get('description')
        scenario.difficulty_level = int(request.form.get('difficulty_level', 1))
        
        # Update scenario-specific fields
        if scenario.scenario_type == ScenarioType.PHISHING_EMAIL:
            scenario.email_subject = request.form.get('email_subject')
            scenario.email_body = request.form.get('email_body')
            scenario.sender_name = request.form.get('sender_name')
            scenario.sender_email = request.form.get('sender_email')
        elif scenario.scenario_type == ScenarioType.FAKE_LOGIN:
            scenario.target_website = request.form.get('target_website')
            scenario.login_template = request.form.get('login_template')
        elif scenario.scenario_type == ScenarioType.SUSPICIOUS_LINK:
            scenario.malicious_url = request.form.get('malicious_url')
            scenario.link_text = request.form.get('link_text')
        
        # Educational content
        scenario.educational_message = request.form.get('educational_message')
        scenario.learning_objectives = request.form.get('learning_objectives')
        scenario.warning_signs = request.form.get('warning_signs')
        
        db.session.commit()
        flash('Scenario updated successfully!', 'success')
        return redirect(url_for('admin.view_scenario', scenario_id=scenario.id))
    
    return render_template('admin/edit_scenario.html', scenario=scenario)

@bp.route('/scenarios/<int:scenario_id>/activate', methods=['POST'])
@login_required
@admin_required
def activate_scenario(scenario_id):
    """Activate a scenario"""
    scenario = Scenario.query.get_or_404(scenario_id)
    
    if not scenario.can_be_activated():
        flash('Scenario cannot be activated. Please fill in all required fields.', 'error')
        return redirect(url_for('admin.view_scenario', scenario_id=scenario.id))
    
    scenario.status = ScenarioStatus.ACTIVE
    db.session.commit()
    
    flash('Scenario activated successfully!', 'success')
    return redirect(url_for('admin.view_scenario', scenario_id=scenario.id))

@bp.route('/scenarios/<int:scenario_id>/deactivate', methods=['POST'])
@login_required
@admin_required
def deactivate_scenario(scenario_id):
    """Deactivate a scenario"""
    scenario = Scenario.query.get_or_404(scenario_id)
    scenario.status = ScenarioStatus.PAUSED
    db.session.commit()
    
    flash('Scenario deactivated.', 'info')
    return redirect(url_for('admin.view_scenario', scenario_id=scenario.id))

@bp.route('/users')
@login_required
@admin_required
def users():
    """List all users"""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@bp.route('/users/<int:user_id>')
@login_required
@admin_required
def view_user(user_id):
    """View user details and interaction history"""
    user = User.query.get_or_404(user_id)
    interactions = user.interactions.order_by(Interaction.created_at.desc()).all()
    stats = user.get_interaction_stats()
    
    return render_template('admin/view_user.html', 
                         user=user, 
                         interactions=interactions,
                         stats=stats)

@bp.route('/analytics')
@login_required
@admin_required
def analytics():
    """Advanced analytics dashboard"""
    # Overall statistics
    total_users = User.query.count()
    total_interactions = Interaction.query.count()
    
    # Scenario performance
    scenarios = Scenario.query.all()
    scenario_stats = []
    for scenario in scenarios:
        stats = {
            'name': scenario.name,
            'type': scenario.scenario_type.value,
            'success_rate': scenario.get_success_rate(),
            'total_interactions': scenario.total_interactions
        }
        scenario_stats.append(stats)
    
    # User performance distribution
    user_stats = []
    for user in User.query.all():
        stats = user.get_interaction_stats()
        user_stats.append({
            'username': user.username,
            'detection_rate': stats['detection_rate'],
            'total_interactions': stats['total_interactions']
        })
    
    return render_template('admin/analytics.html',
                         scenario_stats=scenario_stats,
                         user_stats=user_stats)

# Group Management Routes
@bp.route('/groups')
@login_required
@admin_required
def groups():
    """List all groups"""
    groups = Group.query.filter_by(is_active=True).order_by(Group.created_at.desc()).all()
    return render_template('admin/groups.html', groups=groups)

@bp.route('/groups/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_group():
    """Create new group"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', '')
        
        if not name:
            flash('Group name is required.', 'error')
            return render_template('admin/create_group.html')
        
        # Check if group name already exists
        existing_group = Group.query.filter_by(name=name, is_active=True).first()
        if existing_group:
            flash('A group with this name already exists.', 'error')
            return render_template('admin/create_group.html')
        
        # Create group
        group = Group(
            name=name,
            description=description,
            created_by=current_user.id
        )
        
        db.session.add(group)
        db.session.commit()
        
        # Add registered users if provided
        registered_users = request.form.getlist('registered_users')
        if registered_users:
            users = User.query.filter(User.id.in_(registered_users)).all()
            group.members.extend(users)
        
        # Add external emails if provided
        external_emails = request.form.get('external_emails', '')
        if external_emails:
            # Split by both commas and newlines, then clean up
            import re
            email_list = [email.strip() for email in re.split(r'[,\n]', external_emails) if email.strip()]
            group.add_external_emails(email_list)
        
        db.session.commit()
        
        flash(f'Group "{name}" created successfully with {group.get_member_count()} members.', 'success')
        return redirect(url_for('admin.groups'))
    
    # Get all users for the form
    users = User.query.filter_by(consent_given=True).order_by(User.email).all()
    return render_template('admin/create_group.html', users=users)

@bp.route('/groups/<int:group_id>')
@login_required
@admin_required
def view_group(group_id):
    """View group details"""
    group = Group.query.get_or_404(group_id)
    campaigns = group.campaigns.order_by(EmailCampaign.created_at.desc()).all()
    
    return render_template('admin/view_group.html', group=group, campaigns=campaigns)

@bp.route('/groups/<int:group_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_group(group_id):
    """Edit group"""
    group = Group.query.get_or_404(group_id)
    
    if request.method == 'POST':
        group.name = request.form.get('name', group.name)
        group.description = request.form.get('description', group.description)
        
        # Update registered members
        registered_users = request.form.getlist('registered_users')
        current_member_ids = [member.id for member in group.members]
        
        # Remove members not in the new list
        for member in group.members[:]:  # Create a copy to iterate over
            if str(member.id) not in registered_users:
                group.members.remove(member)
        
        # Add new members
        for user_id in registered_users:
            if int(user_id) not in current_member_ids:
                user = User.query.get(int(user_id))
                if user:
                    group.members.append(user)
        
        # Update external emails
        external_emails = request.form.get('external_emails', '')
        if external_emails:
            # Split by both commas and newlines, then clean up
            import re
            email_list = [email.strip() for email in re.split(r'[,\n]', external_emails) if email.strip()]
            group.email_list = json.dumps(email_list)
        else:
            group.email_list = json.dumps([])
        
        db.session.commit()
        
        flash(f'Group "{group.name}" updated successfully.', 'success')
        return redirect(url_for('admin.view_group', group_id=group.id))
    
    users = User.query.filter_by(consent_given=True).order_by(User.email).all()
    current_member_ids = [member.id for member in group.members]
    external_emails = ', '.join(group.get_external_emails())
    
    return render_template('admin/edit_group.html', 
                         group=group, 
                         users=users, 
                         current_member_ids=current_member_ids,
                         external_emails=external_emails)

@bp.route('/groups/<int:group_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_group(group_id):
    """Delete group (soft delete)"""
    group = Group.query.get_or_404(group_id)
    group.is_active = False
    db.session.commit()
    
    flash(f'Group "{group.name}" has been deleted.', 'success')
    return redirect(url_for('admin.groups'))

# Email Campaign Routes
@bp.route('/campaigns')
@login_required
@admin_required
def campaigns():
    """List all email campaigns"""
    campaigns = EmailCampaign.query.order_by(EmailCampaign.created_at.desc()).all()
    return render_template('admin/campaigns.html', campaigns=campaigns)

@bp.route('/campaigns/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_campaign():
    """Create new email campaign"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', '')
        scenario_id = request.form.get('scenario_id')
        group_id = request.form.get('group_id')
        subject = request.form.get('subject')
        body = request.form.get('body')
        sender_name = request.form.get('sender_name')
        sender_email = request.form.get('sender_email')
        
        if not all([name, group_id, subject, body, sender_name, sender_email]):
            flash('Name, group, subject, body, sender name, and sender email are required.', 'error')
            return redirect(url_for('admin.create_campaign'))
        
        # Validate group exists
        group = Group.query.get(group_id)
        if not group:
            flash('Invalid group selected.', 'error')
            return redirect(url_for('admin.create_campaign'))
        
        # Validate scenario if provided
        scenario = None
        if scenario_id:
            scenario = Scenario.query.get(scenario_id)
            if not scenario:
                flash('Invalid scenario selected.', 'error')
                return redirect(url_for('admin.create_campaign'))
        
        # Create campaign
        campaign = EmailCampaign(
            name=name,
            description=description,
            scenario_id=scenario.id if scenario else None,
            group_id=group_id,
            subject=subject,
            body=body,
            sender_name=sender_name,
            sender_email=sender_email,
            created_by=current_user.id
        )
        
        # Handle attached images from the form
        attached_images = request.form.get('attached_images', '')
        if attached_images:
            campaign.attached_images = attached_images
        
        db.session.add(campaign)
        db.session.commit()
        
        flash(f'Campaign "{name}" created successfully.', 'success')
        return redirect(url_for('admin.view_campaign', campaign_id=campaign.id))
    
    # Get scenarios and groups for the form
    scenarios = Scenario.query.filter_by(scenario_type=ScenarioType.PHISHING_EMAIL).all()
    groups = Group.query.filter_by(is_active=True).all()
    
    return render_template('admin/create_campaign.html', scenarios=scenarios, groups=groups)

@bp.route('/campaigns/<int:campaign_id>')
@login_required
@admin_required
def view_campaign(campaign_id):
    """View campaign details and analytics"""
    campaign = EmailCampaign.query.get_or_404(campaign_id)
    recipients = campaign.recipients.order_by(EmailRecipient.created_at.desc()).all()
    
    return render_template('admin/view_campaign.html', campaign=campaign, recipients=recipients)

@bp.route('/campaigns/<int:campaign_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_campaign(campaign_id):
    """Edit campaign"""
    campaign = EmailCampaign.query.get_or_404(campaign_id)
    
    # Allow editing campaigns at any status for phishing simulations
    # Note: Editing sent campaigns allows for corrections and re-use
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        scenario_id = request.form.get('scenario_id')
        group_id = request.form.get('group_id')
        subject = request.form.get('subject', '').strip()
        body = request.form.get('body', '').strip()
        sender_name = request.form.get('sender_name', '').strip()
        sender_email = request.form.get('sender_email', '').strip()
        
        # Validate required fields
        if not all([name, group_id, subject, body, sender_name, sender_email]):
            flash('Name, group, subject, body, sender name, and sender email are required.', 'error')
            scenarios = Scenario.query.filter_by(scenario_type=ScenarioType.PHISHING_EMAIL).all()
            groups = Group.query.filter_by(is_active=True).all()
            return render_template('admin/edit_campaign.html', campaign=campaign, scenarios=scenarios, groups=groups)
        
        # Validate group exists
        group = Group.query.get(group_id)
        if not group:
            flash('Invalid group selected.', 'error')
            scenarios = Scenario.query.filter_by(scenario_type=ScenarioType.PHISHING_EMAIL).all()
            groups = Group.query.filter_by(is_active=True).all()
            return render_template('admin/edit_campaign.html', campaign=campaign, scenarios=scenarios, groups=groups)
        
        # Validate scenario if provided
        scenario = None
        if scenario_id:
            scenario = Scenario.query.get(scenario_id)
            if not scenario:
                flash('Invalid scenario selected.', 'error')
                scenarios = Scenario.query.filter_by(scenario_type=ScenarioType.PHISHING_EMAIL).all()
                groups = Group.query.filter_by(is_active=True).all()
                return render_template('admin/edit_campaign.html', campaign=campaign, scenarios=scenarios, groups=groups)
        
        # Update campaign
        campaign.name = name
        campaign.description = description
        campaign.scenario_id = scenario.id if scenario else None
        campaign.group_id = group_id
        campaign.subject = subject
        campaign.body = body
        campaign.sender_name = sender_name
        campaign.sender_email = sender_email
        campaign.total_recipients = group.get_member_count()
        
        # Handle attached images from the form
        attached_images = request.form.get('attached_images', '')
        campaign.attached_images = attached_images if attached_images else None
        
        db.session.commit()
        flash(f'Campaign "{campaign.name}" has been updated successfully.', 'success')
        return redirect(url_for('admin.view_campaign', campaign_id=campaign.id))
    
    # GET request - show edit form
    scenarios = Scenario.query.filter_by(scenario_type=ScenarioType.PHISHING_EMAIL).all()
    groups = Group.query.filter_by(is_active=True).all()
    return render_template('admin/edit_campaign.html', campaign=campaign, scenarios=scenarios, groups=groups)

@bp.route('/campaigns/<int:campaign_id>/send', methods=['POST'])
@login_required
@admin_required
def send_campaign(campaign_id):
    """Send email campaign"""
    campaign = EmailCampaign.query.get_or_404(campaign_id)
    
    if not campaign.can_be_sent():
        flash('Campaign cannot be sent. Please check all required fields.', 'error')
        return redirect(url_for('admin.view_campaign', campaign_id=campaign.id))
    
    # Send campaign (or re-send if already sent)
    is_resend = campaign.status in [CampaignStatus.SENT, CampaignStatus.COMPLETED]
    
    try:
        sender = PhishingEmailSender()
        success, message = sender.send_campaign(campaign)
        
        if success:
            action = "re-sent" if is_resend else "sent"
            flash(f'Campaign {action} successfully! {message}', 'success')
        else:
            action = "re-send" if is_resend else "send"
            flash(f'Failed to {action} campaign: {message}', 'error')
    
    except ValueError as ve:
        # Configuration errors
        flash(f'Email configuration error: {str(ve)}', 'error')
        current_app.logger.error(f"Email config error when sending campaign {campaign.id}: {str(ve)}")
    except Exception as e:
        # Other unexpected errors
        flash(f'Unexpected error: {str(e)}', 'error')
        current_app.logger.error(f"Unexpected error when sending campaign {campaign.id}: {str(e)}")
    
    return redirect(url_for('admin.view_campaign', campaign_id=campaign.id))

@bp.route('/campaigns/<int:campaign_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_campaign(campaign_id):
    """Delete campaign"""
    campaign = EmailCampaign.query.get_or_404(campaign_id)
    
    # Allow deletion of campaigns at any status for phishing simulations
    # Note: This allows cleanup of test campaigns and sent campaigns if needed
    
    db.session.delete(campaign)
    db.session.commit()
    
    flash(f'Campaign "{campaign.name}" has been deleted.', 'success')
    return redirect(url_for('admin.campaigns'))

@bp.route('/campaigns/upload-image', methods=['POST'])
@login_required
@admin_required
def upload_campaign_image():
    """Upload image for email campaign"""
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Check file size
        if hasattr(file, 'content_length') and file.content_length > MAX_FILE_SIZE:
            return jsonify({'success': False, 'error': 'File too large. Maximum size is 5MB'}), 400
        
        # Save the image
        image_url = save_campaign_image(file)
        if not image_url:
            return jsonify({'success': False, 'error': 'Invalid file type. Allowed: PNG, JPG, JPEG, GIF, BMP, WebP'}), 400
        
        return jsonify({
            'success': True,
            'url': image_url,
            'filename': file.filename
        })
    except Exception as e:
        current_app.logger.error(f"Image upload error: {str(e)}")
        return jsonify({'success': False, 'error': 'An error occurred while uploading the image'}), 500 