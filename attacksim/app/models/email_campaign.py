from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import enum
import json
from app import db

class CampaignStatus(enum.Enum):
    """Status of an email campaign"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENDING = "sending"
    SENT = "sent"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class EmailCampaign(db.Model):
    """Email campaign model for tracking phishing email attacks"""
    __tablename__ = 'email_campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Campaign configuration
    scenario_id = db.Column(db.Integer, db.ForeignKey('scenarios.id'), nullable=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    clone_id = db.Column(db.Integer, db.ForeignKey('clones.id'), nullable=True)  # Associated clone for tracking
    status = db.Column(db.Enum(CampaignStatus), default=CampaignStatus.DRAFT, nullable=False)
    
    # Email details
    subject = db.Column(db.String(300), nullable=False)
    body = db.Column(db.Text, nullable=False)
    sender_name = db.Column(db.String(100), nullable=False)
    sender_email = db.Column(db.String(200), nullable=False)
    
    # Images attached to the email
    attached_images = db.Column(db.Text, nullable=True)  # JSON format: [{"filename": "image.jpg", "url": "/static/images/campaigns/image.jpg"}]
    
    # Tracking URLs and parameters
    tracking_domain = db.Column(db.String(200), nullable=True)
    tracking_enabled = db.Column(db.Boolean, default=True, nullable=False)
    
    # Scheduling
    scheduled_for = db.Column(db.DateTime, nullable=True)
    sent_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Analytics
    total_recipients = db.Column(db.Integer, default=0, nullable=False)
    emails_sent = db.Column(db.Integer, default=0, nullable=False)
    emails_delivered = db.Column(db.Integer, default=0, nullable=False)
    emails_opened = db.Column(db.Integer, default=0, nullable=False)
    emails_clicked = db.Column(db.Integer, default=0, nullable=False)
    emails_reported = db.Column(db.Integer, default=0, nullable=False)
    send_failures = db.Column(db.Integer, default=0, nullable=False)
    
    # Metadata
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Store recipient details as JSON
    recipient_details = db.Column(db.Text, nullable=True)  # JSON format
    
    # Relationships
    scenario = db.relationship('Scenario', backref='email_campaigns')
    # target_group relationship is defined in Group model with backref='target_group'
    clone = db.relationship('Clone', backref='email_campaigns')
    recipients = db.relationship('EmailRecipient', backref='campaign', lazy='dynamic', cascade='all, delete-orphan')
    creator = db.relationship('User', backref='created_campaigns', foreign_keys=[created_by])
    
    def __repr__(self):
        return f'<EmailCampaign {self.name}>'
    
    def get_open_rate(self):
        """Calculate email open rate percentage"""
        if self.emails_sent == 0:
            return 0
        return round((self.emails_opened / self.emails_sent) * 100, 1)
    
    def get_click_rate(self):
        """Calculate email click rate percentage"""
        if self.emails_sent == 0:
            return 0
        return round((self.emails_clicked / self.emails_sent) * 100, 1)
    
    def get_report_rate(self):
        """Calculate email report rate percentage (good behavior)"""
        if self.emails_sent == 0:
            return 0
        return round((self.emails_reported / self.emails_sent) * 100, 1)
    
    def get_delivery_rate(self):
        """Calculate email delivery rate percentage"""
        if self.emails_sent == 0:
            return 0
        return round((self.emails_delivered / self.emails_sent) * 100, 1)
    
    def increment_stat(self, stat_type):
        """Increment a specific statistic"""
        if stat_type == 'opened':
            self.emails_opened += 1
        elif stat_type == 'clicked':
            self.emails_clicked += 1
        elif stat_type == 'reported':
            self.emails_reported += 1
        elif stat_type == 'delivered':
            self.emails_delivered += 1
        elif stat_type == 'failed':
            self.send_failures += 1
        
        db.session.commit()
    
    def mark_sent(self):
        """Mark campaign as sent"""
        self.status = CampaignStatus.SENT
        self.sent_at = datetime.utcnow()
        db.session.commit()
    
    def mark_completed(self):
        """Mark campaign as completed"""
        self.status = CampaignStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        db.session.commit()
    
    def can_be_sent(self):
        """Check if campaign can be sent"""
        # Allow sending campaigns at any status for phishing simulations (enables re-sending)
        return (self.target_group and 
                all([self.subject, self.body, self.sender_email]))
    
    def get_recipient_emails(self):
        """Get all recipient emails for this campaign"""
        if not self.target_group:
            return []
        return self.target_group.get_all_emails()
    
    def get_submission_rate(self):
        """Get credential submission rate for this campaign"""
        recipients_count = self.recipients.count()
        if recipients_count == 0:
            return 0.0
        
        # Get submissions from credentials table
        submitted = 0
        if self.clone_id:
            from app.models.credential import PhishingCredential
            submitted = PhishingCredential.query.filter_by(campaign_id=self.id).count()
        
        # Also check scenario interactions as backup
        if self.scenario_id and submitted == 0:
            from app.models.interaction import InteractionType
            from app.models import Interaction
            scenario_submitted = Interaction.query.filter_by(
                scenario_id=self.scenario_id,
                interaction_type=InteractionType.FORM_SUBMITTED
            ).count()
            submitted = max(submitted, scenario_submitted)
        
        return round((submitted / recipients_count) * 100, 1)
    
    def get_avg_time_to_click(self):
        """Get average time from email open to link click"""
        # Get recipients who both opened and clicked
        recipients = self.recipients.filter(
            EmailRecipient.opened_at.isnot(None),
            EmailRecipient.clicked_at.isnot(None)
        ).all()
        
        if not recipients:
            return 0
        
        total_time = 0
        count = 0
        
        for recipient in recipients:
            time_diff = recipient.clicked_at - recipient.opened_at
            total_time += time_diff.total_seconds() / 60  # Convert to minutes
            count += 1
        
        return round(total_time / count, 1) if count > 0 else 0
    
    def get_detection_rate(self):
        """Get percentage of recipients who reported the email as suspicious"""
        recipients_count = self.recipients.count()
        if recipients_count == 0:
            return 0.0
        
        reported_count = self.recipients.filter(EmailRecipient.reported_at.isnot(None)).count()
        
        # Also check scenario interactions for threat detection
        detected_count = 0
        if self.scenario_id:
            from app.models import Interaction
            detected_count = Interaction.query.filter_by(
                scenario_id=self.scenario_id,
                detected_threat=True
            ).count()
        
        total_detected = max(reported_count, detected_count)
        return round((total_detected / recipients_count) * 100, 1)
    
    def get_repeat_visitors(self):
        """Get number of recipients who clicked multiple times"""
        return self.recipients.filter(EmailRecipient.click_count > 1).count()
    
    def to_dict(self):
        """Convert campaign to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status.value if self.status else None,
            'scenario_name': self.scenario.name if self.scenario else None,
            'group_name': self.target_group.name if self.target_group else None,
            'total_recipients': self.total_recipients,
            'emails_sent': self.emails_sent,
            'emails_delivered': self.emails_delivered,
            'emails_opened': self.emails_opened,
            'emails_clicked': self.emails_clicked,
            'emails_reported': self.emails_reported,
            'send_failures': self.send_failures,
            'open_rate': self.get_open_rate(),
            'click_rate': self.get_click_rate(),
            'report_rate': self.get_report_rate(),
            'delivery_rate': self.get_delivery_rate(),
            'scheduled_for': self.scheduled_for.isoformat() if self.scheduled_for else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def get_attached_images(self):
        """Get list of attached images"""
        if not self.attached_images:
            return []
        try:
            return json.loads(self.attached_images)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def add_attached_image(self, filename, url):
        """Add an attached image"""
        images = self.get_attached_images()
        images.append({"filename": filename, "url": url})
        self.attached_images = json.dumps(images)
    
    def remove_attached_image(self, filename):
        """Remove an attached image"""
        images = self.get_attached_images()
        images = [img for img in images if img.get("filename") != filename]
        self.attached_images = json.dumps(images) if images else None

