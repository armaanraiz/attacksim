from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from app import db
import json

# Association table for group memberships
group_members = db.Table('group_members',
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class Group(db.Model):
    """Group model for managing collections of users for attack campaigns"""
    __tablename__ = 'groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Group configuration
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Email list - store emails as JSON for non-registered users
    email_list = db.Column(db.Text, nullable=True)  # JSON format for external emails
    
    # Relationships
    creator = db.relationship('User', backref='created_groups', foreign_keys=[created_by])
    members = db.relationship('User', secondary=group_members, backref=db.backref('groups', lazy='dynamic'))
    campaigns = db.relationship('EmailCampaign', backref='target_group', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Group {self.name}>'
    
    def get_all_emails(self):
        """Get all emails in this group (both registered users and external emails)"""
        emails = []
        
        # Get emails from registered members
        for member in self.members:
            emails.append(member.email)
        
        # Get external emails from email_list
        if self.email_list:
            try:
                external_emails = json.loads(self.email_list)
                emails.extend(external_emails)
            except (json.JSONDecodeError, TypeError):
                pass
        
        return list(set(emails))  # Remove duplicates
    
    def add_external_emails(self, emails):
        """Add external emails to the group"""
        current_emails = []
        if self.email_list:
            try:
                current_emails = json.loads(self.email_list)
            except (json.JSONDecodeError, TypeError):
                current_emails = []
        
        # Add new emails
        if isinstance(emails, str):
            emails = [emails]
        
        for email in emails:
            if email and email not in current_emails:
                current_emails.append(email.strip().lower())
        
        self.email_list = json.dumps(current_emails)
        db.session.commit()
    
    def remove_external_email(self, email):
        """Remove an external email from the group"""
        if not self.email_list:
            return
        
        try:
            current_emails = json.loads(self.email_list)
            if email in current_emails:
                current_emails.remove(email)
                self.email_list = json.dumps(current_emails)
                db.session.commit()
        except (json.JSONDecodeError, TypeError):
            pass
    
    def get_member_count(self):
        """Get total number of members (registered + external emails)"""
        registered_count = len(self.members)
        external_count = 0
        
        if self.email_list:
            try:
                external_emails = json.loads(self.email_list)
                external_count = len(external_emails)
            except (json.JSONDecodeError, TypeError):
                pass
        
        return registered_count + external_count
    
    def get_external_emails(self):
        """Get list of external emails"""
        if not self.email_list:
            return []
        
        try:
            return json.loads(self.email_list)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def to_dict(self):
        """Convert group to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'member_count': self.get_member_count(),
            'registered_members': len(self.members),
            'external_emails': len(self.get_external_emails()),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 