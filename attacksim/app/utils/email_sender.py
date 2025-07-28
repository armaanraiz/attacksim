import secrets
import uuid
import os
import json
from datetime import datetime
from flask import current_app, url_for
from flask_mail import Message
from app import mail, db
from app.models import EmailRecipient, User
from app.models.email_campaign import CampaignStatus
from app.models.clone import Clone
import logging

logger = logging.getLogger(__name__)

class PhishingEmailSender:
    """Utility class for sending phishing simulation emails"""
    
    def __init__(self):
        """Initialize email sender with configuration"""
        self.mail = mail
        self.tracking_domain = current_app.config.get('TRACKING_DOMAIN', 'localhost:5001')
        self.protocol = current_app.config.get('TRACKING_PROTOCOL', 'http')
        
        # Email server configuration validation
        self.smtp_server = current_app.config.get('MAIL_SERVER')
        self.smtp_port = current_app.config.get('MAIL_PORT')
        self.smtp_username = current_app.config.get('MAIL_USERNAME')
        self.smtp_password = current_app.config.get('MAIL_PASSWORD')
        
    def _check_email_config(self):
        """Validate email configuration"""
        if not all([self.smtp_server, self.smtp_port, self.smtp_username, self.smtp_password]):
            raise ValueError("Email configuration incomplete. Please check MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, and MAIL_PASSWORD.")

    def send_campaign(self, campaign):
        """Send emails for an entire campaign"""
        try:
            # Check email configuration first
            self._check_email_config()
            # Get recipient emails
            recipient_emails = campaign.get_recipient_emails()
            campaign.total_recipients = len(recipient_emails)
            
            # Check if this is a re-send (recipients already exist)
            existing_recipients = EmailRecipient.query.filter_by(campaign_id=campaign.id).all()
            
            if existing_recipients:
                # Re-send to existing recipients
                recipients_to_send = existing_recipients
                logger.info(f"Re-sending campaign {campaign.name} to {len(recipients_to_send)} existing recipients")
            else:
                # Create new recipient records for first send
                recipients_created = []
                for email in recipient_emails:
                    # Check if user exists
                    user = User.query.filter_by(email=email).first()
                    
                    # Create recipient record
                    recipient = EmailRecipient(
                        campaign_id=campaign.id,
                        email=email,
                        user_id=user.id if user else None,
                        unique_token=self._generate_unique_token()
                    )
                    db.session.add(recipient)
                    recipients_created.append(recipient)
                
                db.session.commit()
                recipients_to_send = recipients_created
                logger.info(f"Sending campaign {campaign.name} to {len(recipients_to_send)} new recipients")
            
            # Send emails to each recipient
            sent_count = 0
            for recipient in recipients_to_send:
                try:
                    email_sent = self._send_single_email(campaign, recipient)
                    if email_sent:
                        sent_count += 1
                        recipient.sent_at = datetime.utcnow()
                        recipient.mark_delivered()  # Assume delivered for now
                    else:
                        recipient.mark_failed("Failed to send email")
                except Exception as e:
                    logger.error(f"Failed to send email to {recipient.email}: {str(e)}")
                    # Also log the full traceback for debugging
                    import traceback
                    logger.error(f"Full traceback: {traceback.format_exc()}")
                    recipient.mark_failed(str(e))
            
            # Update campaign stats  
            # Check if this was a re-send by looking at existing recipients
            is_resend = len(EmailRecipient.query.filter_by(campaign_id=campaign.id).all()) > 0
            if is_resend:
                # For re-sends, add to existing count
                campaign.emails_sent += sent_count
            else:
                # For new sends, set the count
                campaign.emails_sent = sent_count
            campaign.mark_sent()
            
            logger.info(f"Campaign {campaign.name} sent to {sent_count}/{len(recipient_emails)} recipients")
            return True, f"Successfully sent {sent_count} out of {len(recipient_emails)} emails"
            
        except Exception as e:
            logger.error(f"Failed to send campaign {campaign.name}: {str(e)}")
            return False, f"Failed to send campaign: {str(e)}"
    
    def _send_single_email(self, campaign, recipient):
        """Send email to a single recipient"""
        try:
            logger.info(f"Starting email send to {recipient.email}")
            
            # Generate tracking URLs
            tracking_pixel_url = self._generate_tracking_pixel_url(recipient.unique_token)
            click_tracking_url = self._generate_click_tracking_url(recipient.unique_token, campaign)
            logger.info(f"Generated tracking URLs for {recipient.email}: pixel={tracking_pixel_url}, click={click_tracking_url}")
            
            # Prepare email body with tracking and embedded images
            email_body = self._prepare_email_body(
                campaign.body, 
                tracking_pixel_url, 
                click_tracking_url,
                recipient,
                campaign
            )
            logger.info(f"Prepared email body for {recipient.email}")
            
            # Create message
            logger.info(f"Creating message for {recipient.email}")
            msg = Message(
                subject=campaign.subject,
                sender=(campaign.sender_name, campaign.sender_email),
                recipients=[recipient.email],
                html=email_body
            )
            logger.info(f"Message created for {recipient.email}")
            
            # Attach images if any
            attached_images = campaign.get_attached_images()
            logger.info(f"Attaching {len(attached_images)} images to email for {recipient.email}")
            for i, image in enumerate(attached_images):
                try:
                    logger.info(f"Processing image {i+1}: {image}")
                    # Convert URL path to actual file path
                    if image['url'].startswith('/static/'):
                        file_path = os.path.join(current_app.root_path, image['url'][1:])  # Remove leading slash
                        logger.info(f"Image file path: {file_path}")
                        if os.path.exists(file_path):
                            with open(file_path, 'rb') as img_file:
                                # Create CID for inline image embedding
                                cid = f"image{i+1}"
                                logger.info(f"Attaching image with CID: {cid}")
                                # Use the basic Flask-Mail attach method
                                image_data = img_file.read()
                                msg.attach(
                                    image['filename'],              # filename
                                    'image/jpeg',                   # content_type  
                                    image_data                      # data
                                )
                            logger.info(f"Attached inline image {image['filename']} with CID {cid} to email for {recipient.email}")
                        else:
                            logger.warning(f"Image file not found: {file_path}")
                except Exception as img_error:
                    logger.error(f"Failed to attach image {image.get('filename', 'unknown')}: {str(img_error)}")
                    import traceback
                    logger.error(f"Image attachment traceback: {traceback.format_exc()}")
            
            # Send email
            logger.info(f"Sending email to {recipient.email}")
            mail.send(msg)
            logger.info(f"Email sent successfully to {recipient.email}")
            return True
            
        except Exception as e:
            error_msg = str(e).lower()
            if 'authentication' in error_msg or 'password' in error_msg:
                logger.error(f"Email authentication failed for {recipient.email}. Check MAIL_PASSWORD environment variable.")
            elif 'connection' in error_msg or 'network' in error_msg:
                logger.error(f"Network connection failed for {recipient.email}. Check MAIL_SERVER and MAIL_PORT settings.")
            else:
                logger.error(f"Failed to send email to {recipient.email}: {str(e)}")
            return False
    
    def _prepare_email_body(self, body, tracking_pixel_url, click_tracking_url, recipient, campaign):
        """Prepare email body with tracking elements and embedded images"""
        # Replace placeholder variables
        prepared_body = body.replace('{{recipient_email}}', recipient.email)
        prepared_body = prepared_body.replace('{{tracking_url}}', click_tracking_url)
        
        # Embed images as inline attachments with CID references
        attached_images = campaign.get_attached_images()
        for i, image in enumerate(attached_images):
            # Create CID reference for inline images
            cid = f"image{i+1}"
            image_tag = f'<img src="cid:{cid}" alt="{image["filename"]}" style="max-width: 100%; height: auto;">'
            
            # You can add image placeholders in email body like {{image1}}, {{image2}}, etc.
            prepared_body = prepared_body.replace(f'{{{{image{i+1}}}}}', image_tag)
        
        # If there are images but no explicit placeholders, add them at the end
        if attached_images and not any(f'{{{{image{i+1}}}}}' in body for i in range(len(attached_images))):
            image_section = '<div style="margin-top: 20px;">'
            for i, image in enumerate(attached_images):
                cid = f"image{i+1}"
                image_section += f'<div style="margin-bottom: 10px;"><img src="cid:{cid}" alt="{image["filename"]}" style="max-width: 100%; height: auto;"></div>'
            image_section += '</div>'
            prepared_body += image_section
        
        # Add tracking pixel at the end (invisible)
        tracking_pixel = f'<img src="{tracking_pixel_url}" width="1" height="1" style="display:none;" alt="">'
        
        # Replace any existing links with tracked versions
        # This is a simple implementation - in production you'd want more sophisticated link tracking
        if 'href=' in prepared_body:
            import re
            # Replace href attributes with tracking URLs
            def replace_href(match):
                return f'href="{click_tracking_url}"'
            
            prepared_body = re.sub(r'href="[^"]*"', replace_href, prepared_body)
        
        return prepared_body + tracking_pixel
    
    def _generate_unique_token(self):
        """Generate unique tracking token"""
        return str(uuid.uuid4())
    
    def _generate_tracking_pixel_url(self, token):
        """Generate URL for email open tracking"""
        return f"{self.protocol}://{self.tracking_domain}/track/open/{token}"
    
    def _generate_click_tracking_url(self, token, campaign):
        """Generate URL for click tracking using clone URL if available"""
        # If campaign has an associated clone, use the clone URL
        if campaign.clone_id:
            clone = Clone.query.get(campaign.clone_id)
            if clone and clone.status == 'active':
                # Use the clone's full URL with tracking parameters
                return clone.get_full_url(
                    campaign_id=campaign.id,
                    scenario_id=campaign.scenario_id,
                    token=token
                )
        
        # Fallback to generic tracking URL if no clone is specified
        if campaign.scenario_id:
            return f"{self.protocol}://{self.tracking_domain}/sim/phishing/{campaign.scenario_id}?t={token}&campaign_id={campaign.id}"
        else:
            # Ultimate fallback for campaigns without scenarios
            return f"{self.protocol}://{self.tracking_domain}/track/click/{token}?campaign_id={campaign.id}"
    
    def schedule_campaign(self, campaign):
        """Schedule a campaign for later sending (would integrate with Celery)"""
        # This would integrate with Celery for scheduled sending
        # For now, we'll just mark it as scheduled
        campaign.status = CampaignStatus.SCHEDULED
        db.session.commit()
        
        # In a real implementation, you'd create a Celery task here
        logger.info(f"Campaign {campaign.name} scheduled for {campaign.scheduled_for}")
        return True

