#!/usr/bin/env python3
"""
AttackSim - Security Awareness Training Platform
Main application entry point
"""

import os
from app import create_app, db
# Import ALL models to ensure all tables are created
from app.models import (
    User, Role, roles_users,
    Scenario, ScenarioType, ScenarioStatus,
    Interaction, InteractionType, InteractionResult,
    EmailCampaign, EmailRecipient, CampaignStatus,
    Group, group_members,
    Clone, CloneType, CloneStatus,
    PhishingCredential, CredentialType
)
import time
from sqlalchemy import text

# Create Flask application
app = create_app()

# Database migration code removed - schema is now properly structured
# All database constraints and columns are handled by the models

# Auto-create database tables on startup (for Render deployment)
def initialize_database():
    """Initialize database tables only"""
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            print(f"🔄 Initializing database (attempt {attempt + 1}/{max_retries})...")
            
            # First, ensure transaction is clean
            try:
                db.session.rollback()
            except:
                pass
            
            # Create all tables with proper schema
            db.create_all()
            
            # Verify tables were created by doing a simple test query
            try:
                db.session.execute(text("SELECT 1")).fetchone()
                db.session.commit()
                print("✅ Database tables created/updated successfully!")
                return True
                
            except Exception as e:
                db.session.rollback()
                print(f"⚠️  Database verification failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                    
        except Exception as e:
            try:
                db.session.rollback()
            except:
                pass
            print(f"⚠️  Database initialization attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("❌ Database initialization failed after all retries")
                return False
                
    return False

# Global flag to track initialization status
_db_initialized = False

def ensure_database_initialized():
    """Ensure database is initialized before serving requests"""
    global _db_initialized
    if not _db_initialized:
        with app.app_context():
            if initialize_database():
                _db_initialized = True
            else:
                raise RuntimeError("Failed to initialize database")

# Initialize database on app creation (works for all deployment methods)
with app.app_context():
    if initialize_database():
        _db_initialized = True

# Add before_first_request handler to ensure DB is ready
@app.before_request
def ensure_db_ready():
    """Ensure database is ready before handling any request"""
    global _db_initialized
    if not _db_initialized:
        try:
            ensure_database_initialized()
        except Exception as e:
            print(f"❌ Database not ready: {e}")
            # Clean up any bad transactions
            try:
                db.session.rollback()
            except:
                pass

@app.shell_context_processor
def make_shell_context():
    """Make database models available in Flask shell"""
    return {
        'db': db,
        'User': User,
        'Role': Role,
        'Scenario': Scenario,
        'Interaction': Interaction,
        'Clone': Clone,
        'PhishingCredential': PhishingCredential,
        'EmailCampaign': EmailCampaign,
        'EmailRecipient': EmailRecipient,
        'Group': Group
    }

@app.cli.command()
def init_db():
    """Initialize the database with tables"""
    db.create_all()
    print("Database initialized!")

@app.cli.command()
def create_admin():
    """Create an admin user"""
    username = input("Admin username: ")
    email = input("Admin email: ")
    password = input("Admin password: ")
    
    # Check if user already exists
    if User.query.filter_by(username=username).first():
        print(f"User {username} already exists!")
        return
    
    if User.query.filter_by(email=email).first():
        print(f"Email {email} already registered!")
        return
    
    # Create admin user
    admin = User(
        username=username,
        email=email,
        first_name="Admin",
        last_name="User",
        is_admin=True,
        is_active=True
    )
    admin.set_password(password)
    admin.give_consent()  # Admin consents by default
    
    db.session.add(admin)
    db.session.commit()
    
    print(f"Admin user {username} created successfully!")

@app.cli.command()
def create_sample_data():
    """Create sample scenarios and users for testing"""
    from app.models.scenario import ScenarioType, ScenarioStatus
    
    # Create sample users
    test_users = [
        {
            'username': 'testuser1',
            'email': 'test1@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'department': 'IT'
        },
        {
            'username': 'testuser2', 
            'email': 'test2@example.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'department': 'Marketing'
        }
    ]
    
    for user_data in test_users:
        if not User.query.filter_by(username=user_data['username']).first():
            user = User(**user_data)
            user.set_password('password123')
            user.give_consent()
            db.session.add(user)
    
    # Create admin if doesn't exist
    admin = User.query.filter_by(is_admin=True).first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@attacksim.local',
            first_name='Admin',
            last_name='User',
            is_admin=True
        )
        admin.set_password('admin123')
        admin.give_consent()
        db.session.add(admin)
        db.session.commit()
    
    # Create sample scenarios
    scenarios = [
        {
            'name': 'Bank Phishing Email',
            'description': 'Simulates a phishing email from a bank asking users to verify their account',
            'scenario_type': ScenarioType.PHISHING_EMAIL,
            'email_subject': 'Urgent: Verify Your Account',
            'email_body': 'Dear valued customer, we have detected suspicious activity on your account. Please click the link below to verify your identity and secure your account.',
            'sender_name': 'Security Team',
            'sender_email': 'security@bank-example.com',
            'educational_message': 'Banks never ask for personal information via email. Always check the sender address and look for suspicious language.',
            'difficulty_level': 2
        },
        {
            'name': 'Facebook Login Phishing',
            'description': 'Fake Facebook login page to steal credentials',
            'scenario_type': ScenarioType.FAKE_LOGIN,
            'target_website': 'Facebook',
            'login_template': 'facebook',
            'educational_message': 'Always check the URL carefully. Legitimate sites use HTTPS and have the correct domain name.',
            'difficulty_level': 3
        },
        {
            'name': 'Malicious Link Test',
            'description': 'Tests ability to identify suspicious links',
            'scenario_type': ScenarioType.SUSPICIOUS_LINK,
            'malicious_url': 'http://suspicious-site.malware.com/download',
            'link_text': 'Download Free Software',
            'educational_message': 'Be cautious of links offering free downloads or asking you to click immediately. Hover over links to see the real destination.',
            'difficulty_level': 1
        }
    ]
    
    for scenario_data in scenarios:
        if not Scenario.query.filter_by(name=scenario_data['name']).first():
            scenario = Scenario(**scenario_data, created_by=admin.id)
            db.session.add(scenario)
    
    db.session.commit()
    print("Sample data created successfully!")

if __name__ == '__main__':
    # Set environment variables if not set
    if not os.environ.get('FLASK_ENV'):
        os.environ['FLASK_ENV'] = 'development'
    
    if not os.environ.get('SECRET_KEY'):
        os.environ['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    

    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5001) 