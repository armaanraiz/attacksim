#!/usr/bin/env python3
"""
Simple email configuration test script for AttackSim
Run this to test if your email settings are working properly.
"""

import os
import sys
from flask import Flask
from flask_mail import Mail, Message
from config import Config

def test_email_config():
    """Test email configuration"""
    
    # Create minimal Flask app
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize mail
    mail = Mail(app)
    
    # Check required environment variables
    mail_password = os.environ.get('MAIL_PASSWORD')
    mail_username = os.environ.get('MAIL_USERNAME', app.config.get('MAIL_USERNAME'))
    
    print("=== Email Configuration Test ===")
    print(f"Mail Server: {app.config.get('MAIL_SERVER')}")
    print(f"Mail Port: {app.config.get('MAIL_PORT')}")
    print(f"Mail Username: {mail_username}")
    print(f"Mail Password: {'Set' if mail_password else 'NOT SET'}")
    print(f"Use TLS: {app.config.get('MAIL_USE_TLS')}")
    
    if not mail_password:
        print("\n❌ ERROR: MAIL_PASSWORD environment variable is not set!")
        print("Please set it with: export MAIL_PASSWORD='your-app-password'")
        return False
    
    if not mail_username:
        print("\n❌ ERROR: MAIL_USERNAME not configured!")
        return False
    
    # Test sending a basic email
    try:
        with app.app_context():
            test_email = input("\nEnter test email address (or press Enter to skip sending): ").strip()
            
            if test_email:
                print(f"\nSending test email to {test_email}...")
                
                msg = Message(
                    subject="AttackSim Email Test",
                    sender=(app.config.get('ADMIN_EMAIL'), mail_username),
                    recipients=[test_email],
                    body="This is a test email from AttackSim. If you received this, your email configuration is working correctly!"
                )
                
                mail.send(msg)
                print("✅ Test email sent successfully!")
                return True
            else:
                print("✅ Configuration looks good (test email skipped)")
                return True
                
    except Exception as e:
        print(f"\n❌ ERROR sending test email: {str(e)}")
        
        error_msg = str(e).lower()
        if 'authentication' in error_msg or 'password' in error_msg:
            print("\n💡 This looks like an authentication error.")
            print("   - Make sure you're using an App Password, not your regular Gmail password")
            print("   - Enable 2-factor authentication on your Gmail account")
            print("   - Generate an App Password at: https://myaccount.google.com/apppasswords")
        elif 'connection' in error_msg:
            print("\n💡 This looks like a connection error.")
            print("   - Check your internet connection")
            print("   - Verify the MAIL_SERVER and MAIL_PORT settings")
        
        return False

if __name__ == "__main__":
    success = test_email_config()
    sys.exit(0 if success else 1) 