#!/usr/bin/env python3
"""
Initialize Clone Management System
This script creates the clone table and adds the initial Discord clone.
"""

import os
import sys
from datetime import datetime

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Clone, User
from app.models.clone import CloneType, CloneStatus

def init_clones():
    """Initialize the clone management system"""
    app = create_app()
    
    with app.app_context():
        print("Initializing Clone Management System...")
        
        # Create clone table
        try:
            db.create_all()
            print("✓ Clone table created successfully")
        except Exception as e:
            print(f"✗ Error creating clone table: {e}")
            return False
        
        # Check if Discord clone already exists
        existing_discord = Clone.query.filter_by(
            clone_type=CloneType.DISCORD,
            base_url='https://discord-clone-tau-smoky.vercel.app'
        ).first()
        
        if existing_discord:
            print("✓ Discord clone already exists")
            return True
        
        # Get the first admin user to assign as creator
        admin_user = User.query.filter_by(is_admin=True).first()
        if not admin_user:
            print("✗ No admin user found. Please create an admin user first.")
            return False
        
        # Create Discord clone
        try:
            discord_clone = Clone(
                name="Discord Security Team",
                description="Discord clone deployed on Vercel for phishing simulation",
                clone_type=CloneType.DISCORD,
                status=CloneStatus.ACTIVE,
                base_url="https://discord-clone-tau-smoky.vercel.app",
                landing_path="/",
                icon="📱",
                button_color="blue",
                created_by=admin_user.id
            )
            
            db.session.add(discord_clone)
            db.session.commit()
            
            print("✓ Discord clone added successfully!")
            print(f"  - Name: {discord_clone.name}")
            print(f"  - URL: {discord_clone.base_url}{discord_clone.landing_path}")
            print(f"  - Type: {discord_clone.clone_type.value}")
            print(f"  - Status: {discord_clone.status.value}")
            
        except Exception as e:
            print(f"✗ Error adding Discord clone: {e}")
            db.session.rollback()
            return False
        
        print("\n🎉 Clone Management System initialized successfully!")
        print("\nNext steps:")
        print("1. Log in to the admin panel")
        print("2. Go to Admin -> Clone Management")
        print("3. Add more clones as needed")
        print("4. Use clones in your email campaigns")
        
        return True

def add_sample_clones():
    """Add sample clones for testing"""
    app = create_app()
    
    with app.app_context():
        admin_user = User.query.filter_by(is_admin=True).first()
        if not admin_user:
            print("✗ No admin user found")
            return False
        
        sample_clones = [
            {
                'name': 'Facebook Security',
                'description': 'Facebook clone for phishing simulation',
                'clone_type': CloneType.FACEBOOK,
                'base_url': 'https://facebook-clone.vercel.app',
                'icon': '👥',
                'button_color': 'blue'
            },
            {
                'name': 'Gmail Security Alert',
                'description': 'Gmail clone for phishing simulation',
                'clone_type': CloneType.GMAIL,
                'base_url': 'https://gmail-clone.vercel.app',
                'icon': '📧',
                'button_color': 'red'
            },
            {
                'name': 'PayPal Security Center',
                'description': 'PayPal clone for phishing simulation',
                'clone_type': CloneType.PAYPAL,
                'base_url': 'https://paypal-clone.vercel.app',
                'icon': '💳',
                'button_color': 'yellow'
            }
        ]
        
        for clone_data in sample_clones:
            existing = Clone.query.filter_by(
                clone_type=clone_data['clone_type'],
                base_url=clone_data['base_url']
            ).first()
            
            if not existing:
                clone = Clone(
                    name=clone_data['name'],
                    description=clone_data['description'],
                    clone_type=clone_data['clone_type'],
                    status=CloneStatus.INACTIVE,  # Set as inactive since these are placeholders
                    base_url=clone_data['base_url'],
                    landing_path="/",
                    icon=clone_data['icon'],
                    button_color=clone_data['button_color'],
                    created_by=admin_user.id
                )
                
                db.session.add(clone)
                print(f"✓ Added sample clone: {clone_data['name']}")
        
        try:
            db.session.commit()
            print("✓ Sample clones added successfully")
            return True
        except Exception as e:
            print(f"✗ Error adding sample clones: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Initialize Clone Management System')
    parser.add_argument('--samples', action='store_true', 
                       help='Add sample clones for testing')
    
    args = parser.parse_args()
    
    success = init_clones()
    
    if success and args.samples:
        print("\nAdding sample clones...")
        add_sample_clones()
    
    if success:
        print("\n✅ Initialization complete!")
    else:
        print("\n❌ Initialization failed!")
        sys.exit(1) 