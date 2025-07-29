from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from app import db
from app.models import Scenario, Interaction, EmailRecipient, EmailCampaign, Clone, PhishingCredential, CredentialType
from app.models.clone import CloneStatus
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
        logger.info(f"🎯 TRACK-VIEW REQUEST RECEIVED: {json.dumps(data, indent=2)}")
        
        # Extract tracking information
        tracking_token = data.get('tracking_token')
        scenario_id = data.get('scenario_id')
        campaign_id = data.get('campaign_id')
        clone_type = data.get('clone_type', 'unknown')
        user_agent = data.get('user_agent')
        page_url = data.get('page_url')
        
        logger.info(f"📊 Tracking params: campaign_id={campaign_id}, token={tracking_token}, clone_type={clone_type}")
        
        # Get IP address
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        if ip_address and ',' in ip_address:
            ip_address = ip_address.split(',')[0].strip()
        
        # Find clone_id based on clone_type or page_url
        clone_id = None
        clone = None
        if clone_type:
            try:
                # Convert clone_type to uppercase to match the enum values stored in database
                clone_type_upper = clone_type.upper()
                clone = Clone.query.filter_by(clone_type=clone_type_upper, status=CloneStatus.ACTIVE).first()
                if clone:
                    clone_id = clone.id
                    # Increment visit counter
                    clone.increment_visit()
                    logger.info(f"✅ Found clone: {clone.name} (ID: {clone.id}) for type: {clone_type}")
                else:
                    logger.warning(f"❌ No active clone found for type: {clone_type} (tried: {clone_type_upper})")
            except Exception as e:
                logger.warning(f"Could not query clones table: {e}")
                # Continue without clone tracking
        
        # Track email recipient if tracking token exists
        # NOTE: This is page view tracking, NOT email click tracking
        # Email clicks are tracked in /track/click/<token> route
        email_recipient = None
        if tracking_token:
            email_recipient = EmailRecipient.query.filter_by(unique_token=tracking_token).first()
            if email_recipient:
                # Update metadata and mark as clicked since they're viewing the clone
                email_recipient.ip_address = ip_address
                email_recipient.user_agent = user_agent
                if not email_recipient.clicked_at:  # Only mark as clicked once
                    email_recipient.mark_clicked()
                db.session.commit()
                logger.info(f"Updated metadata and marked as clicked for recipient {email_recipient.email} - Page view tracked")
            else:
                logger.warning(f"❌ No email recipient found for token: {tracking_token}")
        
        # Create interaction record if scenario exists
        if scenario_id:
            scenario = Scenario.query.get(scenario_id)
            if scenario:
                # Only create interaction if we have a user_id (logged in user or email recipient with user)
                user_id = None
                if email_recipient and email_recipient.user_id:
                    user_id = email_recipient.user_id
                
                if user_id:
                    interaction = Interaction(
                        user_id=user_id,
                        scenario_id=scenario_id,
                        interaction_type=InteractionType.LINK_CLICKED,  # User clicked and viewed the clone page
                        result=InteractionResult.PARTIAL,
                        ip_address=ip_address,
                        user_agent=user_agent,
                        clicked_url=page_url,
                        email_delivery_id=tracking_token
                    )
                    
                    db.session.add(interaction)
                    db.session.commit()
                    
                    logger.info(f"Tracked clone view: {clone_type} for scenario {scenario_id}")
                else:
                    logger.info(f"Skip interaction creation - no user_id available for scenario {scenario_id}")
        
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