class EmailRecipient(db.Model):
    """Individual email recipient tracking"""
    __tablename__ = 'email_recipients'
    
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('email_campaigns.id'), nullable=False)
    
    # Recipient details
    email = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # If registered user
    
    # Tracking
    unique_token = db.Column(db.String(100), unique=True, nullable=False)  # For tracking
    sent_at = db.Column(db.DateTime, nullable=True)
    delivered_at = db.Column(db.DateTime, nullable=True)
    opened_at = db.Column(db.DateTime, nullable=True)
    clicked_at = db.Column(db.DateTime, nullable=True)
    reported_at = db.Column(db.DateTime, nullable=True)
    
    # Interaction tracking
    open_count = db.Column(db.Integer, default=0, nullable=False)
    click_count = db.Column(db.Integer, default=0, nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    
    # Status
    send_failed = db.Column(db.Boolean, default=False, nullable=False)
    failure_reason = db.Column(db.String(200), nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='email_recipients')
    
    def __repr__(self):
        return f'<EmailRecipient {self.email}>'
    
    def mark_opened(self, ip_address=None, user_agent=None):
        """Mark email as opened"""
        if not self.opened_at:
            self.opened_at = datetime.utcnow()
        self.open_count += 1
        if ip_address:
            self.ip_address = ip_address
        if user_agent:
            self.user_agent = user_agent
        db.session.commit()
        
        # Update campaign stats
        if self.open_count == 1:  # Only count unique opens
            self.campaign.increment_stat('opened')
    
    def mark_clicked(self):
        """Mark email link as clicked"""
        if not self.clicked_at:
            self.clicked_at = datetime.utcnow()
        self.click_count += 1
        db.session.commit()
        
        # Update campaign stats
        if self.click_count == 1:  # Only count unique clicks
            self.campaign.increment_stat('clicked')
    
    def mark_reported(self):
        """Mark email as reported (good behavior)"""
        self.reported_at = datetime.utcnow()
        db.session.commit()
        
        # Update campaign stats
        self.campaign.increment_stat('reported')
    
    def mark_delivered(self):
        """Mark email as delivered"""
        self.delivered_at = datetime.utcnow()
        db.session.commit()
        
        # Update campaign stats
        self.campaign.increment_stat('delivered')
    
    def mark_failed(self, reason=None):
        """Mark email send as failed"""
        self.send_failed = True
        self.failure_reason = reason
        db.session.commit()
        
        # Update campaign stats
        self.campaign.increment_stat('failed')
    
    def to_dict(self):
        """Convert recipient to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'email': self.email,
            'user_id': self.user_id,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'opened_at': self.opened_at.isoformat() if self.opened_at else None,
            'clicked_at': self.clicked_at.isoformat() if self.clicked_at else None,
            'reported_at': self.reported_at.isoformat() if self.reported_at else None,
            'open_count': self.open_count,
            'click_count': self.click_count,
            'send_failed': self.send_failed,
            'failure_reason': self.failure_reason
        } 