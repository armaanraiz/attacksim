#!/usr/bin/env python3
"""
Test script for end-to-end phishing tracking integration

This script tests the complete flow:
1. Create a clone
2. Create an email campaign linked to the clone  
3. Generate tracking URLs
4. Simulate form submission
5. Verify data is stored correctly

Run this script to test the tracking system.
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app import create_app, db
from app.models import Clone, EmailCampaign, PhishingCredential, Scenario, Group, User
from app.models.clone import CloneType, CloneStatus
from app.models.email_campaign import CampaignStatus
from app.utils.email_sender import PhishingEmailSender
import uuid
from datetime import datetime

def test_tracking_integration():
    """Test the complete tracking integration"""
    
    print("🚀 Testing Phishing Tracking Integration...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # 1. Create a test clone
            print("\n1. Creating test clone...")
            test_clone = Clone(
                name="Test Discord Clone",
                description="Test clone for tracking integration",
                clone_type=CloneType.DISCORD,
                status=CloneStatus.ACTIVE,
                base_url="https://discord-clone-test.vercel.app",
                landing_path="/login",
                icon="💬",
                button_color="purple",
                uses_universal_tracking=True,
                created_by=1  # Assume admin user exists
            )
            
            db.session.add(test_clone)
            db.session.commit()
            print(f"✅ Created clone: {test_clone.name} (ID: {test_clone.id})")
            
            # 2. Create a test scenario
            print("\n2. Creating test scenario...")
            test_scenario = Scenario(
                name="Discord Security Test",
                description="Test scenario for tracking",
                scenario_type="phishing_email",
                status="active",
                email_subject="Verify Your Discord Account",
                email_body="Please verify your account by clicking the link below.",
                educational_message="This was a test! Always verify Discord URLs carefully.",
                created_by=1
            )
            
            db.session.add(test_scenario)
            db.session.commit()
            print(f"✅ Created scenario: {test_scenario.name} (ID: {test_scenario.id})")
            
            # 3. Create a test group (if doesn't exist)
            print("\n3. Creating test group...")
            test_group = Group.query.filter_by(name="Test Group").first()
            if not test_group:
                test_group = Group(
                    name="Test Group",
                    description="Test group for tracking",
                    created_by=1
                )
                db.session.add(test_group)
                db.session.commit()
            print(f"✅ Using group: {test_group.name} (ID: {test_group.id})")
            
            # 4. Create a test email campaign linked to the clone
            print("\n4. Creating test email campaign...")
            test_campaign = EmailCampaign(
                name="Test Tracking Campaign",
                description="Test campaign for tracking integration",
                scenario_id=test_scenario.id,
                group_id=test_group.id,
                clone_id=test_clone.id,  # Link to our test clone
                status=CampaignStatus.DRAFT,
                subject="Verify Your Discord Account",
                body="Please verify your account by clicking the link below: {{tracking_url}}",
                sender_name="Discord Security",
                sender_email="security@discord.com",
                tracking_domain="attacksim.onrender.com",
                created_by=1
            )
            
            db.session.add(test_campaign)
            db.session.commit()
            print(f"✅ Created campaign: {test_campaign.name} (ID: {test_campaign.id})")
            
            # 5. Test URL generation with clone integration
            print("\n5. Testing URL generation...")
            sender = PhishingEmailSender()
            
            # Generate a test tracking token
            test_token = str(uuid.uuid4())
            
            # Test the new clone-integrated URL generation
            tracking_url = sender._generate_click_tracking_url(test_token, test_campaign)
            print(f"✅ Generated tracking URL: {tracking_url}")
            
            # Verify the URL contains clone base_url
            if test_clone.base_url in tracking_url:
                print("✅ URL correctly uses clone base URL")
            else:
                print("❌ URL does not use clone base URL")
                return False
            
            # Verify tracking parameters are included
            expected_params = ['campaign_id', 't', 'scenario_id']
            for param in expected_params:
                if param in tracking_url:
                    print(f"✅ URL contains {param} parameter")
                else:
                    print(f"❌ URL missing {param} parameter")
                    return False
            
            # 6. Simulate credential submission
            print("\n6. Simulating credential submission...")
            
            # Create test credential data
            credential_data = {
                'campaign_id': test_campaign.id,
                'clone_id': test_clone.id,
                'scenario_id': test_scenario.id,
                'tracking_token': test_token,
                'credential_type': 'email_password',
                'email': 'testuser@example.com',
                'password': 'testpassword123',
                'clone_type': 'discord',
                'page_url': tracking_url,
                'ip_address': '192.168.1.100',
                'user_agent': 'Mozilla/5.0 (Test Browser)',
                'referrer': 'https://example.com/email'
            }
            
            # Create credential record
            credential = PhishingCredential.create_credential_record(credential_data)
            db.session.add(credential)
            db.session.commit()
            
            print(f"✅ Created credential record (ID: {credential.id})")
            
            # 7. Verify data relationships
            print("\n7. Verifying data relationships...")
            
            # Check clone has credentials
            clone_credentials = PhishingCredential.get_clone_credentials(test_clone.id)
            if clone_credentials:
                print(f"✅ Clone has {len(clone_credentials)} credential(s)")
            else:
                print("❌ Clone has no credentials")
                return False
            
            # Check campaign has credentials
            campaign_credentials = PhishingCredential.get_campaign_credentials(test_campaign.id)
            if campaign_credentials:
                print(f"✅ Campaign has {len(campaign_credentials)} credential(s)")
            else:
                print("❌ Campaign has no credentials")
                return False
            
            # Check password is hashed
            if credential.password_hash and credential.password_hash != credential_data['password']:
                print("✅ Password is properly hashed")
            else:
                print("❌ Password is not hashed")
                return False
            
            # 8. Test clone statistics
            print("\n8. Testing clone statistics...")
            
            # Simulate visits and submissions
            test_clone.increment_visit()
            test_clone.increment_submission()
            
            stats = test_clone.get_stats()
            print(f"✅ Clone stats: {stats}")
            
            # 9. Test to_dict methods
            print("\n9. Testing serialization...")
            
            clone_dict = test_clone.to_dict()
            credential_dict = credential.to_dict()
            
            print(f"✅ Clone serializes to: {len(clone_dict)} fields")
            print(f"✅ Credential serializes to: {len(credential_dict)} fields")
            
            # 10. Clean up test data
            print("\n10. Cleaning up test data...")
            
            db.session.delete(credential)
            db.session.delete(test_campaign)
            db.session.delete(test_scenario)
            db.session.delete(test_clone)
            db.session.commit()
            
            print("✅ Test data cleaned up")
            
            print("\n🎉 All tests passed! Tracking integration is working correctly.")
            return True
            
        except Exception as e:
            print(f"\n❌ Test failed with error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = test_tracking_integration()
    sys.exit(0 if success else 1) 