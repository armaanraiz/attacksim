#!/usr/bin/env python3
"""
Check Local Database Status
Compares current local database schema with expected schema from table.txt
"""

import os
import sys
import sqlite3
from datetime import datetime

# Add the app to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_sqlite_tables():
    """Check the current SQLite database structure"""
    db_path = 'instance/database.db'
    
    if not os.path.exists(db_path):
        print("❌ No local database found at: instance/database.db")
        print("   Run 'python run.py' first to create the database")
        return False
    
    print(f"📁 Database found: {os.path.abspath(db_path)}")
    print(f"📊 Database size: {os.path.getsize(db_path) / 1024:.1f} KB")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"\n📋 Found {len(tables)} tables:")
        for table in tables:
            print(f"   - {table}")
        
        # Check specific tables and their columns
        expected_tables = {
            'clones': ['id', 'name', 'clone_type', 'status', 'base_url', 'total_visits', 'total_submissions', 'uses_universal_tracking'],
            'email_campaigns': ['id', 'name', 'clone_id', 'subject', 'body', 'status'],
            'email_recipients': ['id', 'campaign_id', 'email', 'unique_token', 'opened_at', 'clicked_at', 'open_count', 'click_count'],
            'phishing_credentials': ['id', 'campaign_id', 'clone_id', 'username_email', 'password_hash', 'submitted_at'],
            'user': ['id', 'email', 'username', 'active', 'consent_given', 'login_count'],
            'groups': ['id', 'name', 'is_active', 'email_list']
        }
        
        print(f"\n🔍 Checking table schemas:")
        missing_tables = []
        missing_columns = {}
        
        for table_name, expected_cols in expected_tables.items():
            if table_name in tables:
                # Get actual columns
                cursor.execute(f"PRAGMA table_info({table_name});")
                actual_cols = [row[1] for row in cursor.fetchall()]
                
                missing_cols = [col for col in expected_cols if col not in actual_cols]
                
                if missing_cols:
                    missing_columns[table_name] = missing_cols
                    print(f"   ⚠️  {table_name}: missing columns {missing_cols}")
                else:
                    print(f"   ✅ {table_name}: all expected columns present")
                    
                # Show record count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                print(f"      📊 Records: {count}")
                
            else:
                missing_tables.append(table_name)
                print(f"   ❌ {table_name}: table missing")
        
        conn.close()
        
        # Summary
        print(f"\n📈 MIGRATION ASSESSMENT:")
        print(f"   Missing tables: {len(missing_tables)}")
        print(f"   Tables with missing columns: {len(missing_columns)}")
        
        if missing_tables or missing_columns:
            print(f"\n🔧 RECOMMENDATION:")
            print(f"   Run: python migrate_local_db.py")
            print(f"   This will update your database to match the current schema")
        else:
            print(f"\n✅ Your database appears to be up to date!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking database: {str(e)}")
        return False

def check_app_models():
    """Check if the app models can be imported and used"""
    try:
        from app import create_app, db
        from app.models import User, Group, Clone, EmailCampaign, EmailRecipient, PhishingCredential
        
        app = create_app()
        with app.app_context():
            print(f"\n🐍 Flask App Status:")
            print(f"   ✅ App created successfully")
            print(f"   ✅ Models imported successfully")
            
            # Try to query each table
            try:
                users = User.query.count()
                print(f"   ✅ Users table accessible: {users} records")
            except Exception as e:
                print(f"   ❌ Users table issue: {str(e)}")
            
            try:
                groups = Group.query.count()
                print(f"   ✅ Groups table accessible: {groups} records")
            except Exception as e:
                print(f"   ❌ Groups table issue: {str(e)}")
                
            try:
                clones = Clone.query.count()
                print(f"   ✅ Clones table accessible: {clones} records")
            except Exception as e:
                print(f"   ❌ Clones table issue: {str(e)}")
                
            try:
                campaigns = EmailCampaign.query.count()
                print(f"   ✅ Campaigns table accessible: {campaigns} records")
            except Exception as e:
                print(f"   ❌ Campaigns table issue: {str(e)}")
                
            try:
                recipients = EmailRecipient.query.count()
                print(f"   ✅ Recipients table accessible: {recipients} records")
            except Exception as e:
                print(f"   ❌ Recipients table issue: {str(e)}")
                
            try:
                credentials = PhishingCredential.query.count()
                print(f"   ✅ Credentials table accessible: {credentials} records")
            except Exception as e:
                print(f"   ❌ Credentials table issue: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Flask App Error: {str(e)}")
        print(f"   This suggests your database schema is incompatible")
        print(f"   Run: python migrate_local_db.py")
        return False

if __name__ == "__main__":
    print("🔍 CHECKING LOCAL DATABASE STATUS")
    print("=" * 50)
    
    # Check SQLite database directly
    sqlite_ok = check_sqlite_tables()
    
    # Check Flask app models
    if sqlite_ok:
        app_ok = check_app_models()
        
        if sqlite_ok and app_ok:
            print(f"\n🎉 Database status check completed!")
        else:
            print(f"\n⚠️  Issues found. Consider running migration.")
    
    print(f"\n💡 Next steps:")
    print(f"   • If migration needed: python migrate_local_db.py")
    print(f"   • To debug tracking: python debug_tracking.py")
    print(f"   • To start app: python run.py") 