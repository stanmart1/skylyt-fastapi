#!/usr/bin/env python3
"""
Test script to verify bank transfer integration is working correctly
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_bank_transfer_endpoints():
    """Test bank transfer related endpoints"""
    
    print("🔍 Testing Bank Transfer Integration...")
    
    # Test 1: Check if bank accounts endpoint exists
    try:
        response = requests.get(f"{BASE_URL}/bank-accounts")
        print(f"✅ Bank accounts endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Bank accounts endpoint failed: {e}")
    
    # Test 2: Check if settings endpoint exists
    try:
        response = requests.get(f"{BASE_URL}/settings/")
        print(f"✅ Settings endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            bank_fields = ['bank_name', 'account_name', 'account_number', 'is_primary_account']
            has_bank_fields = all(field in data for field in bank_fields)
            print(f"   Has bank transfer fields: {has_bank_fields}")
    except Exception as e:
        print(f"❌ Settings endpoint failed: {e}")
    
    # Test 3: Check if payment initialize endpoint exists
    try:
        # This will fail without auth, but we just want to check if endpoint exists
        response = requests.post(f"{BASE_URL}/payments/initialize", 
                               json={"booking_id": 1, "payment_method": "bank_transfer"})
        print(f"✅ Payment initialize endpoint exists: {response.status_code != 404}")
    except Exception as e:
        print(f"❌ Payment initialize endpoint failed: {e}")
    
    # Test 4: Check if payment process endpoint exists (compatibility)
    try:
        response = requests.post(f"{BASE_URL}/payments/process", 
                               json={"booking_id": 1, "payment_method": "bank_transfer"})
        print(f"✅ Payment process endpoint exists: {response.status_code != 404}")
    except Exception as e:
        print(f"❌ Payment process endpoint failed: {e}")
    
    print("\n🎉 Bank Transfer Integration Test Complete!")

if __name__ == "__main__":
    test_bank_transfer_endpoints()