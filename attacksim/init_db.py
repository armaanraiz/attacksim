#!/usr/bin/env python3
"""
Database initialization script for AttackSim
Adds the new tables for group management and email campaigns
"""

import os
import sys
from flask import Flask
from app import create_app, db

def init_database():
    """Initialize the database with all tables"""
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        
        # Create all tables
        db.create_all()
        
        print("✅ Database tables created successfully!")
        
        # Create default roles if they don't exist
        try:
            from flask_security import current_app
            user_datastore = current_app.extensions['security'].datastore
            
            if not user_datastore.find_role('admin'):
                user_datastore.create_role(name='admin', description='Administrator')
                print("✅ Admin role created")
            
            if not user_datastore.find_role('user'):
                user_datastore.create_role(name='user', description='Regular User')
                print("✅ User role created")
            
            db.session.commit()
            print("✅ Default roles initialized")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not create default roles: {e}")
        
        print("\n🎉 Database initialization complete!")
        print("\nNext steps:")
        print("1. Run 'python3 run.py create-admin' to create an admin user")
        print("2. Start the application with 'python3 run.py'")

if __name__ == '__main__':
    init_database() 