@bp.route('/track-interaction', methods=['POST'])
@cross_origin()
def track_interaction():
    """Track when a user clicks links or interacts with the clone (TIER 2)"""
    try:
        data = request.get_json()
        logger.info(f"🔗 TIER 2 - TRACK-INTERACTION REQUEST RECEIVED: {json.dumps(data, indent=2)}")
        
        # Extract tracking information
        tracking_token = data.get('tracking_token')
        scenario_id = data.get('scenario_id')
        campaign_id = data.get('campaign_id')
        clone_type = data.get('clone_type', 'unknown')
        user_agent = data.get('user_agent')
        page_url = data.get('page_url')
        clicked_link = data.get('clicked_link', 'Unknown')
        clicked_url = data.get('clicked_url', '')
        interaction_level = data.get('interaction_level', 'interaction')
        
        logger.info(f"🔗 Tier 2 - Interaction params: campaign_id={campaign_id}, token={tracking_token}, clicked_link={clicked_link}")
        
        # Get IP address
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        if ip_address and ',' in ip_address:
            ip_address = ip_address.split(',')[0].strip()
        
        # Find clone_id based on clone_type
        clone_id = None
        clone = None
        if clone_type:
            try:
                clone_type_upper = clone_type.upper()
                clone = Clone.query.filter_by(clone_type=clone_type_upper, status=CloneStatus.ACTIVE).first()
                if clone:
                    clone_id = clone.id
                    logger.info(f"✅ Found clone for interaction: {clone.name} (ID: {clone.id}) for type: {clone_type}")
                else:
                    logger.warning(f"❌ No active clone found for interaction type: {clone_type} (tried: {clone_type_upper})")
            except Exception as e:
                logger.warning(f"Could not query clones table: {e}")
        
        # Track email recipient if tracking token exists
        email_recipient = None
        if tracking_token:
            email_recipient = EmailRecipient.query.filter_by(unique_token=tracking_token).first()
            if email_recipient:
                # Update metadata but don't mark as clicked (that's for Tier 1)
                email_recipient.ip_address = ip_address
                email_recipient.user_agent = user_agent
                db.session.commit()
                logger.info(f"Updated metadata for recipient {email_recipient.email} - Interaction tracked")
            else:
                logger.warning(f"❌ No email recipient found for token: {tracking_token}")
        
        # Create interaction record if scenario exists
        if scenario_id:
            scenario = Scenario.query.get(scenario_id)
            if scenario:
                # Only create interaction if we have a user_id
                user_id = None
                if email_recipient and email_recipient.user_id:
                    user_id = email_recipient.user_id
                
                if user_id:
                    interaction = Interaction(
                        user_id=user_id,
                        scenario_id=scenario_id,
                        interaction_type=InteractionType.LINK_CLICKED,  # User clicked a link
                        result=InteractionResult.PARTIAL,  # They're engaging but not fully phished yet
                        ip_address=ip_address,
                        user_agent=user_agent,
                        clicked_url=clicked_url,
                        email_delivery_id=tracking_token
                    )
                    
                    db.session.add(interaction)
                    db.session.commit()
                    
                    logger.info(f"Tracked Tier 2 interaction: {clicked_link} for scenario {scenario_id}")
                else:
                    logger.info(f"Skip interaction creation - no user_id available for Tier 2 interaction")
        
        return jsonify({
            'success': True,
            'message': 'Interaction tracked successfully',
            'interaction_level': interaction_level,
            'clicked_link': clicked_link
        })
        
    except Exception as e:
        logger.error(f"Failed to track interaction: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to track interaction'
        }), 500

