from datetime import datetime, timedelta
from app import db
from enum import Enum

class CloneType(Enum):
    DISCORD = 'discord'
    FACEBOOK = 'facebook'
    GOOGLE = 'google'
    MICROSOFT = 'microsoft'
    APPLE = 'apple'
    TWITTER = 'twitter'
    INSTAGRAM = 'instagram'
    LINKEDIN = 'linkedin'
    BANKING = 'banking'
    CORPORATE = 'corporate'
    OTHER = 'other'

class CloneStatus(Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    MAINTENANCE = 'maintenance'
    ARCHIVED = 'archived'

class Clone(db.Model):
    """Model for managing phishing clone URLs"""
    __tablename__ = 'clones'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)  # e.g., "Discord Security Team"
    description = db.Column(db.Text, nullable=True)
    
    # Clone configuration - FIXED: Use String instead of Enum for PostgreSQL compatibility
    clone_type = db.Column(db.String(50), nullable=False)  # Store enum value as string
    status = db.Column(db.String(20), default='active', nullable=False)  # Store enum value as string
    
    # URLs
    base_url = db.Column(db.String(500), nullable=False)  # e.g., "https://discord-clone-tau-smoky.vercel.app"
    landing_path = db.Column(db.String(200), default='/', nullable=False)  # e.g., "/login" or "/"
    
    # Display configuration
    icon = db.Column(db.String(10), default='🌐', nullable=False)  # Emoji icon for display
    button_color = db.Column(db.String(20), default='blue', nullable=False)  # Tailwind color class
    
    # Tracking configuration
    uses_universal_tracking = db.Column(db.Boolean, default=True, nullable=False)  # Whether it uses universal-tracking.js
    custom_tracking_code = db.Column(db.Text, nullable=True)  # Custom tracking implementation if needed
    
    # Analytics
    times_used = db.Column(db.Integer, default=0, nullable=False)
    last_used = db.Column(db.DateTime, nullable=True)
    total_visits = db.Column(db.Integer, default=0, nullable=False)
    total_submissions = db.Column(db.Integer, default=0, nullable=False)
    
    # Metadata
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    creator = db.relationship('User', backref='clones')
    
    def __repr__(self):
        return f'<Clone {self.name}>'
    
    def get_full_url(self, campaign_id=None, scenario_id=None, token=None):
        """Get the full URL with tracking parameters"""
        url = f"{self.base_url.rstrip('/')}{self.landing_path}"
        
        # Add tracking parameters
        params = []
        if campaign_id:
            params.append(f"campaign_id={campaign_id}")
        if scenario_id:
            params.append(f"scenario_id={scenario_id}")
        if token:
            params.append(f"t={token}")
        
        if params:
            url += f"?{'&'.join(params)}"
        
        return url
    
    def get_tracking_script_url(self, backend_url=None):
        """Get URL for the universal tracking script"""
        if backend_url:
            return f"{backend_url}/static/js/universal-tracking.js"
        return "/static/js/universal-tracking.js"
    
    def increment_usage(self):
        """Increment usage counter"""
        self.times_used += 1
        self.last_used = datetime.utcnow()
        db.session.commit()
    
    def increment_visit(self):
        """Increment visit counter"""
        self.total_visits += 1
        db.session.commit()
    
    def increment_submission(self):
        """Increment submission counter"""
        self.total_submissions += 1
        db.session.commit()
    
    def get_stats(self):
        """Get clone statistics"""
        from app.models.credential import PhishingCredential
        
        # Get submission rate
        submission_rate = (self.total_submissions / self.total_visits * 100) if self.total_visits > 0 else 0
        
        # Get recent credentials (last 30 days)
        recent_credentials = PhishingCredential.query.filter_by(clone_id=self.id)\
            .filter(PhishingCredential.submitted_at >= datetime.utcnow() - timedelta(days=30))\
            .count()
        
        return {
            'total_visits': self.total_visits,
            'total_submissions': self.total_submissions,
            'submission_rate': round(submission_rate, 2),
            'recent_credentials': recent_credentials,
            'times_used_in_campaigns': self.times_used,
            'last_used': self.last_used.isoformat() if self.last_used else None
        }
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'clone_type': self.clone_type,
            'status': self.status,
            'base_url': self.base_url,
            'landing_path': self.landing_path,
            'icon': self.icon,
            'button_color': self.button_color,
            'uses_universal_tracking': self.uses_universal_tracking,
            'times_used': self.times_used,
            'total_visits': self.total_visits,
            'total_submissions': self.total_submissions,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'stats': self.get_stats()
        }
    
    @staticmethod
    def get_active_clones():
        """Get all active clones"""
        return Clone.query.filter_by(status='active').order_by(Clone.name).all()
    
    @staticmethod
    def get_clones_by_type(clone_type):
        """Get clones by type"""
        return Clone.query.filter_by(clone_type=clone_type, status='active').all()
    
    @staticmethod
    def find_by_type_and_url(clone_type, base_url=None):
        """Find clone by type and optionally by URL"""
        query = Clone.query.filter_by(clone_type=clone_type, status='active')
        if base_url:
            query = query.filter(Clone.base_url.contains(base_url))
        return query.first()
    
    @staticmethod
    def create_clone_from_data(data, user_id):
        """Create a new clone from form data"""
        # Validate clone_type
        clone_type = data.get('clone_type')
        if clone_type not in [ct.value for ct in CloneType]:
            clone_type = 'other'
        
        # Validate status
        status = data.get('status', 'active')
        if status not in [cs.value for cs in CloneStatus]:
            status = 'active'
        
        clone = Clone(
            name=data.get('name'),
            description=data.get('description', ''),
            clone_type=clone_type,
            status=status,
            base_url=data.get('base_url').rstrip('/'),
            landing_path=data.get('landing_path', '/'),
            icon=data.get('icon', '🌐'),
            button_color=data.get('button_color', 'blue'),
            uses_universal_tracking=data.get('uses_universal_tracking', True),
            created_by=user_id
        )
        return clone 