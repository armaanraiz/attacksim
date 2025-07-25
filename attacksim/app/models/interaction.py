from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import enum
from app import db

class InteractionType(enum.Enum):
    """Types of user interactions"""
    EMAIL_OPENED = "email_opened"
    EMAIL_CLICKED = "email_clicked"
    LOGIN_ATTEMPTED = "login_attempted"
    LINK_CLICKED = "link_clicked"
    THREAT_REPORTED = "threat_reported"
    ATTACHMENT_DOWNLOADED = "attachment_downloaded"
    FORM_SUBMITTED = "form_submitted"

class InteractionResult(enum.Enum):
    """Result of the interaction"""
    DETECTED = "detected"          # User successfully identified the threat
    FELL_FOR_IT = "fell_for_it"    # User fell for the attack
    PARTIAL = "partial"            # User was suspicious but not certain
    TIMEOUT = "timeout"            # No interaction within time limit

class Interaction(db.Model):
    """User interaction tracking model"""
    __tablename__ = 'interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    scenario_id = db.Column(db.Integer, db.ForeignKey('scenarios.id'), nullable=False)
    
    # Interaction details
    interaction_type = db.Column(db.Enum(InteractionType), nullable=False)
    result = db.Column(db.Enum(InteractionResult), nullable=False)
    detected_threat = db.Column(db.Boolean, default=False, nullable=False)
    
    # Tracking data
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 compatible
    user_agent = db.Column(db.String(500), nullable=True)
    referrer = db.Column(db.String(500), nullable=True)
    
    # Timing information
    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    response_time = db.Column(db.Integer, nullable=True)  # Response time in seconds
    
    # Interaction specific data
    clicked_url = db.Column(db.String(500), nullable=True)
    submitted_data = db.Column(db.Text, nullable=True)  # JSON format for form data
    email_delivery_id = db.Column(db.String(100), nullable=True)  # For email tracking
    
    # User feedback and learning
    user_feedback = db.Column(db.Text, nullable=True)
    confidence_level = db.Column(db.Integer, nullable=True)  # 1-5 scale of user confidence
    reported_suspicious = db.Column(db.Boolean, default=False, nullable=False)
    
    # Educational interaction
    viewed_education = db.Column(db.Boolean, default=False, nullable=False)
    education_time_spent = db.Column(db.Integer, nullable=True)  # Seconds spent on educational content
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Interaction {self.id}: {self.interaction_type.value} - {self.result.value}>'
    
    def mark_completed(self, result=None):
        """Mark interaction as completed"""
        self.completed_at = datetime.utcnow()
        if self.started_at:
            self.response_time = int((self.completed_at - self.started_at).total_seconds())
        
        if result:
            self.result = result
            self.detected_threat = (result == InteractionResult.DETECTED)
        
        db.session.commit()
    
    def record_education_viewed(self, time_spent=None):
        """Record that user viewed educational content"""
        self.viewed_education = True
        if time_spent:
            self.education_time_spent = time_spent
        db.session.commit()
    
    def record_threat_reported(self, feedback=None):
        """Record that user reported the threat"""
        self.reported_suspicious = True
        self.detected_threat = True
        self.result = InteractionResult.DETECTED
        if feedback:
            self.user_feedback = feedback
        db.session.commit()
    
    def get_response_time_display(self):
        """Get human-readable response time"""
        if not self.response_time:
            return "No response"
        
        if self.response_time < 60:
            return f"{self.response_time} seconds"
        elif self.response_time < 3600:
            minutes = self.response_time // 60
            seconds = self.response_time % 60
            return f"{minutes}m {seconds}s"
        else:
            hours = self.response_time // 3600
            minutes = (self.response_time % 3600) // 60
            return f"{hours}h {minutes}m"
    
    def get_education_time_display(self):
        """Get human-readable education time"""
        if not self.education_time_spent:
            return "Not viewed"
        
        if self.education_time_spent < 60:
            return f"{self.education_time_spent} seconds"
        else:
            minutes = self.education_time_spent // 60
            seconds = self.education_time_spent % 60
            return f"{minutes}m {seconds}s"
    
    def to_dict(self):
        """Convert interaction to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'scenario_id': self.scenario_id,
            'interaction_type': self.interaction_type.value if self.interaction_type else None,
            'result': self.result.value if self.result else None,
            'detected_threat': self.detected_threat,
            'reported_suspicious': self.reported_suspicious,
            'viewed_education': self.viewed_education,
            'response_time': self.response_time,
            'response_time_display': self.get_response_time_display(),
            'education_time_display': self.get_education_time_display(),
            'confidence_level': self.confidence_level,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 