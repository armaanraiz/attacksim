from app import db
from datetime import datetime
from enum import Enum

class CloneType(Enum):
    DISCORD = 'discord'
    FACEBOOK = 'facebook'
    INSTAGRAM = 'instagram'
    YOUTUBE = 'youtube'
    TWITTER = 'twitter'
    TWITCH = 'twitch'
    GMAIL = 'gmail'
    LINKEDIN = 'linkedin'
    PAYPAL = 'paypal'
    BANK = 'bank'
    OTHER = 'other'

class CloneStatus(Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    MAINTENANCE = 'maintenance'

class Clone(db.Model):
    """Model for managing phishing clone URLs"""
    __tablename__ = 'clones'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)  # e.g., "Discord Security Team"
    description = db.Column(db.Text, nullable=True)
    
    # Clone configuration
    clone_type = db.Column(db.Enum(CloneType), nullable=False)
    status = db.Column(db.Enum(CloneStatus), default=CloneStatus.ACTIVE, nullable=False)
    
    # URLs
    base_url = db.Column(db.String(500), nullable=False)  # e.g., "https://discord-clone-tau-smoky.vercel.app"
    landing_path = db.Column(db.String(200), default='/', nullable=False)  # e.g., "/login" or "/"
    
    # Display configuration
    icon = db.Column(db.String(10), default='🌐', nullable=False)  # Emoji icon for display
    button_color = db.Column(db.String(20), default='blue', nullable=False)  # Tailwind color class
    
    # Tracking
    times_used = db.Column(db.Integer, default=0, nullable=False)
    last_used = db.Column(db.DateTime, nullable=True)
    
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
    
    def increment_usage(self):
        """Increment usage counter"""
        self.times_used += 1
        self.last_used = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'clone_type': self.clone_type.value if self.clone_type else None,
            'status': self.status.value if self.status else None,
            'base_url': self.base_url,
            'landing_path': self.landing_path,
            'icon': self.icon,
            'button_color': self.button_color,
            'times_used': self.times_used,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def get_active_clones():
        """Get all active clones"""
        return Clone.query.filter_by(status=CloneStatus.ACTIVE).order_by(Clone.name).all()
    
    @staticmethod
    def get_clones_by_type(clone_type):
        """Get clones by type"""
        return Clone.query.filter_by(clone_type=clone_type, status=CloneStatus.ACTIVE).all() 