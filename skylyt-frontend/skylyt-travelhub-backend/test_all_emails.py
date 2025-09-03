#!/usr/bin/env python3
"""
Test all email templates individually to identify issues
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.email_service import EmailService

def test_all_email_templates():
    """Test each email template individually"""
    print("🧪 Testing All Email Templates Individually")
    print("=" * 60)
    
    email_service = EmailService()
    verified_email = "adelodunpeter24@gmail.com"
    
    # Test 1: Welcome Email
    print("\n1. Testing Welcome Email")
    try:
        result = email_service.send_welcome_email(verified_email, "Peter Adelodun")
        print(f"   Result: {'✅ SUCCESS' if result else '❌ FAILED'}")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Test 2: Booking Confirmation
    print("\n2. Testing Booking Confirmation Email")
    try:
        result = email_service.send_booking_confirmation(verified_email, {
            "user_name": "Peter Adelodun",
            "booking_reference": "BK12345678",
            "booking_type": "hotel",
            "hotel_name": "Luxury Hotel Lagos",
            "total_amount": 150000.0,
            "currency": "NGN"
        })
        print(f"   Result: {'✅ SUCCESS' if result else '❌ FAILED'}")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Test 3: Payment Confirmation
    print("\n3. Testing Payment Confirmation Email")
    try:
        result = email_service.send_payment_confirmation(verified_email, {
            "user_name": "Peter Adelodun",
            "booking_reference": "BK12345678",
            "payment_method": "Bank Transfer",
            "amount": 150000.0,
            "currency": "NGN",
            "transaction_id": "TXN123456789"
        })
        print(f"   Result: {'✅ SUCCESS' if result else '❌ FAILED'}")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Test 4: Booking Completion
    print("\n4. Testing Booking Completion Email")
    try:
        result = email_service.send_booking_completion(verified_email, {
            "user_name": "Peter Adelodun",
            "booking_reference": "BK12345678",
            "booking_type": "car",
            "car_name": "Mercedes-Benz E-Class",
            "total_amount": 75000.0,
            "currency": "NGN"
        })
        print(f"   Result: {'✅ SUCCESS' if result else '❌ FAILED'}")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Test 5: Password Reset
    print("\n5. Testing Password Reset Email")
    try:
        result = email_service.send_password_reset(verified_email, "reset_token_123")
        print(f"   Result: {'✅ SUCCESS' if result else '❌ FAILED'}")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")

if __name__ == "__main__":
    test_all_email_templates()