@bp.route('/track-submission', methods=['POST'])
@cross_origin()
def track_submission():
    """Track when a user submits credentials on a phishing clone (TIER 3: PHISHED)"""
    try:
        data = request.get_json()
        logger.info(f"🎣 TIER 3 - TRACK-SUBMISSION REQUEST RECEIVED (USER PHISHED!): {json.dumps({k: v if k != 'password' else '***' for k, v in data.items()}, indent=2)}")
        
        # Extract interaction level
        interaction_level = data.get('interaction_level', 'phished')
        logger.info(f"🎣 TIER 3 - User interaction level: {interaction_level}")
        
        # Extract submitted data
        email = data.get('email')
        password = data.get('password')
        tracking_token = data.get('tracking_token')
        scenario_id = data.get('scenario_id')
        campaign_id = data.get('campaign_id')
        clone_type = data.get('clone_type', 'unknown')
        user_agent = data.get('user_agent')
        page_url = data.get('page_url')
        referrer = data.get('referrer')
        
        logger.info(f"🎯 Submission params: campaign_id={campaign_id}, token={tracking_token}, email={email}, clone_type={clone_type}")
        
        # Get IP address
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        if ip_address and ',' in ip_address:
            ip_address = ip_address.split(',')[0].strip()
        
        # Find clone_id based on clone_type or page_url
        clone_id = None
        clone = None
        if clone_type:
            try:
                # Convert clone_type to uppercase to match the enum values stored in database
                clone_type_upper = clone_type.upper()
                clone = Clone.query.filter_by(clone_type=clone_type_upper, status=CloneStatus.ACTIVE).first()
                if clone:
                    clone_id = clone.id
                    # Increment submission counter
                    clone.increment_submission()
                    logger.info(f"✅ Found clone for submission: {clone.name} (ID: {clone.id}) for type: {clone_type}")
                else:
                    logger.warning(f"❌ No active clone found for submission type: {clone_type} (tried: {clone_type_upper})")
            except Exception as e:
                logger.warning(f"Could not query clones table: {e}")
                # Continue without clone tracking
        
        # Track email recipient
        email_recipient = None
        if tracking_token:
            email_recipient = EmailRecipient.query.filter_by(unique_token=tracking_token).first()
        
        # Store credentials in new PhishingCredential model
        credential_data = {
            'campaign_id': campaign_id,
            'clone_id': clone_id,
            'scenario_id': scenario_id,
            'tracking_token': tracking_token,
            'credential_type': 'email_password',
            'email': email,
            'password': password,
            'clone_type': clone_type,
            'page_url': page_url,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'referrer': referrer
        }
        
        credential = PhishingCredential.create_credential_record(credential_data)
        db.session.add(credential)
        
        # Prepare submitted data for interaction record (without raw password)
        submitted_data = {
            'email': email,
            'credential_id': None,  # Will be set after commit
            'clone_type': clone_type,
            'timestamp': datetime.utcnow().isoformat(),
            'page_url': page_url
        }
        
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
                    # Only create interaction if we have a user_id
                    user_id = None
                    if email_recipient and email_recipient.user_id:
                        user_id = email_recipient.user_id
                        credential.user_id = email_recipient.user_id
                    
                    if user_id:
                        # Create new interaction
                        interaction = Interaction(
                            user_id=user_id,
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
                        
                        db.session.add(interaction)
                    else:
                        logger.info(f"Skip interaction creation - no user_id available for submission")
                
                # Update scenario statistics
                scenario.increment_stats(detected=False)
        
        # Commit all changes
        db.session.commit()
        
        # Update submitted data with credential ID
        if interaction and credential.id:
            submitted_data['credential_id'] = credential.id
            interaction.submitted_data = json.dumps(submitted_data)
            db.session.commit()
        
        # Get educational message from scenario or use default
        educational_message = "This was a phishing simulation! Never enter your real credentials on suspicious sites."
        if scenario_id:
            scenario = Scenario.query.get(scenario_id)
            if scenario and scenario.educational_message:
                educational_message = scenario.educational_message
        
        logger.info(f"Tracked credential submission: {clone_type} - {email[:20]}... for campaign {campaign_id}")
        
        return jsonify({
            'success': True,
            'message': 'Credentials tracked successfully',
            'educational_message': educational_message,
            'credential_id': credential.id
        })
        
    except Exception as e:
        logger.error(f"Failed to track submission: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to track submission'
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
            # Count Tier 2 interactions (link clicks)
            interaction_count = sum(1 for i in interactions if i.interaction_type == InteractionType.LINK_CLICKED)
        else:
            submitted_count = 0
            detected_count = 0
            interaction_count = 0
        
        stats = {
            'campaign_id': campaign_id,
            'total_recipients': total_recipients,
            'emails_opened': opened_count,
            'links_clicked': clicked_count,
            'credentials_submitted': submitted_count,
            'threats_detected': detected_count,
            'interactions': interaction_count,  # Tier 2: Link clicks
            'open_rate': (opened_count / total_recipients * 100) if total_recipients > 0 else 0,
            'click_rate': (clicked_count / total_recipients * 100) if total_recipients > 0 else 0,
            'submission_rate': (submitted_count / total_recipients * 100) if total_recipients > 0 else 0,
            'detection_rate': (detected_count / total_recipients * 100) if total_recipients > 0 else 0,
            'interaction_rate': (interaction_count / total_recipients * 100) if total_recipients > 0 else 0
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Failed to get campaign stats: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get stats'}), 500 