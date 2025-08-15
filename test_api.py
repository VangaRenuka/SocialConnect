#!/usr/bin/env python3
"""
Test script for SocialConnect API endpoints
"""

import requests
import json
import time

# Base URL
BASE_URL = "http://127.0.0.1:8000/api"

def test_user_registration():
    """Test user registration endpoint"""
    print("Testing User Registration...")
    
    # Use timestamp to make username/email unique
    timestamp = int(time.time())
    username = f"testuser{timestamp}"
    email = f"test{timestamp}@example.com"
    
    url = f"{BASE_URL}/auth/register/"
    data = {
        "username": username,
        "email": email,
        "password": "testpass123",
        "password_confirm": "testpass123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response, username, email
    except Exception as e:
        print(f"Error: {e}")
        return None, None, None

def test_user_login(username):
    """Test user login endpoint"""
    print("\nTesting User Login...")
    
    url = f"{BASE_URL}/auth/login/"
    data = {
        "email_or_username": username,
        "password": "testpass123"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_protected_endpoint(token):
    """Test a protected endpoint with authentication"""
    print(f"\nTesting Protected Endpoint with token...")
    
    url = f"{BASE_URL}/users/"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    print("=== SocialConnect API Testing ===\n")
    
    # Test registration
    reg_response, username, email = test_user_registration()
    
    if reg_response and reg_response.status_code == 201:
        print("✅ Registration successful!")
        
        # Test login
        login_response = test_user_login(username)
        
        if login_response and login_response.status_code == 200:
            print("✅ Login successful!")
            
            # Extract token
            token_data = login_response.json()
            access_token = token_data.get('access_token')
            
            if access_token:
                print("✅ Got access token!")
                
                # Test protected endpoint
                test_protected_endpoint(access_token)
            else:
                print("❌ No access token in response")
        else:
            print("❌ Login failed")
    else:
        print("❌ Registration failed")
    
    print("\n=== Testing Complete ===")

if __name__ == "__main__":
    main()

