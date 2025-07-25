from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import enum
from app import db

class ScenarioType(enum.Enum):
    """Types of attack scenarios"""
    PHISHING_EMAIL = "phishing_email"
    FAKE_LOGIN = "fake_login"
    SUSPICIOUS_LINK = "suspicious_link"
    SOCIAL_ENGINEERING = "social_engineering"
    MALICIOUS_ATTACHMENT = "malicious_attachment"

class ScenarioStatus(enum.Enum):
    """Status of a scenario"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class Scenario(db.Model):
    """Attack scenario model for simulations"""
    __tablename__ = 'scenarios'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Scenario configuration
    scenario_type = db.Column(db.Enum(ScenarioType), nullable=False)
    status = db.Column(db.Enum(ScenarioStatus), default=ScenarioStatus.DRAFT, nullable=False)
    difficulty_level = db.Column(db.Integer, default=1, nullable=False)  # 1-5 scale
    
    # Email/Phishing specific fields
    email_subject = db.Column(db.String(200), nullable=True)
    email_body = db.Column(db.Text, nullable=True)
    sender_name = db.Column(db.String(100), nullable=True)
    sender_email = db.Column(db.String(120), nullable=True)
    
    # Website/Login specific fields
    target_website = db.Column(db.String(200), nullable=True)  # e.g., "Facebook", "Bank Login"
    fake_url = db.Column(db.String(500), nullable=True)
    login_template = db.Column(db.String(100), nullable=True)  # Template file name
    
    # Link specific fields
    malicious_url = db.Column(db.String(500), nullable=True)
    link_text = db.Column(db.String(200), nullable=True)
    
    # Educational content
    educational_message = db.Column(db.Text, nullable=True)
    learning_objectives = db.Column(db.Text, nullable=True)
    warning_signs = db.Column(db.Text, nullable=True)  # JSON format for warning signs list
    
    # Targeting and scheduling
    target_users = db.Column(db.Text, nullable=True)  # JSON format for user IDs or criteria
    schedule_start = db.Column(db.DateTime, nullable=True)
    schedule_end = db.Column(db.DateTime, nullable=True)
    
    # Analytics and tracking
    total_sent = db.Column(db.Integer, default=0, nullable=False)
    total_interactions = db.Column(db.Integer, default=0, nullable=False)
    successful_detections = db.Column(db.Integer, default=0, nullable=False)
    
    # Metadata
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    interactions = db.relationship('Interaction', backref='scenario', lazy='dynamic', cascade='all, delete-orphan')
    creator = db.relationship('User', backref='created_scenarios', foreign_keys=[created_by])
    
    def __repr__(self):
        return f'<Scenario {self.name}>'
    
    def get_success_rate(self):
        """Calculate the detection success rate"""
        if self.total_interactions == 0:
            return 0
        return round((self.successful_detections / self.total_interactions) * 100, 1)
    
    def get_failure_rate(self):
        """Calculate the failure rate (fell for the attack)"""
        if self.total_interactions == 0:
            return 0
        failures = self.total_interactions - self.successful_detections
        return round((failures / self.total_interactions) * 100, 1)
    
    def is_active(self):
        """Check if scenario is currently active"""
        now = datetime.utcnow()
        if self.status != ScenarioStatus.ACTIVE:
            return False
        if self.schedule_start and now < self.schedule_start:
            return False
        if self.schedule_end and now > self.schedule_end:
            return False
        return True
    
    def can_be_activated(self):
        """Check if scenario has all required fields for activation"""
        if self.scenario_type == ScenarioType.PHISHING_EMAIL:
            return all([self.email_subject, self.email_body, self.sender_email])
        elif self.scenario_type == ScenarioType.FAKE_LOGIN:
            return all([self.target_website, self.login_template])
        elif self.scenario_type == ScenarioType.SUSPICIOUS_LINK:
            return all([self.malicious_url, self.link_text])
        return True
    
    def increment_stats(self, detected=False):
        """Increment interaction statistics"""
        self.total_interactions += 1
        if detected:
            self.successful_detections += 1
        db.session.commit()
    
    def to_dict(self):
        """Convert scenario to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'scenario_type': self.scenario_type.value if self.scenario_type else None,
            'status': self.status.value if self.status else None,
            'difficulty_level': self.difficulty_level,
            'success_rate': self.get_success_rate(),
            'failure_rate': self.get_failure_rate(),
            'total_sent': self.total_sent,
            'total_interactions': self.total_interactions,
            'successful_detections': self.successful_detections,
            'is_active': self.is_active(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 