#!/usr/bin/env python3
"""
Local Database Migration Script
Updates local SQLite database to match current production PostgreSQL schema
Based on table.txt schema structure
"""

import os
import sys
import sqlite3
from datetime import datetime

# Add the app to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import *
from sqlalchemy import text

def backup_database():
    """Create a backup of the current database before migration"""
    if os.path.exists('instance/database.db'):
        backup_name = f'instance/database_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        import shutil
        shutil.copy2('instance/database.db', backup_name)
        print(f"✅ Database backed up to: {backup_name}")
        return backup_name
    return None

def run_migration():
    """Run the database migration"""
    app = create_app()
    
    with app.app_context():
        print("🔄 MIGRATING LOCAL DATABASE TO CURRENT SCHEMA")
        print("=" * 60)
        
        # Create backup
        backup_file = backup_database()
        
        try:
            # Create all tables with current schema
            print("\n1. Creating/updating tables...")
            db.create_all()
            print("✅ All tables created/updated")
            
            # Run specific migrations for schema changes
            print("\n2. Running schema migrations...")
            
            # Migration 1: Add missing columns to clones table
            try:
                db.session.execute(text("""
                    ALTER TABLE clones ADD COLUMN uses_universal_tracking BOOLEAN DEFAULT TRUE;
                """))
                print("✅ Added uses_universal_tracking to clones")
            except Exception as e:
                if "duplicate column name" not in str(e).lower():
                    print(f"ℹ️  uses_universal_tracking already exists or not needed: {e}")
            
            try:
                db.session.execute(text("""
                    ALTER TABLE clones ADD COLUMN custom_tracking_code TEXT;
                """))
                print("✅ Added custom_tracking_code to clones")
            except Exception as e:
                if "duplicate column name" not in str(e).lower():
                    print(f"ℹ️  custom_tracking_code already exists or not needed: {e}")
            
            try:
                db.session.execute(text("""
                    ALTER TABLE clones ADD COLUMN total_visits INTEGER DEFAULT 0;
                """))
                print("✅ Added total_visits to clones")
            except Exception as e:
                if "duplicate column name" not in str(e).lower():
                    print(f"ℹ️  total_visits already exists or not needed: {e}")
            
            try:
                db.session.execute(text("""
                    ALTER TABLE clones ADD COLUMN total_submissions INTEGER DEFAULT 0;
                """))
                print("✅ Added total_submissions to clones")
            except Exception as e:
                if "duplicate column name" not in str(e).lower():
                    print(f"ℹ️  total_submissions already exists or not needed: {e}")
            
            # Migration 2: Add clone_id to email_campaigns if missing
            try:
                db.session.execute(text("""
                    ALTER TABLE email_campaigns ADD COLUMN clone_id INTEGER;
                """))
                print("✅ Added clone_id to email_campaigns")
            except Exception as e:
                if "duplicate column name" not in str(e).lower():
                    print(f"ℹ️  clone_id already exists or not needed: {e}")
            
            # Migration 3: Ensure email_recipients has all required fields
            required_recipient_columns = [
                ("open_count", "INTEGER DEFAULT 0"),
                ("click_count", "INTEGER DEFAULT 0"),
                ("ip_address", "VARCHAR(45)"),
                ("user_agent", "VARCHAR(500)"),
                ("send_failed", "BOOLEAN DEFAULT FALSE"),
                ("failure_reason", "VARCHAR(200)"),
                ("delivered_at", "TIMESTAMP"),
                ("reported_at", "TIMESTAMP")
            ]
            
            for column_name, column_def in required_recipient_columns:
                try:
                    db.session.execute(text(f"""
                        ALTER TABLE email_recipients ADD COLUMN {column_name} {column_def};
                    """))
                    print(f"✅ Added {column_name} to email_recipients")
                except Exception as e:
                    if "duplicate column name" not in str(e).lower():
                        print(f"ℹ️  {column_name} already exists or not needed: {e}")
            
            # Migration 4: Ensure user table has all required fields
            user_columns = [
                ("consent_given", "BOOLEAN DEFAULT FALSE"),
                ("consent_date", "TIMESTAMP"),
                ("google_id", "VARCHAR(100)"),
                ("first_name", "VARCHAR(50)"),
                ("last_name", "VARCHAR(50)"),
                ("department", "VARCHAR(100)"),
                ("last_login_at", "TIMESTAMP"),
                ("current_login_at", "TIMESTAMP"),
                ("last_login_ip", "VARCHAR(100)"),
                ("current_login_ip", "VARCHAR(100)"),
                ("login_count", "INTEGER DEFAULT 0")
            ]
            
            for column_name, column_def in user_columns:
                try:
                    db.session.execute(text(f"""
                        ALTER TABLE user ADD COLUMN {column_name} {column_def};
                    """))
                    print(f"✅ Added {column_name} to user")
                except Exception as e:
                    if "duplicate column name" not in str(e).lower():
                        print(f"ℹ️  {column_name} already exists or not needed: {e}")
            
            # Migration 5: Ensure groups table has required fields
            try:
                db.session.execute(text("""
                    ALTER TABLE groups ADD COLUMN is_active BOOLEAN DEFAULT TRUE;
                """))
                print("✅ Added is_active to groups")
            except Exception as e:
                if "duplicate column name" not in str(e).lower():
                    print(f"ℹ️  is_active already exists or not needed: {e}")
            
            try:
                db.session.execute(text("""
                    ALTER TABLE groups ADD COLUMN email_list TEXT;
                """))
                print("✅ Added email_list to groups")
            except Exception as e:
                if "duplicate column name" not in str(e).lower():
                    print(f"ℹ️  email_list already exists or not needed: {e}")
            
            # Commit all changes
            db.session.commit()
            print("\n3. ✅ All schema migrations completed successfully!")
            
            # Migration 6: Create sample data if tables are empty
            print("\n4. Checking for sample data...")
            
            # Create admin role if it doesn't exist
            admin_role = Role.query.filter_by(name='admin').first()
            if not admin_role:
                admin_role = Role(name='admin', description='Administrator role')
                db.session.add(admin_role)
                print("✅ Created admin role")
            
            # Create default admin user if no users exist
            if User.query.count() == 0:
                from werkzeug.security import generate_password_hash
                import secrets
                
                admin_user = User(
                    email='admin@attacksim.local',
                    username='admin',
                    password=generate_password_hash('admin123'),
                    active=True,
                    fs_uniquifier=secrets.token_hex(16),
                    consent_given=True,
                    consent_date=datetime.utcnow(),
                    created_at=datetime.utcnow(),
                    login_count=0
                )
                db.session.add(admin_user)
                db.session.flush()  # Get the user ID
                
                # Assign admin role
                admin_user.roles.append(admin_role)
                
                print("✅ Created default admin user (admin@attacksim.local / admin123)")
            
            # Create default group if none exist
            if Group.query.count() == 0:
                admin_user = User.query.filter_by(email='admin@attacksim.local').first()
                if admin_user:
                    default_group = Group(
                        name='Test Users',
                        description='Default group for testing',
                        created_by=admin_user.id,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                        is_active=True,
                        email_list='test1@example.com\ntest2@example.com\ntest3@example.com'
                    )
                    db.session.add(default_group)
                    print("✅ Created default test group")
            
            # Create Discord clone if none exist
            discord_clone = Clone.query.filter_by(clone_type='DISCORD').first()
            if not discord_clone:
                admin_user = User.query.filter_by(email='admin@attacksim.local').first()
                if admin_user:
                    discord_clone = Clone(
                        name='Discord Security Team',
                        description='Discord login page phishing simulation',
                        clone_type='DISCORD',
                        status='ACTIVE',
                        base_url='https://discord-loginpage.vercel.app',
                        landing_path='/',
                        icon='💬',
                        button_color='blue',
                        uses_universal_tracking=True,
                        times_used=0,
                        total_visits=0,
                        total_submissions=0,
                        created_by=admin_user.id,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db.session.add(discord_clone)
                    print("✅ Created Discord clone")
            
            # Create default scenario if none exist
            if Scenario.query.count() == 0:
                admin_user = User.query.filter_by(email='admin@attacksim.local').first()
                if admin_user:
                    default_scenario = Scenario(
                        name='Discord Account Security',
                        description='Test users ability to identify Discord phishing attempts',
                        scenario_type='phishing_email',
                        status='active',
                        difficulty_level=2,
                        email_subject='Discord Account Security Alert',
                        email_body='Your Discord account has been flagged for suspicious activity.',
                        educational_message='This was a phishing simulation! Always verify Discord communications through official channels.',
                        total_sent=0,
                        total_interactions=0,
                        successful_detections=0,
                        created_by=admin_user.id,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db.session.add(default_scenario)
                    print("✅ Created default scenario")
            
            # Final commit
            db.session.commit()
            
            print("\n" + "=" * 60)
            print("🎉 LOCAL DATABASE MIGRATION COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print("\n📊 Current Database Status:")
            print(f"   Users: {User.query.count()}")
            print(f"   Groups: {Group.query.count()}")
            print(f"   Clones: {Clone.query.count()}")
            print(f"   Scenarios: {Scenario.query.count()}")
            print(f"   Campaigns: {EmailCampaign.query.count()}")
            
            print(f"\n🔑 Default Admin Login:")
            print(f"   Email: admin@attacksim.local")
            print(f"   Password: admin123")
            
            print(f"\n📁 Database File: {os.path.abspath('instance/database.db')}")
            if backup_file:
                print(f"📁 Backup File: {os.path.abspath(backup_file)}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Migration failed: {str(e)}")
            db.session.rollback()
            
            if backup_file and os.path.exists(backup_file):
                print(f"\n🔄 Restoring from backup: {backup_file}")
                import shutil
                shutil.copy2(backup_file, 'instance/database.db')
                print("✅ Database restored from backup")
            
            return False

def verify_migration():
    """Verify that the migration was successful"""
    app = create_app()
    
    with app.app_context():
        print("\n🔍 VERIFYING MIGRATION...")
        
        try:
            # Test basic queries
            users = User.query.count()
            groups = Group.query.count()
            clones = Clone.query.count()
            campaigns = EmailCampaign.query.count()
            
            print(f"✅ Users table: {users} records")
            print(f"✅ Groups table: {groups} records")
            print(f"✅ Clones table: {clones} records")
            print(f"✅ Campaigns table: {campaigns} records")
            
            # Test that new columns exist by querying them
            test_user = User.query.first()
            if test_user:
                _ = test_user.consent_given  # This will fail if column doesn't exist
                print("✅ User table new columns accessible")
            
            test_clone = Clone.query.first()
            if test_clone:
                _ = test_clone.total_visits  # This will fail if column doesn't exist
                print("✅ Clone table new columns accessible")
            
            print("✅ Migration verification successful!")
            return True
            
        except Exception as e:
            print(f"❌ Migration verification failed: {str(e)}")
            return False

if __name__ == "__main__":
    print("🚀 Starting Local Database Migration...")
    
    if run_migration():
        if verify_migration():
            print("\n🎉 All done! Your local database is now up to date.")
            print("You can now run: python run.py")
        else:
            print("\n⚠️  Migration completed but verification failed.")
    else:
        print("\n💥 Migration failed. Check the error messages above.") 