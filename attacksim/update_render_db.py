#!/usr/bin/env python3
"""
Database update script for AttackSim - Adds new tracking system tables
This script adds the PhishingCredential model and enhanced Clone model to your existing Render database
"""

import os
import psycopg
from urllib.parse import urlparse

def update_render_database():
    """Update the Render database with new tracking system tables"""
    
    # Get database URL from environment or prompt user
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        database_url = input("Enter your DATABASE_URL from Render: ")
    
    if not database_url:
        print("❌ DATABASE_URL is required")
        return
    
    print(f"🔗 Connecting to database...")
    
    # Connect to database
    try:
        conn = psycopg.connect(database_url)
        cursor = conn.cursor()
        
        print("✅ Connected to Render database successfully!")
        
        # SQL commands to add new tables and update existing ones
        update_sql = """
        -- Create clones table (new enhanced model)
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
        
        -- Create phishing_credentials table (new model) - FIXED foreign key references
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
        
        -- Add clone_id to email_campaigns table (if not exists)
        DO $$ 
        BEGIN 
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='email_campaign' AND column_name='clone_id') THEN
                ALTER TABLE email_campaign ADD COLUMN clone_id INTEGER REFERENCES clones(id);
                RAISE NOTICE 'Added clone_id column to email_campaign table';
            ELSE
                RAISE NOTICE 'clone_id column already exists in email_campaign table';
            END IF;
        END $$;
        
        -- Add new fields to email_campaigns table (if not exists)
        DO $$ 
        BEGIN 
            -- Add scenario_id
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='email_campaign' AND column_name='scenario_id') THEN
                ALTER TABLE email_campaign ADD COLUMN scenario_id INTEGER REFERENCES scenario(id);
                RAISE NOTICE 'Added scenario_id column to email_campaign table';
            END IF;
            
            -- Add status field with enum-like constraint
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='email_campaign' AND column_name='status') THEN
                ALTER TABLE email_campaign ADD COLUMN status VARCHAR(20) DEFAULT 'draft';
                ALTER TABLE email_campaign ADD CONSTRAINT check_status 
                    CHECK (status IN ('draft', 'scheduled', 'sending', 'sent', 'completed', 'cancelled'));
                RAISE NOTICE 'Added status column to email_campaign table';
            END IF;
            
            -- Add description field
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='email_campaign' AND column_name='description') THEN
                ALTER TABLE email_campaign ADD COLUMN description TEXT;
                RAISE NOTICE 'Added description column to email_campaign table';
            END IF;
            
            -- Add body field
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='email_campaign' AND column_name='body') THEN
                ALTER TABLE email_campaign ADD COLUMN body TEXT;
                RAISE NOTICE 'Added body column to email_campaign table';
            END IF;
            
            -- Add tracking fields
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='email_campaign' AND column_name='tracking_domain') THEN
                ALTER TABLE email_campaign ADD COLUMN tracking_domain VARCHAR(200);
                RAISE NOTICE 'Added tracking_domain column to email_campaign table';
            END IF;
            
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='email_campaign' AND column_name='tracking_enabled') THEN
                ALTER TABLE email_campaign ADD COLUMN tracking_enabled BOOLEAN DEFAULT TRUE;
                RAISE NOTICE 'Added tracking_enabled column to email_campaign table';
            END IF;
            
            -- Add analytics fields
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='email_campaign' AND column_name='total_recipients') THEN
                ALTER TABLE email_campaign ADD COLUMN total_recipients INTEGER DEFAULT 0;
                RAISE NOTICE 'Added total_recipients column to email_campaign table';
            END IF;
            
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='email_campaign' AND column_name='emails_sent') THEN
                ALTER TABLE email_campaign ADD COLUMN emails_sent INTEGER DEFAULT 0;
                RAISE NOTICE 'Added emails_sent column to email_campaign table';
            END IF;
            
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='email_campaign' AND column_name='emails_opened') THEN
                ALTER TABLE email_campaign ADD COLUMN emails_opened INTEGER DEFAULT 0;
                RAISE NOTICE 'Added emails_opened column to email_campaign table';
            END IF;
            
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='email_campaign' AND column_name='emails_clicked') THEN
                ALTER TABLE email_campaign ADD COLUMN emails_clicked INTEGER DEFAULT 0;
                RAISE NOTICE 'Added emails_clicked column to email_campaign table';
            END IF;
            
            -- Add timestamp fields
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='email_campaign' AND column_name='sent_at') THEN
                ALTER TABLE email_campaign ADD COLUMN sent_at TIMESTAMP;
                RAISE NOTICE 'Added sent_at column to email_campaign table';
            END IF;
            
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='email_campaign' AND column_name='updated_at') THEN
                ALTER TABLE email_campaign ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
                RAISE NOTICE 'Added updated_at column to email_campaign table';
            END IF;
        END $$;
        
        -- Create email_recipients table (if not exists)
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
        
        -- Create indexes for performance
        CREATE INDEX IF NOT EXISTS idx_phishing_credentials_campaign_id ON phishing_credentials(campaign_id);
        CREATE INDEX IF NOT EXISTS idx_phishing_credentials_clone_id ON phishing_credentials(clone_id);
        CREATE INDEX IF NOT EXISTS idx_phishing_credentials_tracking_token ON phishing_credentials(tracking_token);
        CREATE INDEX IF NOT EXISTS idx_phishing_credentials_submitted_at ON phishing_credentials(submitted_at);
        CREATE INDEX IF NOT EXISTS idx_email_recipients_token ON email_recipients(unique_token);
        CREATE INDEX IF NOT EXISTS idx_email_recipients_campaign_id ON email_recipients(campaign_id);
        CREATE INDEX IF NOT EXISTS idx_clones_type_status ON clones(clone_type, status);
        
        -- Add constraint to ensure clone_type is valid
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'check_clone_type') THEN
                ALTER TABLE clones ADD CONSTRAINT check_clone_type 
                    CHECK (clone_type IN ('discord', 'facebook', 'google', 'microsoft', 'apple', 'twitter', 'instagram', 'linkedin', 'banking', 'corporate', 'other'));
                RAISE NOTICE 'Added clone_type constraint to clones table';
            END IF;
        END $$;
        
        -- Add constraint to ensure clone status is valid
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'check_clone_status') THEN
                ALTER TABLE clones ADD CONSTRAINT check_clone_status 
                    CHECK (status IN ('active', 'inactive', 'maintenance', 'archived'));
                RAISE NOTICE 'Added status constraint to clones table';
            END IF;
        END $$;
        """
        
        # Execute table creation/updates
        print("🔄 Updating database schema...")
        cursor.execute(update_sql)
        
        # Add some sample clone data (only if admin user exists and no clones exist)
        sample_clones_sql = """
        -- Insert sample clones (only if clones table is empty and admin exists)
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM "user" WHERE id = 1) AND NOT EXISTS (SELECT 1 FROM clones) THEN
                INSERT INTO clones (name, description, clone_type, base_url, landing_path, icon, button_color, created_by)
                VALUES 
                    ('Discord Security Clone', 'Official-looking Discord login page for phishing simulations', 'discord', 
                     'https://your-discord-clone.vercel.app', '/login', '💬', 'purple', 1),
                    ('Facebook Security Check', 'Facebook login verification page for testing', 'facebook', 
                     'https://your-facebook-clone.vercel.app', '/login', '📘', 'blue', 1);
                RAISE NOTICE 'Added sample clones';
            ELSE
                RAISE NOTICE 'Skipped sample clones (admin user missing or clones already exist)';
            END IF;
        END $$;
        """
        
        try:
            cursor.execute(sample_clones_sql)
        except Exception as e:
            print(f"⚠️  Could not add sample clones: {e}")
        
        conn.commit()
        print("✅ Database schema updated successfully!")
        
        # Verify new tables exist
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('clones', 'phishing_credentials', 'email_recipients')
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print(f"✅ Verified new tables exist: {[t[0] for t in tables]}")
        
        # Show current table structure
        cursor.execute("""
            SELECT table_name, column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name IN ('clones', 'phishing_credentials') 
            ORDER BY table_name, ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print(f"✅ New table columns created: {len(columns)} columns")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Database update complete!")
        print("\n📋 Summary of changes:")
        print("✅ Created 'clones' table for clone management")
        print("✅ Created 'phishing_credentials' table for secure credential storage")  
        print("✅ Created 'email_recipients' table for email tracking")
        print("✅ Enhanced 'email_campaign' table with clone linking")
        print("✅ Added performance indexes")
        print("✅ Added data validation constraints")
        
        print("\n🚀 Next steps:")
        print("1. Deploy your updated code to Render")
        print("2. Go to Admin → Clones to add your clone URLs")
        print("3. Create campaigns and select clones for tracking")
        print("4. Test the tracking system!")
        
    except Exception as e:
        print(f"❌ Error updating database: {e}")
        print("Make sure your DATABASE_URL is correct and the database is accessible")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔧 AttackSim Database Update Tool")
    print("This script will add the new tracking system to your existing database")
    print("=" * 60)
    update_render_database() 