class EmailTracker:
    """Utility class for tracking email interactions"""
    
    @staticmethod
    def track_email_open(token, request):
        """Track email open event"""
        try:
            recipient = EmailRecipient.query.filter_by(unique_token=token).first()
            if recipient:
                recipient.mark_opened(
                    ip_address=request.remote_addr,
                    user_agent=request.user_agent.string
                )
                logger.info(f"Email opened by {recipient.email}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to track email open for token {token}: {str(e)}")
            return False
    
    @staticmethod
    def track_email_click(token, request):
        """Track email click event"""
        try:
            recipient = EmailRecipient.query.filter_by(unique_token=token).first()
            if recipient:
                recipient.mark_clicked()
                
                # Also track as an interaction if user is registered
                if recipient.user:
                    from app.models import Interaction
                    from app.models.interaction import InteractionType, InteractionResult
                    
                    interaction = Interaction(
                        user_id=recipient.user.id,
                        scenario_id=recipient.campaign.scenario_id,
                        interaction_type=InteractionType.EMAIL_CLICKED,
                        result=InteractionResult.FELL_FOR_IT,  # Clicked on phishing link
                        detected_threat=False,
                        ip_address=request.remote_addr,
                        user_agent=request.user_agent.string
                    )
                    db.session.add(interaction)
                    db.session.commit()
                
                logger.info(f"Email clicked by {recipient.email}")
                return recipient
            return None
        except Exception as e:
            logger.error(f"Failed to track email click for token {token}: {str(e)}")
            return None
    
    @staticmethod
    def track_email_report(token):
        """Track email report event (user reported as phishing)"""
        try:
            recipient = EmailRecipient.query.filter_by(unique_token=token).first()
            if recipient:
                recipient.mark_reported()
                
                # Also track as an interaction if user is registered
                if recipient.user:
                    from app.models import Interaction
                    from app.models.interaction import InteractionType, InteractionResult
                    
                    interaction = Interaction(
                        user_id=recipient.user.id,
                        scenario_id=recipient.campaign.scenario_id,
                        interaction_type=InteractionType.THREAT_REPORTED,
                        result=InteractionResult.DETECTED,  # Successfully detected threat
                        detected_threat=True,
                        reported_suspicious=True
                    )
                    db.session.add(interaction)
                    db.session.commit()
                
                logger.info(f"Email reported as phishing by {recipient.email}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to track email report for token {token}: {str(e)}")
            return False 