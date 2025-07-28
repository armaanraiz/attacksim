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
    
    def get_discord_analytics(self):
        """Get Discord-specific analytics for this clone"""
        if self.clone_type != CloneType.DISCORD:
            return None
        
        try:
            from app.models.credential import PhishingCredential
            
            # Get all credentials submitted via this clone
            credentials = PhishingCredential.query.filter_by(clone_id=self.id).all()
            
            # Analyze credential patterns
            total_credentials = len(credentials)
            unique_users = len(set(c.username_email for c in credentials if c.username_email))
            
            # Time-based analysis
            recent_7_days = datetime.utcnow() - timedelta(days=7)
            recent_credentials = [c for c in credentials if c.submitted_at >= recent_7_days]
            
            # Success rate analysis
            conversion_rate = (total_credentials / self.total_visits * 100) if self.total_visits > 0 else 0
            
            # Common credential patterns (for educational analysis)
            email_domains = []
            for cred in credentials:
                if cred.username_email and '@' in cred.username_email:
                    domain = cred.username_email.split('@')[1].lower()
                    email_domains.append(domain)
            
            # Count domain frequency
            domain_counts = {}
            for domain in email_domains:
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
            
            # Get top 5 domains
            top_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                'total_credentials': total_credentials,
                'unique_users': unique_users,
                'recent_7_days': len(recent_credentials),
                'conversion_rate': round(conversion_rate, 2),
                'avg_submissions_per_day': round(total_credentials / max(1, (datetime.utcnow() - self.created_at).days), 2),
                'top_email_domains': top_domains,
                'peak_submission_hour': self.get_peak_submission_hour(),
                'effectiveness_score': self.calculate_effectiveness_score()
            }
        except Exception as e:
            print(f"⚠️  Could not get Discord analytics: {e}")
            return None
    
    def get_peak_submission_hour(self):
        """Get the hour of day when most submissions occur"""
        try:
            from app.models.credential import PhishingCredential
            
            credentials = PhishingCredential.query.filter_by(clone_id=self.id).all()
            hour_counts = {}
            
            for cred in credentials:
                hour = cred.submitted_at.hour
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
            
            if not hour_counts:
                return None
            
            peak_hour = max(hour_counts, key=hour_counts.get)
            return f"{peak_hour:02d}:00"
        except Exception:
            return None
    
    def calculate_effectiveness_score(self):
        """Calculate overall effectiveness score (0-100)"""
        try:
            # Factors: conversion rate (40%), usage frequency (30%), recent activity (30%)
            conversion_score = min(100, (self.total_submissions / max(1, self.total_visits)) * 100 * 2)  # Max 50% conversion = 100 points
            
            usage_score = min(100, self.times_used * 10)  # 10 campaigns = 100 points
            
            # Recent activity score
            if self.last_used:
                days_since_used = (datetime.utcnow() - self.last_used).days
                recency_score = max(0, 100 - (days_since_used * 5))  # Lose 5 points per day
            else:
                recency_score = 0
            
            # Weighted average
            effectiveness = (conversion_score * 0.4) + (usage_score * 0.3) + (recency_score * 0.3)
            return round(effectiveness, 1)
        except Exception:
            return 0.0
    
    def get_temporal_analytics(self, days=30):
        """Get time-based analytics for the last N days"""
        try:
            from app.models.credential import PhishingCredential
            
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            credentials = PhishingCredential.query.filter(
                PhishingCredential.clone_id == self.id,
                PhishingCredential.submitted_at >= start_date
            ).all()
            
            # Group by day
            daily_stats = {}
            for i in range(days):
                date = (start_date + timedelta(days=i)).date()
                daily_stats[date] = {
                    'submissions': 0,
                    'unique_users': set()
                }
            
            for cred in credentials:
                date = cred.submitted_at.date()
                if date in daily_stats:
                    daily_stats[date]['submissions'] += 1
                    if cred.username_email:
                        daily_stats[date]['unique_users'].add(cred.username_email)
            
            # Convert to list format for charts
            timeline = []
            for date in sorted(daily_stats.keys()):
                timeline.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'submissions': daily_stats[date]['submissions'],
                    'unique_users': len(daily_stats[date]['unique_users'])
                })
            
            return timeline
        except Exception as e:
            print(f"⚠️  Could not get temporal analytics: {e}")
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