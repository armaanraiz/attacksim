from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
from app import db

# Flask-Security-Too Models
roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    """Role model for Flask-Security-Too"""
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    """User model for Flask-Security-Too authentication"""
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=True)
    password = db.Column(db.String(255))
    
    # Flask-Security-Too required fields
    active = db.Column(db.Boolean(), default=True)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    confirmed_at = db.Column(db.DateTime())
    
    # OAuth fields for Google sign-in
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    
    # User profile information
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    
    # AttackSim specific fields
    consent_given = db.Column(db.Boolean, default=False, nullable=False)
    consent_date = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(100))
    current_login_ip = db.Column(db.String(100))
    login_count = db.Column(db.Integer)
    
    # Relationships
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    interactions = db.relationship('Interaction', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def give_consent(self):
        """Record user consent for attack simulations"""
        self.consent_given = True
        self.consent_date = datetime.utcnow()
        db.session.commit()
    
    def revoke_consent(self):
        """Revoke user consent for attack simulations"""
        self.consent_given = False
        self.consent_date = None
        db.session.commit()
    
    def get_full_name(self):
        """Return user's full name or email if names not provided"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email
    
    def is_admin(self):
        """Check if user has admin role"""
        return self.has_role('admin')
    
    def get_interaction_stats(self):
        """Get user's interaction statistics"""
        total_interactions = self.interactions.count()
        successful_detections = self.interactions.filter_by(detected_threat=True).count()
        failed_detections = total_interactions - successful_detections
        
        detection_rate = 0
        if total_interactions > 0:
            detection_rate = (successful_detections / total_interactions) * 100
        
        return {
            'total_interactions': total_interactions,
            'successful_detections': successful_detections,
            'failed_detections': failed_detections,
            'detection_rate': round(detection_rate, 1)
        }
    
    def to_dict(self):
        """Convert user to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'full_name': self.get_full_name(),
            'department': self.department,
            'is_admin': self.is_admin(),
            'consent_given': self.consent_given,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None
        } 