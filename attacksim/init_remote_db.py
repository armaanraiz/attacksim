#!/usr/bin/env python3
"""
Remote database initialization script for AttackSim production deployment
This script can be run from anywhere to initialize your production database
"""

import os
import psycopg
from urllib.parse import urlparse

def init_remote_database():
    """Initialize the remote production database"""
    
    # Get database URL from environment or prompt user
    database_url = input("Enter your DATABASE_URL from Render: ")
    
    if not database_url:
        print("❌ DATABASE_URL is required")
        return
    
    # Parse the database URL
    parsed = urlparse(database_url)
    
    # Connect to database
    try:
        conn = psycopg.connect(database_url)
        cursor = conn.cursor()
        
        print("✅ Connected to database successfully!")
        
        # SQL commands to create tables
        create_tables_sql = """
        -- Create roles table
        CREATE TABLE IF NOT EXISTS role (
            id SERIAL PRIMARY KEY,
            name VARCHAR(80) UNIQUE NOT NULL,
            description TEXT
        );
        
        -- Create users table
        CREATE TABLE IF NOT EXISTS user (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            username VARCHAR(80) UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            department VARCHAR(100),
            phone VARCHAR(20),
            is_admin BOOLEAN DEFAULT FALSE,
            is_active BOOLEAN DEFAULT TRUE,
            consent_given BOOLEAN DEFAULT FALSE,
            consent_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login_at TIMESTAMP,
            current_login_at TIMESTAMP,
            last_login_ip VARCHAR(100),
            current_login_ip VARCHAR(100),
            login_count INTEGER DEFAULT 0,
            confirmed_at TIMESTAMP,
            fs_uniquifier VARCHAR(255) UNIQUE NOT NULL
        );
        
        -- Create groups table
        CREATE TABLE IF NOT EXISTS "group" (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by INTEGER REFERENCES "user"(id)
        );
        
        -- Create email campaigns table
        CREATE TABLE IF NOT EXISTS email_campaign (
            id SERIAL PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            subject VARCHAR(500) NOT NULL,
            sender_name VARCHAR(100) NOT NULL,
            sender_email VARCHAR(255) NOT NULL,
            template_name VARCHAR(100) NOT NULL,
            clone_url VARCHAR(500),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by INTEGER REFERENCES "user"(id),
            group_id INTEGER REFERENCES "group"(id)
        );
        
        -- Create scenarios table
        CREATE TABLE IF NOT EXISTS scenario (
            id SERIAL PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            description TEXT,
            difficulty_level VARCHAR(20) DEFAULT 'medium',
            scenario_type VARCHAR(50) NOT NULL,
            status VARCHAR(20) DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by INTEGER REFERENCES "user"(id)
        );
        
        -- Create interactions table
        CREATE TABLE IF NOT EXISTS interaction (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES "user"(id),
            scenario_id INTEGER REFERENCES scenario(id),
            campaign_id INTEGER REFERENCES email_campaign(id),
            interaction_type VARCHAR(50) NOT NULL,
            success BOOLEAN DEFAULT FALSE,
            ip_address VARCHAR(100),
            user_agent TEXT,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Execute table creation
        cursor.execute(create_tables_sql)
        
        # Create default roles
        cursor.execute("""
            INSERT INTO role (name, description) 
            VALUES ('admin', 'Administrator'), ('user', 'Regular User')
            ON CONFLICT (name) DO NOTHING;
        """)
        
        conn.commit()
        print("✅ Database tables created successfully!")
        print("✅ Default roles created!")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Database initialization complete!")
        print("\nNext steps:")
        print("1. Visit your deployed app URL")
        print("2. Go to /admin/create-admin to create your first admin user")
        print("3. Start creating phishing campaigns!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure your DATABASE_URL is correct and the database is accessible")

if __name__ == "__main__":
    init_remote_database() 