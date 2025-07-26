from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from app import db
from app.models import Scenario, Interaction, EmailRecipient, EmailCampaign
from app.models.interaction import InteractionType, InteractionResult
import logging
from datetime import datetime
import json

bp = Blueprint('api', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)

@bp.route('/track-view', methods=['POST'])
@cross_origin()
def track_view():
    """Track when a user views a phishing clone page"""
    try:
        data = request.get_json()
        
        # Extract tracking information
        tracking_token = data.get('tracking_token')
        scenario_id = data.get('scenario_id')
        campaign_id = data.get('campaign_id')
        clone_type = data.get('clone_type', 'unknown')
        user_agent = data.get('user_agent')
        page_url = data.get('page_url')
        
        # Get IP address
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        if ip_address and ',' in ip_address:
            ip_address = ip_address.split(',')[0].strip()
        
        # Track email recipient if tracking token exists
        email_recipient = None
        if tracking_token:
            email_recipient = EmailRecipient.query.filter_by(unique_token=tracking_token).first()
            if email_recipient and not email_recipient.clicked_at:
                email_recipient.mark_clicked()
                email_recipient.ip_address = ip_address
                email_recipient.user_agent = user_agent
                db.session.commit()
        
        # Create interaction record if scenario exists
        if scenario_id:
            scenario = Scenario.query.get(scenario_id)
            if scenario:
                interaction = Interaction(
                    scenario_id=scenario_id,
                    interaction_type=InteractionType.EMAIL_CLICKED,
                    result=InteractionResult.PARTIAL,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    clicked_url=page_url,
                    email_delivery_id=tracking_token
                )
                
                # Try to link to user if possible
                if email_recipient and email_recipient.user_id:
                    interaction.user_id = email_recipient.user_id
                
                db.session.add(interaction)
                db.session.commit()
                
                logger.info(f"Tracked clone view: {clone_type} for scenario {scenario_id}")
        
        return jsonify({
            'success': True,
            'message': 'View tracked successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to track view: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to track view'
        }), 500

@bp.route('/track-submission', methods=['POST'])
@cross_origin()
def track_submission():
    """Track when a user submits credentials on a phishing clone"""
    try:
        data = request.get_json()
        
        # Extract submitted data
        email = data.get('email')
        password = data.get('password')  # In production, hash this immediately
        tracking_token = data.get('tracking_token')
        scenario_id = data.get('scenario_id')
        campaign_id = data.get('campaign_id')
        clone_type = data.get('clone_type', 'unknown')
        user_agent = data.get('user_agent')
        page_url = data.get('page_url')
        
        # Get IP address
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        if ip_address and ',' in ip_address:
            ip_address = ip_address.split(',')[0].strip()
        
        # Prepare submitted data (hash password for security)
        submitted_data = {
            'email': email,
            'password_hash': hash(password) if password else None,  # Simple hash, use bcrypt in production
            'clone_type': clone_type,
            'timestamp': datetime.utcnow().isoformat(),
            'page_url': page_url
        }
        
        # Track email recipient
        email_recipient = None
        if tracking_token:
            email_recipient = EmailRecipient.query.filter_by(unique_token=tracking_token).first()
        
        # Create or update interaction record
        interaction = None
        if scenario_id:
            scenario = Scenario.query.get(scenario_id)
            if scenario:
                # Check if there's an existing interaction for this session
                existing_interaction = None
                if tracking_token:
                    existing_interaction = Interaction.query.filter_by(
                        email_delivery_id=tracking_token,
                        scenario_id=scenario_id
                    ).first()
                
                if existing_interaction:
                    # Update existing interaction
                    interaction = existing_interaction
                    interaction.interaction_type = InteractionType.FORM_SUBMITTED
                    interaction.result = InteractionResult.FELL_FOR_IT
                    interaction.submitted_data = json.dumps(submitted_data)
                    interaction.detected_threat = False
                    interaction.mark_completed()
                else:
                    # Create new interaction
                    interaction = Interaction(
                        scenario_id=scenario_id,
                        interaction_type=InteractionType.FORM_SUBMITTED,
                        result=InteractionResult.FELL_FOR_IT,
                        detected_threat=False,
                        ip_address=ip_address,
                        user_agent=user_agent,
                        clicked_url=page_url,
                        submitted_data=json.dumps(submitted_data),
                        email_delivery_id=tracking_token
                    )
                    
                    # Try to link to user if possible
                    if email_recipient and email_recipient.user_id:
                        interaction.user_id = email_recipient.user_id
                    
                    db.session.add(interaction)
                
                # Update scenario statistics
                scenario.increment_stats(detected=False)
                
                db.session.commit()
                
                logger.info(f"Tracked credential submission: {clone_type} for scenario {scenario_id}")
                
                return jsonify({
                    'success': True,
                    'message': 'Credentials submitted successfully',
                    'educational_message': scenario.educational_message or 
                        "This was a phishing simulation! Never enter your real credentials on suspicious sites.",
                    'interaction_id': interaction.id
                })
        
        # Fallback response
        return jsonify({
            'success': True,
            'message': 'Data recorded',
            'educational_message': "This was a phishing simulation! Never enter your real credentials on suspicious sites."
        })
        
    except Exception as e:
        logger.error(f"Failed to track submission: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to track submission',
            'educational_message': "This was a phishing simulation! Never enter your real credentials on suspicious sites."
        }), 500

