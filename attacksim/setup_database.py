#!/usr/bin/env python3
"""
Comprehensive Database Setup and Migration
This file handles all database setup, migrations, and fixes in one place.
Can be run through web interface or as a standalone script.
"""

import os
import sys
from datetime import datetime

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_complete_database():
    """Complete database setup including schema creation and enum fixes"""
    try:
        from app import create_app, db
        from app.models import User, Clone
        from sqlalchemy import text, inspect
        
        app = create_app()
        
        with app.app_context():
            print("=== Comprehensive Database Setup ===")
            
            # Detect database type
            inspector = inspect(db.engine)
            dialect_name = db.engine.dialect.name
            print(f"Database type: {dialect_name}")
            
            if dialect_name == 'postgresql':
                return setup_postgresql_database()
            elif dialect_name == 'sqlite':
                return setup_sqlite_database()
            else:
                print(f"Unsupported database type: {dialect_name}")
                return False
                
    except Exception as e:
        print(f"✗ Error during database setup: {e}")
        return False

def setup_postgresql_database():
    """Complete PostgreSQL database setup"""
    from app import db
    from sqlalchemy import text
    
    try:
        print("Setting up PostgreSQL database...")
        
        # Complete SQL setup for PostgreSQL
        setup_sql = """
        -- ===== STEP 1: Clean up old enum types =====
        DO $$
        BEGIN
            -- Drop old enum types if they exist
            IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'clonetype') THEN
                -- Change columns using enum to varchar first
                IF EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='clones' AND column_name='clone_type' 
                          AND data_type='USER-DEFINED') THEN
                    ALTER TABLE clones ALTER COLUMN clone_type TYPE VARCHAR(50);
                END IF;
                DROP TYPE clonetype CASCADE;
                RAISE NOTICE 'Dropped old clonetype enum';
            END IF;
            
            IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'clonestatus') THEN
                IF EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='clones' AND column_name='status' 
                          AND data_type='USER-DEFINED') THEN
                    ALTER TABLE clones ALTER COLUMN status TYPE VARCHAR(20);
                END IF;
                DROP TYPE clonestatus CASCADE;
                RAISE NOTICE 'Dropped old clonestatus enum';
            END IF;
        END $$;
        
        -- ===== STEP 2: Create/Update all tables =====
        
        -- Users table (if not exists)
        CREATE TABLE IF NOT EXISTS "user" (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255),
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            is_admin BOOLEAN DEFAULT FALSE,
            is_active BOOLEAN DEFAULT TRUE,
            confirmed_at TIMESTAMP,
            last_login_at TIMESTAMP,
            current_login_at TIMESTAMP,
            last_login_ip VARCHAR(45),
            current_login_ip VARCHAR(45),
            login_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fs_uniquifier VARCHAR(255) UNIQUE
        );
        
        -- Scenarios table
        CREATE TABLE IF NOT EXISTS scenario (
            id SERIAL PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            description TEXT,
            scenario_type VARCHAR(50) DEFAULT 'phishing',
            difficulty VARCHAR(20) DEFAULT 'medium',
            is_active BOOLEAN DEFAULT TRUE,
            created_by INTEGER REFERENCES "user"(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Clones table (enhanced)
        CREATE TABLE IF NOT EXISTS clones (
            id SERIAL PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            description TEXT,
            clone_type VARCHAR(50) NOT NULL,
            status VARCHAR(20) DEFAULT 'active',
            base_url VARCHAR(500) NOT NULL,
            landing_path VARCHAR(200) DEFAULT '/',
            icon VARCHAR(10) DEFAULT '🌐',
            button_color VARCHAR(20) DEFAULT 'blue',
            uses_universal_tracking BOOLEAN DEFAULT TRUE,
            custom_tracking_code TEXT,
            times_used INTEGER DEFAULT 0,
            last_used TIMESTAMP,
            total_visits INTEGER DEFAULT 0,
            total_submissions INTEGER DEFAULT 0,
            created_by INTEGER REFERENCES "user"(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Email campaigns table (enhanced)
        CREATE TABLE IF NOT EXISTS email_campaign (
            id SERIAL PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            subject VARCHAR(300) NOT NULL,
            description TEXT,
            body TEXT,
            sender_name VARCHAR(100),
            sender_email VARCHAR(255),
            clone_id INTEGER REFERENCES clones(id),
            scenario_id INTEGER REFERENCES scenario(id),
            status VARCHAR(20) DEFAULT 'draft',
            tracking_domain VARCHAR(200),
            tracking_enabled BOOLEAN DEFAULT TRUE,
            total_recipients INTEGER DEFAULT 0,
            emails_sent INTEGER DEFAULT 0,
            emails_opened INTEGER DEFAULT 0,
            emails_clicked INTEGER DEFAULT 0,
            sent_at TIMESTAMP,
            created_by INTEGER REFERENCES "user"(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Email recipients table
        CREATE TABLE IF NOT EXISTS email_recipients (
            id SERIAL PRIMARY KEY,
            campaign_id INTEGER REFERENCES email_campaign(id),
            email VARCHAR(255) NOT NULL,
            user_id INTEGER REFERENCES "user"(id),
            unique_token VARCHAR(100) UNIQUE NOT NULL,
            sent_at TIMESTAMP,
            opened_at TIMESTAMP,
            clicked_at TIMESTAMP,
            ip_address VARCHAR(45),
            user_agent VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Phishing credentials table (enhanced)
        CREATE TABLE IF NOT EXISTS phishing_credentials (
            id SERIAL PRIMARY KEY,
            campaign_id INTEGER REFERENCES email_campaign(id),
            clone_id INTEGER REFERENCES clones(id),
            scenario_id INTEGER REFERENCES scenario(id),
            tracking_token VARCHAR(100),
            user_id INTEGER REFERENCES "user"(id),
            credential_type VARCHAR(50) NOT NULL,
            username_email VARCHAR(255),
            password_hash VARCHAR(255),
            additional_data TEXT,
            clone_type VARCHAR(50),
            source_url VARCHAR(500),
            ip_address VARCHAR(45),
            user_agent VARCHAR(500),
            referrer VARCHAR(500),
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- ===== STEP 3: Add missing columns to existing tables =====
        
        -- Add missing columns to email_campaign if they don't exist
        DO $$ 
        BEGIN 
            -- Clone ID
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='email_campaign' AND column_name='clone_id') THEN
                ALTER TABLE email_campaign ADD COLUMN clone_id INTEGER REFERENCES clones(id);
            END IF;
            
            -- Scenario ID
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='email_campaign' AND column_name='scenario_id') THEN
                ALTER TABLE email_campaign ADD COLUMN scenario_id INTEGER REFERENCES scenario(id);
            END IF;
            
            -- Status
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='email_campaign' AND column_name='status') THEN
                ALTER TABLE email_campaign ADD COLUMN status VARCHAR(20) DEFAULT 'draft';
            END IF;
            
            -- Other fields
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='email_campaign' AND column_name='description') THEN
                ALTER TABLE email_campaign ADD COLUMN description TEXT;
            END IF;
            
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='email_campaign' AND column_name='body') THEN
                ALTER TABLE email_campaign ADD COLUMN body TEXT;
            END IF;
        END $$;
        
        -- ===== STEP 4: Remove old constraints and add proper ones =====
        
        DO $$
        BEGIN
            -- Remove old constraints
            IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'check_clone_type') THEN
                ALTER TABLE clones DROP CONSTRAINT check_clone_type;
            END IF;
            
            IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'check_clone_status') THEN
                ALTER TABLE clones DROP CONSTRAINT check_clone_status;
            END IF;
            
            IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'check_status') THEN
                ALTER TABLE email_campaign DROP CONSTRAINT check_status;
            END IF;
        END $$;
        
        -- Add proper constraints with all valid values
        ALTER TABLE clones ADD CONSTRAINT check_clone_type 
            CHECK (clone_type IN ('discord', 'facebook', 'google', 'microsoft', 'apple', 'twitter', 'instagram', 'linkedin', 'banking', 'corporate', 'other'));
            
        ALTER TABLE clones ADD CONSTRAINT check_clone_status 
            CHECK (status IN ('active', 'inactive', 'maintenance', 'archived'));
            
        ALTER TABLE email_campaign ADD CONSTRAINT check_status 
            CHECK (status IN ('draft', 'scheduled', 'sending', 'sent', 'completed', 'cancelled'));
        
        -- ===== STEP 5: Create indexes for performance =====
        
        CREATE INDEX IF NOT EXISTS idx_phishing_credentials_campaign_id ON phishing_credentials(campaign_id);
        CREATE INDEX IF NOT EXISTS idx_phishing_credentials_clone_id ON phishing_credentials(clone_id);
        CREATE INDEX IF NOT EXISTS idx_phishing_credentials_tracking_token ON phishing_credentials(tracking_token);
        CREATE INDEX IF NOT EXISTS idx_phishing_credentials_submitted_at ON phishing_credentials(submitted_at);
        CREATE INDEX IF NOT EXISTS idx_email_recipients_token ON email_recipients(unique_token);
        CREATE INDEX IF NOT EXISTS idx_email_recipients_campaign_id ON email_recipients(campaign_id);
        CREATE INDEX IF NOT EXISTS idx_clones_type_status ON clones(clone_type, status);
        CREATE INDEX IF NOT EXISTS idx_user_email ON "user"(email);
        CREATE INDEX IF NOT EXISTS idx_email_campaign_status ON email_campaign(status);
        """
        
        print("Executing comprehensive database setup...")
        db.session.execute(text(setup_sql))
        db.session.commit()
        
        print("✓ PostgreSQL database setup completed successfully")
        
        # Add sample data if needed
        add_initial_data()
        
        return True
        
    except Exception as e:
        print(f"✗ PostgreSQL setup error: {e}")
        db.session.rollback()
        return False

