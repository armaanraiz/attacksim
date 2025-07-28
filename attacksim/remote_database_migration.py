#!/usr/bin/env python3
"""
Remote Database Migration Script for AttackSim

This script safely applies database fixes to hosted/remote databases
with extra precautions for production environments.

Usage:
    python remote_database_migration.py --database-url "postgresql://..." [options]
"""

import os
import sys
import argparse
import subprocess
import psycopg2
from datetime import datetime
from urllib.parse import urlparse
import time

def parse_database_url(database_url):
    """Parse database URL into connection components"""
    parsed = urlparse(database_url)
    return {
        'host': parsed.hostname,
        'port': parsed.port or 5432,
        'database': parsed.path[1:],  # Remove leading slash
        'username': parsed.username,
        'password': parsed.password
    }

def create_remote_backup(database_url, backup_file=None):
    """Create a backup of the remote database"""
    if not backup_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"remote_backup_{timestamp}.sql"
    
    print(f"📁 Creating backup of remote database...")
    print(f"   Backup file: {backup_file}")
    
    try:
        # Use pg_dump with the full database URL
        result = subprocess.run([
            "pg_dump", 
            database_url,
            "--no-password",  # Use URL credentials
            "--verbose",
            "--file", backup_file
        ], capture_output=True, text=True, timeout=600)  # 10 min timeout
        
        if result.returncode == 0:
            # Check backup file size
            size = os.path.getsize(backup_file) / (1024 * 1024)  # Size in MB
            print(f"✅ Backup created successfully: {backup_file} ({size:.1f} MB)")
            return backup_file
        else:
            print(f"❌ Backup failed: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("❌ Backup timed out (database too large or connection slow)")
        return None
    except FileNotFoundError:
        print("❌ pg_dump not found. Install PostgreSQL client tools.")
        print("   macOS: brew install postgresql")
        print("   Ubuntu: sudo apt-get install postgresql-client")
        return None
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None

def test_remote_connection(database_url):
    """Test connection to remote database"""
    print("🔌 Testing remote database connection...")
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Connection successful!")
        print(f"   PostgreSQL version: {version.split(',')[0]}")
        
        # Check database size
        cursor.execute("""
            SELECT pg_size_pretty(pg_database_size(current_database()));
        """)
        db_size = cursor.fetchone()[0]
        print(f"   Database size: {db_size}")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Connection failed: {e}")
        print("\nCommon issues:")
        print("- Check your database URL format")
        print("- Verify firewall/security group settings")
        print("- Ensure your IP is whitelisted")
        return False
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def check_database_activity(database_url):
    """Check for active connections to the database"""
    print("👥 Checking database activity...")
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT count(*) as active_connections,
                   count(CASE WHEN state = 'active' THEN 1 END) as active_queries
            FROM pg_stat_activity 
            WHERE datname = current_database()
            AND pid != pg_backend_pid();
        """)
        
        active_connections, active_queries = cursor.fetchone()
        
        print(f"   Active connections: {active_connections}")
        print(f"   Active queries: {active_queries}")
        
        if active_connections > 5:
            print("⚠️  Warning: High number of active connections")
            print("   Consider running during low-traffic periods")
        
        cursor.close()
        conn.close()
        
        return active_connections, active_queries
        
    except Exception as e:
        print(f"⚠️  Could not check database activity: {e}")
        return 0, 0

def validate_remote_data(database_url):
    """Validate data on remote database before migration"""
    print("🔍 Validating remote database data...")
    
    validation_queries = [
        ("NULL roles_users", "SELECT COUNT(*) FROM roles_users WHERE user_id IS NULL OR role_id IS NULL"),
        ("NULL user fields", 'SELECT COUNT(*) FROM "user" WHERE active IS NULL OR login_count IS NULL'),
        ("Orphaned credentials", "SELECT COUNT(*) FROM phishing_credentials WHERE campaign_id IS NULL AND clone_id IS NULL AND scenario_id IS NULL"),
        ("Invalid emails", 'SELECT COUNT(*) FROM "user" WHERE NOT email ~* \'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$\''),
        ("Negative response times", "SELECT COUNT(*) FROM interactions WHERE response_time < 0")
    ]
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        issues_found = []
        
        for description, query in validation_queries:
            cursor.execute(query)
            count = cursor.fetchone()[0]
            
            if count > 0:
                issues_found.append(f"{description}: {count}")
                print(f"⚠️  {description}: {count} issues found")
            else:
                print(f"✅ {description}: OK")
        
        cursor.close()
        conn.close()
        
        return len(issues_found) == 0, issues_found
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False, [f"Validation error: {e}"]

def apply_migration_to_remote(database_url, sql_file, dry_run=False):
    """Apply the migration to remote database"""
    
    if not os.path.exists(sql_file):
        print(f"❌ SQL file not found: {sql_file}")
        return False
    
    print(f"🔧 {'[DRY RUN] ' if dry_run else ''}Applying migration to remote database...")
    
    try:
        if dry_run:
            print("🔍 DRY RUN - Would execute SQL migration")
            with open(sql_file, 'r') as f:
                content = f.read()
            print(f"   SQL file size: {len(content)} characters")
            print(f"   Contains {content.count(';')} SQL statements")
            return True
        
        # Apply the migration
        result = subprocess.run([
            "psql", 
            database_url,
            "--file", sql_file,
            "--echo-errors"
        ], capture_output=True, text=True, timeout=1800)  # 30 min timeout
        
        if result.returncode == 0:
            print("✅ Migration applied successfully!")
            print("📊 Migration output:")
            # Show last few lines of output
            lines = result.stdout.strip().split('\n')[-10:]
            for line in lines:
                if line.strip():
                    print(f"   {line}")
            return True
        else:
            print(f"❌ Migration failed!")
            print(f"Error output: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Migration timed out")
        return False
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Apply database fixes to remote AttackSim database")
    parser.add_argument("--database-url", required=True, 
                       help="PostgreSQL database URL (e.g., postgresql://user:pass@host:port/dbname)")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show what would be executed without making changes")
    parser.add_argument("--skip-backup", action="store_true", 
                       help="Skip backup creation (NOT recommended for production)")
    parser.add_argument("--force", action="store_true",
                       help="Proceed even with validation warnings")
    parser.add_argument("--backup-file", 
                       help="Custom backup filename")
    
    args = parser.parse_args()
    
    print("🌐 AttackSim Remote Database Migration")
    print("=" * 50)
    
    # Parse and validate database URL
    try:
        db_info = parse_database_url(args.database_url)
        print(f"Target database: {db_info['username']}@{db_info['host']}:{db_info['port']}/{db_info['database']}")
    except Exception as e:
        print(f"❌ Invalid database URL: {e}")
        sys.exit(1)
    
    # Test connection
    if not test_remote_connection(args.database_url):
        print("❌ Cannot connect to remote database")
        sys.exit(1)
    
    print()
    
    # Check database activity
    connections, queries = check_database_activity(args.database_url)
    if queries > 0 and not args.force:
        response = input(f"⚠️  {queries} active queries detected. Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("❌ Migration cancelled")
            sys.exit(1)
    
    print()
    
    # Validate data
    data_valid, issues = validate_remote_data(args.database_url)
    if not data_valid and not args.force:
        print(f"❌ Found {len(issues)} data validation issues:")
        for issue in issues:
            print(f"   - {issue}")
        print("\nOptions:")
        print("1. Fix issues manually in your database")
        print("2. Use --force to proceed anyway (risky)")
        print("3. Run the local validation script with database URL")
        sys.exit(1)
    
    print()
    
    # Create backup
    backup_file = None
    if not args.skip_backup and not args.dry_run:
        backup_file = create_remote_backup(args.database_url, args.backup_file)
        if backup_file is None:
            response = input("⚠️  Backup failed. Continue without backup? (y/N): ")
            if response.lower() != 'y':
                print("❌ Migration cancelled")
                sys.exit(1)
        print()
    
    # Apply migration
    sql_file = "fix_database_issues.sql"
    success = apply_migration_to_remote(args.database_url, sql_file, args.dry_run)
    
    if not success:
        print("❌ Migration failed!")
        if backup_file:
            print(f"💾 Restore from backup: psql '{args.database_url}' < {backup_file}")
        sys.exit(1)
    
    if not args.dry_run:
        print()
        print("🎉 Remote database migration completed successfully!")
        
        # Quick verification
        print("🔍 Running quick verification...")
        time.sleep(2)  # Give database a moment
        data_valid, issues = validate_remote_data(args.database_url)
        
        if data_valid:
            print("✅ Post-migration validation passed!")
        else:
            print("⚠️  Some validation issues remain:")
            for issue in issues:
                print(f"   - {issue}")
    
    print("\n📋 Next steps:")
    print("1. Test your application thoroughly")
    print("2. Monitor database performance")
    print("3. Watch application logs for constraint violations")
    if backup_file and not args.dry_run:
        print(f"4. Keep backup file safe: {backup_file}")
    print("5. Consider running ANALYZE on your database")

if __name__ == "__main__":
    main() 