@bp.route('/track-ignore', methods=['POST'])
@cross_origin()
def track_ignore():
    """Track when a user ignores/closes the phishing page without submitting"""
    try:
        data = request.get_json()
        
        tracking_token = data.get('tracking_token')
        scenario_id = data.get('scenario_id')
        time_spent = data.get('time_spent', 0)
        
        # Get IP address
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        if ip_address and ',' in ip_address:
            ip_address = ip_address.split(',')[0].strip()
        
        if scenario_id:
            scenario = Scenario.query.get(scenario_id)
            if scenario:
                # Check for existing interaction
                existing_interaction = None
                if tracking_token:
                    existing_interaction = Interaction.query.filter_by(
                        email_delivery_id=tracking_token,
                        scenario_id=scenario_id
                    ).first()
                
                if existing_interaction and existing_interaction.result == InteractionResult.PARTIAL:
                    # Update existing interaction to show user ignored it
                    existing_interaction.result = InteractionResult.DETECTED
                    existing_interaction.detected_threat = True
                    existing_interaction.response_time = time_spent
                    existing_interaction.mark_completed()
                    
                    # Update scenario statistics
                    scenario.increment_stats(detected=True)
                    
                    db.session.commit()
                    
                    logger.info(f"Tracked ignore action for scenario {scenario_id}")
        
        return jsonify({
            'success': True,
            'message': 'Ignore action tracked'
        })
        
    except Exception as e:
        logger.error(f"Failed to track ignore: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to track ignore'}), 500

@bp.route('/campaign-stats/<campaign_id>', methods=['GET'])
@cross_origin()
def get_campaign_stats(campaign_id):
    """Get real-time statistics for a campaign"""
    try:
        campaign = EmailCampaign.query.get_or_404(campaign_id)
        
        # Get recipient statistics
        recipients = EmailRecipient.query.filter_by(campaign_id=campaign_id).all()
        total_recipients = len(recipients)
        
        # Count interactions
        opened_count = sum(1 for r in recipients if r.opened_at)
        clicked_count = sum(1 for r in recipients if r.clicked_at)
        
        # Get scenario interactions
        if campaign.scenario_id:
            interactions = Interaction.query.filter_by(scenario_id=campaign.scenario_id).all()
            submitted_count = sum(1 for i in interactions if i.interaction_type == InteractionType.FORM_SUBMITTED)
            detected_count = sum(1 for i in interactions if i.detected_threat)
        else:
            submitted_count = 0
            detected_count = 0
        
        stats = {
            'campaign_id': campaign_id,
            'total_recipients': total_recipients,
            'emails_opened': opened_count,
            'links_clicked': clicked_count,
            'credentials_submitted': submitted_count,
            'threats_detected': detected_count,
            'open_rate': (opened_count / total_recipients * 100) if total_recipients > 0 else 0,
            'click_rate': (clicked_count / total_recipients * 100) if total_recipients > 0 else 0,
            'submission_rate': (submitted_count / total_recipients * 100) if total_recipients > 0 else 0,
            'detection_rate': (detected_count / total_recipients * 100) if total_recipients > 0 else 0
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Failed to get campaign stats: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get stats'}), 500 