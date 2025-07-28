from datetime import datetime, timedelta
from app import db
from enum import Enum
from sqlalchemy import Enum as SQLEnum

class CloneType(Enum):
    DISCORD = 'DISCORD'
    FACEBOOK = 'FACEBOOK'
    INSTAGRAM = 'INSTAGRAM'
    YOUTUBE = 'YOUTUBE'
    TWITTER = 'TWITTER'
    TWITCH = 'TWITCH'
    GMAIL = 'GMAIL'
    LINKEDIN = 'LINKEDIN'
    PAYPAL = 'PAYPAL'
    BANK = 'BANK'
    OTHER = 'OTHER'

class CloneStatus(Enum):
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    MAINTENANCE = 'MAINTENANCE'

class Clone(db.Model):
    """Model for managing phishing clone URLs"""
    __tablename__ = 'clones'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)  # e.g., "Discord Security Team"
    description = db.Column(db.Text, nullable=True)
    
    # Clone configuration - Use proper SQLAlchemy Enum that maps to PostgreSQL enum
    clone_type = db.Column(SQLEnum(CloneType, name='clonetype'), nullable=False)
    status = db.Column(SQLEnum(CloneStatus, name='clonestatus'), default=CloneStatus.ACTIVE, nullable=False)
    
    # URLs
    base_url = db.Column(db.String(500), nullable=False)  # e.g., "https://discord-clone-tau-smoky.vercel.app"
    landing_path = db.Column(db.String(200), default='/', nullable=False)  # e.g., "/login" or "/"
    
    # Display configuration
    icon = db.Column(db.String(50), default='🌐', nullable=False)  # Emoji icon for display
    button_color = db.Column(db.String(50), default='blue', nullable=False)  # Tailwind color class
    
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
        try:
            self.times_used += 1
            self.last_used = datetime.utcnow()
            db.session.commit()
        except Exception as e:
            print(f"⚠️  Could not increment usage: {e}")
    
    def increment_visit(self):
        """Increment visit counter"""
        try:
            self.total_visits += 1
            db.session.commit()
        except Exception as e:
            print(f"⚠️  Could not increment visit: {e}")
    
    def increment_submission(self):
        """Increment submission counter"""
        try:
            self.total_submissions += 1
            db.session.commit()
        except Exception as e:
            print(f"⚠️  Could not increment submission: {e}")
    
    def get_stats(self):
        """Get clone statistics"""
        try:
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
        except Exception as e:
            print(f"⚠️  Could not get clone stats: {e}")
            # Return basic stats without database queries
            submission_rate = (self.total_submissions / self.total_visits * 100) if self.total_visits > 0 else 0
            return {
                'total_visits': self.total_visits or 0,
                'total_submissions': self.total_submissions or 0,
                'submission_rate': round(submission_rate, 2),
                'recent_credentials': 0,
                'times_used_in_campaigns': self.times_used or 0,
                'last_used': self.last_used.isoformat() if self.last_used else None
            }
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        try:
            stats = self.get_stats()
        except Exception:
            # Fallback stats if get_stats fails
            stats = {
                'total_visits': 0,
                'total_submissions': 0,
                'submission_rate': 0,
                'recent_credentials': 0,
                'times_used_in_campaigns': 0,
                'last_used': None
            }
            
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
            'uses_universal_tracking': self.uses_universal_tracking,
            'times_used': self.times_used,
            'total_visits': self.total_visits,
            'total_submissions': self.total_submissions,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'stats': stats
        }
    
    @staticmethod
    def get_active_clones():
        """Get all active clones"""
        try:
            return Clone.query.filter_by(status=CloneStatus.ACTIVE).order_by(Clone.name).all()
        except Exception as e:
            # Handle case where table doesn't exist yet during initialization
            print(f"⚠️  Could not query clones table: {e}")
            return []
    
    @staticmethod
    def get_clones_by_type(clone_type):
        """Get clones by type"""
        try:
            return Clone.query.filter_by(clone_type=clone_type, status=CloneStatus.ACTIVE).all()
        except Exception as e:
            print(f"⚠️  Could not query clones table: {e}")
            return []
    
    @staticmethod
    def find_by_type_and_url(clone_type, base_url=None):
        """Find clone by type and optionally by URL"""
        try:
            query = Clone.query.filter_by(clone_type=clone_type, status=CloneStatus.ACTIVE)
            if base_url:
                query = query.filter(Clone.base_url.contains(base_url))
            return query.first()
        except Exception as e:
            print(f"⚠️  Could not query clones table: {e}")
            return None
    
    @staticmethod
    def create_clone_from_data(data, user_id):
        """Create a new clone from form data"""
        # Validate clone_type - convert string to enum
        clone_type_str = data.get('clone_type', '').upper()
        try:
            clone_type = CloneType(clone_type_str) if clone_type_str else CloneType.OTHER
        except ValueError:
            # If the provided value is not valid, default to OTHER
            clone_type = CloneType.OTHER
        
        # Validate status - convert string to enum
        status_str = data.get('status', 'ACTIVE').upper()
        try:
            status = CloneStatus(status_str) if status_str else CloneStatus.ACTIVE
        except ValueError:
            # If the provided value is not valid, default to ACTIVE
            status = CloneStatus.ACTIVE
        
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