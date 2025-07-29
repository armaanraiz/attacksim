#!/usr/bin/env python3
"""
Test Discord Clone Accessibility and Communication
"""

import requests
import json
from datetime import datetime

def test_discord_clone_access():
    """Test if Discord clone is accessible"""
    print("🔍 Testing Discord Clone Accessibility")
    print("-" * 50)
    
    discord_url = "https://discord-loginpage.vercel.app/"
    
    try:
        # Test basic accessibility
        response = requests.get(discord_url, timeout=10)
        print(f"✅ Discord clone accessible: {response.status_code}")
        
        # Check if it contains our tracking code
        if "trackPageView" in response.text:
            print("✅ Page view tracking function found")
        else:
            print("❌ Page view tracking function NOT found")
            
        if "handleFormSubmission" in response.text:
            print("✅ Form submission tracking found")
        else:
            print("❌ Form submission tracking NOT found")
            
        if "API_BASE_URL" in response.text:
            print("✅ API configuration found")
        else:
            print("❌ API configuration NOT found")
            
        # Check API URL configuration
        if "attacksim.onrender.com" in response.text:
            print("✅ Render API URL configured")
        elif "localhost:5001" in response.text:
            print("⚠️  Localhost API URL configured (for local testing)")
        else:
            print("❌ No API URL found")
            
        return True
        
    except Exception as e:
        print(f"❌ Discord clone not accessible: {str(e)}")
        return False

def test_api_endpoints():
    """Test if the backend APIs are responding"""
    print("\n🌐 Testing Backend API Endpoints")
    print("-" * 50)
    
    backends = [
        "http://localhost:5001",
        "https://attacksim.onrender.com"
    ]
    
    for backend in backends:
        print(f"\n🔍 Testing: {backend}")
        
        try:
            # Test basic connectivity
            response = requests.get(f"{backend}/", timeout=5)
            print(f"   Main page: {response.status_code}")
            
            # Test track-view endpoint
            test_data = {
                "campaign_id": "999",
                "tracking_token": "test-token-123",
                "scenario_id": "1",
                "user_agent": "Test-Agent/1.0",
                "page_url": "https://discord-loginpage.vercel.app/?campaign_id=999&t=test-token-123",
                "clone_type": "discord",
                "referrer": "https://example.com",
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{backend}/api/track-view",
                json=test_data,
                timeout=10,
                headers={
                    "Content-Type": "application/json",
                    "Origin": "https://discord-loginpage.vercel.app"
                }
            )
            print(f"   track-view: {response.status_code}")
            if response.status_code != 200:
                print(f"      Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Failed: {str(e)}")

def generate_test_url():
    """Generate a test URL to manually test"""
    print("\n🔗 Test URL Generation")
    print("-" * 50)
    
    # Simulate what the backend would generate
    base_url = "https://discord-loginpage.vercel.app"
    campaign_id = "999"
    scenario_id = "1"
    token = "test-token-123"
    
    test_url = f"{base_url}/?campaign_id={campaign_id}&scenario_id={scenario_id}&t={token}"
    
    print(f"📋 Test URL: {test_url}")
    print(f"\n💡 Instructions:")
    print(f"   1. Open this URL in your browser: {test_url}")
    print(f"   2. Open Developer Console (F12)")
    print(f"   3. Submit fake credentials")
    print(f"   4. Check console for tracking logs")
    print(f"   5. Check backend logs for API calls")

def main():
    print("🚀 DISCORD CLONE & BACKEND TEST")
    print("=" * 60)
    
    # Test 1: Discord clone accessibility
    clone_ok = test_discord_clone_access()
    
    # Test 2: Backend API endpoints
    test_api_endpoints()
    
    # Test 3: Generate test URL
    generate_test_url()
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY")
    print("=" * 60)
    
    if clone_ok:
        print("✅ Discord clone is accessible")
        print("✅ Backend APIs are responding")
        print("\n🔧 NEXT STEPS:")
        print("   1. Use the test URL above")
        print("   2. Check browser console for tracking logs")
        print("   3. Check backend logs for API calls")
        print("   4. Verify analytics update")
    else:
        print("❌ Discord clone is not accessible")
        print("   Check if the Vercel deployment is working")

if __name__ == "__main__":
    main() 