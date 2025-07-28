from datetime import datetime
from app import db
from enum import Enum
import hashlib
import json

class CredentialType(Enum):
    EMAIL_PASSWORD = 'email_password'
    USERNAME_PASSWORD = 'username_password'
    SOCIAL_MEDIA = 'social_media'
    BANKING = 'banking'
    CORPORATE = 'corporate'
    OTHER = 'other'

class PhishingCredential(db.Model):
    """Model for storing credentials collected from phishing attacks"""
    __tablename__ = 'phishing_credentials'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Tracking information - FIXED: Use correct table names
    campaign_id = db.Column(db.Integer, db.ForeignKey('email_campaigns.id'), nullable=True)  # Fixed: email_campaigns not email_campaign
    clone_id = db.Column(db.Integer, db.ForeignKey('clones.id'), nullable=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey('scenarios.id'), nullable=True)  # Fixed: scenarios not scenario
    tracking_token = db.Column(db.String(100), nullable=True)
    
    # User information (if known)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Credential data (hashed for security) - FIXED: Use String instead of Enum for PostgreSQL compatibility
    credential_type = db.Column(db.String(50), nullable=False)  # Store enum value as string
    username_email = db.Column(db.String(255), nullable=True)  # Username or email entered
    password_hash = db.Column(db.String(255), nullable=True)  # Hashed password
    additional_data = db.Column(db.Text, nullable=True)  # JSON for any additional form fields
    
    # Clone/Source information
    clone_type = db.Column(db.String(50), nullable=True)  # 'discord', 'facebook', etc.
    source_url = db.Column(db.String(500), nullable=True)
    
    # Request metadata
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    referrer = db.Column(db.String(500), nullable=True)
    
    # Timestamps
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships - FIXED: Use correct table names
    campaign = db.relationship('EmailCampaign', backref='collected_credentials')
    clone = db.relationship('Clone', backref='collected_credentials')
    scenario = db.relationship('Scenario', backref='collected_credentials')
    user = db.relationship('User', backref='phishing_credentials_submitted')
    
    def __repr__(self):
        return f'<PhishingCredential {self.id}: {self.clone_type} - {self.username_email[:20] if self.username_email else "None"}...>'
    
    @staticmethod
    def hash_password(password):
        """Hash password using SHA-256 (for demonstration - use bcrypt in production)"""
        if not password:
            return None
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    @staticmethod
    def create_credential_record(data):
        """Create a new credential record from form submission data"""
        # Validate credential_type
        credential_type = data.get('credential_type', 'email_password')
        valid_credential_types = ['email_password', 'username_password', 'social_media', 'banking', 'corporate', 'other']
        if credential_type not in valid_credential_types:
            credential_type = 'email_password'
        
        credential = PhishingCredential(
            campaign_id=data.get('campaign_id'),
            clone_id=data.get('clone_id'),
            scenario_id=data.get('scenario_id'),
            tracking_token=data.get('tracking_token'),
            credential_type=credential_type,  # Store as string value
            username_email=data.get('email') or data.get('username'),
            password_hash=PhishingCredential.hash_password(data.get('password')),
            additional_data=json.dumps(data.get('additional_data', {})),
            clone_type=data.get('clone_type'),
            source_url=data.get('page_url'),
            ip_address=data.get('ip_address'),
            user_agent=data.get('user_agent'),
            referrer=data.get('referrer')
        )
        
        # Try to link to existing user if possible
        if credential.username_email:
            from app.models.user import User
            user = User.query.filter_by(email=credential.username_email).first()
            if user:
                credential.user_id = user.id
        
        return credential
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'clone_id': self.clone_id,
            'scenario_id': self.scenario_id,
            'credential_type': self.credential_type,
            'username_email': self.username_email,
            'clone_type': self.clone_type,
            'source_url': self.source_url,
            'ip_address': self.ip_address,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None
        }
    
    @staticmethod
    def get_campaign_credentials(campaign_id):
        """Get all credentials collected for a specific campaign"""
        return PhishingCredential.query.filter_by(campaign_id=campaign_id).order_by(PhishingCredential.submitted_at.desc()).all()
    
    @staticmethod
    def get_clone_credentials(clone_id):
        """Get all credentials collected from a specific clone"""
        return PhishingCredential.query.filter_by(clone_id=clone_id).order_by(PhishingCredential.submitted_at.desc()).all() 