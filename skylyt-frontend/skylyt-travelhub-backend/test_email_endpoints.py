#!/usr/bin/env python3
"""
Test script to verify email endpoints functionality
Run: python test_email_endpoints.py
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_email_endpoints():
    print("Testing Email Endpoints...")
    
    # Test 1: Test email service configuration
    try:
        response = requests.post(f"{BASE_URL}/emails/test", 
                               headers={"Authorization": "Bearer YOUR_TOKEN_HERE"})
        print(f"✅ Email test endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Email test failed: {e}")
    
    # Test 2: Send welcome email
    try:
        email_data = {
            "to_email": "test@example.com",
            "email_type": "welcome",
            "data": {"user_name": "Test User"}
        }
        response = requests.post(f"{BASE_URL}/emails/send", 
                               json=email_data,
                               headers={"Authorization": "Bearer ADMIN_TOKEN_HERE"})
        print(f"✅ Send welcome email: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Send email failed: {e}")

if __name__ == "__main__":
    test_email_endpoints()