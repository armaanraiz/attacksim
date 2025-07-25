import secrets
import uuid
from datetime import datetime
from flask import current_app, url_for
from flask_mail import Message
from app import mail, db
from app.models import EmailRecipient, User
import logging

logger = logging.getLogger(__name__)

class PhishingEmailSender:
    """Utility class for sending phishing simulation emails"""
    
    def __init__(self):
        self.tracking_domain = current_app.config.get('TRACKING_DOMAIN', 'localhost:5000')
        self.protocol = 'https' if current_app.config.get('HTTPS_ENABLED', False) else 'http'
    
    def send_campaign(self, campaign):
        """Send emails for an entire campaign"""
        try:
            # Get recipient emails
            recipient_emails = campaign.get_recipient_emails()
            campaign.total_recipients = len(recipient_emails)
            
            # Create recipient records
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
            
            # Send emails to each recipient
            sent_count = 0
            for recipient in recipients_created:
                try:
                    if self._send_single_email(campaign, recipient):
                        sent_count += 1
                        recipient.sent_at = datetime.utcnow()
                        recipient.mark_delivered()  # Assume delivered for now
                    else:
                        recipient.mark_failed("Failed to send email")
                except Exception as e:
                    logger.error(f"Failed to send email to {recipient.email}: {str(e)}")
                    recipient.mark_failed(str(e))
            
            # Update campaign stats
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
            # Generate tracking URLs
            tracking_pixel_url = self._generate_tracking_pixel_url(recipient.unique_token)
            click_tracking_url = self._generate_click_tracking_url(recipient.unique_token, campaign.scenario_id)
            
            # Prepare email body with tracking
            email_body = self._prepare_email_body(
                campaign.body, 
                tracking_pixel_url, 
                click_tracking_url,
                recipient
            )
            
            # Create message
            msg = Message(
                subject=campaign.subject,
                sender=(campaign.sender_name, campaign.sender_email),
                recipients=[recipient.email],
                html=email_body
            )
            
            # Send email
            mail.send(msg)
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {recipient.email}: {str(e)}")
            return False
    
    def _prepare_email_body(self, body, tracking_pixel_url, click_tracking_url, recipient):
        """Prepare email body with tracking elements"""
        # Replace placeholder variables
        prepared_body = body.replace('{{recipient_email}}', recipient.email)
        prepared_body = prepared_body.replace('{{tracking_url}}', click_tracking_url)
        
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
    
    def _generate_click_tracking_url(self, token, scenario_id):
        """Generate URL for click tracking"""
        return f"{self.protocol}://{self.tracking_domain}/sim/phishing/{scenario_id}?t={token}"
    
    def schedule_campaign(self, campaign):
        """Schedule a campaign for later sending (would integrate with Celery)"""
        # This would integrate with Celery for scheduled sending
        # For now, we'll just mark it as scheduled
        from app.models.email_campaign import CampaignStatus
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