def setup_sqlite_database():
    """Complete SQLite database setup"""
    from app import db
    
    try:
        print("Setting up SQLite database...")
        
        # Create all tables
        db.create_all()
        print("✓ SQLite tables created")
        
        # Add sample data if needed
        add_initial_data()
        
        print("✓ SQLite database setup completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ SQLite setup error: {e}")
        return False

def add_initial_data():
    """Add initial data to the database"""
    from app import db
    from app.models import User, Clone
    from werkzeug.security import generate_password_hash
    
    try:
        # Create admin user if it doesn't exist
        admin_user = User.query.filter_by(email='admin@attacksim.com').first()
        if not admin_user:
            admin_user = User(
                email='admin@attacksim.com',
                password=generate_password_hash('admin123'),
                first_name='System',
                last_name='Administrator',
                is_admin=True,
                is_active=True,
                fs_uniquifier='admin-unique-id'
            )
            db.session.add(admin_user)
            db.session.commit()
            print("✓ Created admin user (admin@attacksim.com / admin123)")
        
        # Create sample Discord clone if it doesn't exist
        discord_clone = Clone.query.filter_by(clone_type='discord').first()
        if not discord_clone:
            discord_clone = Clone(
                name='Discord Security Team',
                description='Official-looking Discord login page for phishing simulations',
                clone_type='discord',
                base_url='https://discord-loginpage.vercel.app',
                landing_path='/',
                icon='💬',
                button_color='purple',
                created_by=admin_user.id
            )
            db.session.add(discord_clone)
            db.session.commit()
            print("✓ Created sample Discord clone")
        
    except Exception as e:
        print(f"⚠️  Could not add initial data: {e}")

# Web interface trigger
def trigger_database_setup():
    """Function that can be called from the web interface"""
    return setup_complete_database()

if __name__ == '__main__':
    print("=== AttackSim Database Setup ===")
    success = setup_complete_database()
    
    if success:
        print("\n🎉 Database setup completed successfully!")
        print("\nNext steps:")
        print("1. Try creating a Discord clone through /admin/clones/create")
        print("2. Login with admin@attacksim.com / admin123")
        print("3. Check that all features work properly")
    else:
        print("\n❌ Database setup failed.")
        print("Check the error messages above for troubleshooting.")
    
    sys.exit(0 if success else 1) 