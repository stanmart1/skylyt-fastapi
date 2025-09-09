#!/usr/bin/env python3
"""Create test account via API"""
import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_account():
    """Create account using registration API"""
    api_url = "https://api.skylytluxury.com/api/v1/auth/register"
    
    user_data = {
        "email": "adelodunpeter24@gmail.com",
        "password": "testpassword123",
        "first_name": "Peter",
        "last_name": "Adelodun"
    }
    
    logger.info(f"Creating account for: {user_data['email']}")
    
    try:
        response = requests.post(
            api_url,
            json=user_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        logger.info(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            logger.info("✅ Account created successfully!")
            logger.info(f"User ID: {result['user']['id']}")
            logger.info(f"Email: {result['user']['email']}")
            logger.info(f"Name: {result['user']['full_name']}")
            logger.info("Check email inbox for welcome message")
        else:
            logger.error(f"❌ Account creation failed: {response.text}")
            
    except Exception as e:
        logger.error(f"❌ Request failed: {e}")

if __name__ == "__main__":
    create_account()