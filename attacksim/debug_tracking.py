#!/usr/bin/env python3
"""
Debug script to test Discord clone tracking integration
Run this to check if tracking is working properly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import EmailCampaign, EmailRecipient, Clone, PhishingCredential
from app.models.clone import CloneStatus

def debug_tracking():
    app = create_app()
    with app.app_context():
        print("🔍 DEBUGGING DISCORD CLONE TRACKING")
        print("=" * 50)
        
        # 1. Check if Discord clone exists and is active
        print("\n1. 📋 Checking Discord Clone Status:")
        discord_clones = Clone.query.filter_by(clone_type='DISCORD', status=CloneStatus.ACTIVE).all()
        
        if not discord_clones:
            print("❌ No active Discord clones found!")
            print("   Create a Discord clone first with URL: https://discord-loginpage.vercel.app/")
            return False
        
        clone = discord_clones[0]
        print(f"✅ Discord clone found: {clone.name}")
        print(f"   URL: {clone.base_url}")
        print(f"   Visits: {clone.total_visits}")
        print(f"   Submissions: {clone.total_submissions}")
        
        # 2. Check recent campaigns
        print("\n2. 📧 Checking Recent Campaigns:")
        campaigns = EmailCampaign.query.order_by(EmailCampaign.created_at.desc()).limit(3).all()
        
        if not campaigns:
            print("❌ No campaigns found!")
            print("   Create a campaign first using the Discord clone")
            return False
        
        print(f"Found {len(campaigns)} recent campaigns:")
        
        for campaign in campaigns:
            print(f"\n   Campaign: {campaign.name}")
            print(f"   ID: {campaign.id}")
            print(f"   Clone ID: {campaign.clone_id}")
            print(f"   Recipients: {campaign.recipients.count()}")
            print(f"   Status: {campaign.status.value}")
            
            # Check recipients
            recipients = campaign.recipients.limit(3).all()
            for recipient in recipients:
                print(f"      📍 {recipient.email}")
                print(f"         Token: {recipient.unique_token}")
                print(f"         Sent: {recipient.sent_at}")
                print(f"         Opened: {recipient.opened_at}")
                print(f"         Clicked: {recipient.clicked_at}")
                
                # Check if this recipient has submitted credentials
                credentials = PhishingCredential.query.filter_by(
                    campaign_id=campaign.id,
                    username_email=recipient.email
                ).all()
                print(f"         Credentials: {len(credentials)} submissions")
        
        # 3. Test tracking URL generation
        print("\n3. 🔗 Testing Tracking URL Generation:")
        latest_campaign = campaigns[0]
        
        if latest_campaign.clone_id == clone.id:
            print(f"✅ Campaign is linked to Discord clone")
            
            # Test URL generation
            test_token = "test-token-123"
            test_url = clone.get_full_url(
                campaign_id=latest_campaign.id,
                scenario_id=latest_campaign.scenario_id,
                token=test_token
            )
            print(f"📍 Sample tracking URL: {test_url}")
            
            # Check if URL has required parameters
            if 'campaign_id' in test_url and 't=' in test_url:
                print("✅ Tracking URL contains required parameters")
            else:
                print("❌ Tracking URL missing parameters")
        else:
            print(f"❌ Campaign clone_id ({latest_campaign.clone_id}) != Discord clone id ({clone.id})")
        
        # 4. Recent credential submissions
        print("\n4. 🎣 Checking Recent Credential Submissions:")
        recent_credentials = PhishingCredential.query.order_by(
            PhishingCredential.submitted_at.desc()
        ).limit(5).all()
        
        print(f"Found {len(recent_credentials)} recent credential submissions:")
        for cred in recent_credentials:
            print(f"   📧 {cred.username_email}")
            print(f"      Campaign: {cred.campaign_id}")
            print(f"      Clone: {cred.clone_id}")
            print(f"      Submitted: {cred.submitted_at}")
            print(f"      IP: {cred.ip_address}")
        
        print("\n" + "=" * 50)
        print("🎯 DEBUGGING SUMMARY:")
        print(f"   Discord Clone: {'✅' if discord_clones else '❌'}")
        print(f"   Campaigns: {'✅' if campaigns else '❌'}")
        print(f"   Recipients: {'✅' if any(c.recipients.count() > 0 for c in campaigns) else '❌'}")
        print(f"   Submissions: {'✅' if recent_credentials else '❌'}")
        
        if not recent_credentials:
            print("\n🔧 NEXT STEPS:")
            print("1. Send a campaign using your Discord clone")
            print("2. Click the email link (should redirect to Discord clone)")
            print("3. Submit fake credentials on the Discord clone")
            print("4. Check analytics - numbers should update")
            print("5. Run this script again to verify")
        
        return True

if __name__ == "__main__":
    debug_tracking() 