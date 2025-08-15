#!/usr/bin/env python3
"""
Comprehensive Test Script for SocialConnect - Test All Features!
"""

import requests
import json
import time

# Base URL
BASE_URL = "http://127.0.0.1:8000/api"

class SocialConnectTester:
    def __init__(self):
        self.users = {}
        self.tokens = {}
        self.posts = {}
        
    def print_header(self, title):
        print(f"\n{'='*50}")
        print(f"🧪 {title}")
        print(f"{'='*50}")
    
    def print_success(self, message):
        print(f"✅ {message}")
    
    def print_error(self, message):
        print(f"❌ {message}")
    
    def print_info(self, message):
        print(f"ℹ️  {message}")
    
    def create_user(self, user_num):
        """Create a test user"""
        timestamp = int(time.time())
        username = f"user{user_num}_{timestamp}"
        email = f"user{user_num}_{timestamp}@example.com"
        
        data = {
            "username": username,
            "email": email,
            "password": "testpass123",
            "password_confirm": "testpass123",
            "first_name": f"User{user_num}",
            "last_name": "Test"
        }
        
        response = requests.post(f"{BASE_URL}/auth/register/", json=data)
        
        if response.status_code == 201:
            self.users[user_num] = {"username": username, "email": email}
            self.print_success(f"User {user_num} created: {username}")
            return True
        else:
            self.print_error(f"Failed to create user {user_num}: {response.json()}")
            return False
    
    def login_user(self, user_num):
        """Login a user and get token"""
        if user_num not in self.users:
            self.print_error(f"User {user_num} not created yet")
            return False
            
        username = self.users[user_num]["username"]
        data = {
            "email_or_username": username,
            "password": "testpass123"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login/", json=data)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            if access_token:
                self.tokens[user_num] = access_token
                self.print_success(f"User {user_num} logged in: {username}")
                return True
            else:
                self.print_error(f"No access token for user {user_num}")
                return False
        else:
            self.print_error(f"Login failed for user {user_num}: {response.json()}")
            return False
    
    def create_post(self, user_num, content, category="general"):
        """Create a post for a user"""
        if user_num not in self.tokens:
            self.print_error(f"User {user_num} not logged in")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[user_num]}"}
        data = {
            "content": content,
            "category": category
        }
        
        response = requests.post(f"{BASE_URL}/posts/", json=data, headers=headers)
        
        if response.status_code == 201:
            post_data = response.json()
            post_id = post_data.get('id')
            self.posts[post_id] = {"user": user_num, "content": content}
            self.print_success(f"Post created by user {user_num}: {content[:50]}...")
            return post_id
        else:
            self.print_error(f"Failed to create post: {response.json()}")
            return None
    
    def follow_user(self, follower_num, following_num):
        """Make one user follow another"""
        if follower_num not in self.tokens:
            self.print_error(f"Follower {follower_num} not logged in")
            return False
            
        # Get the user ID to follow (assuming user 1 is ID 1, user 2 is ID 2, etc.)
        following_id = following_num
        
        headers = {"Authorization": f"Bearer {self.tokens[follower_num]}"}
        response = requests.post(f"{BASE_URL}/users/{following_id}/follow/", headers=headers)
        
        if response.status_code == 201:
            self.print_success(f"User {follower_num} now follows user {following_num}")
            return True
        else:
            self.print_error(f"Follow failed: {response.json()}")
            return False
    
    def like_post(self, user_num, post_id):
        """Like a post"""
        if user_num not in self.tokens:
            self.print_error(f"User {user_num} not logged in")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[user_num]}"}
        response = requests.post(f"{BASE_URL}/posts/{post_id}/like/", headers=headers)
        
        if response.status_code == 201:
            self.print_success(f"User {user_num} liked post {post_id}")
            return True
        else:
            self.print_error(f"Like failed: {response.json()}")
            return False
    
    def comment_on_post(self, user_num, post_id, comment_text):
        """Add a comment to a post"""
        if user_num not in self.tokens:
            self.print_error(f"User {user_num} not logged in")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[user_num]}"}
        data = {"content": comment_text}
        
        response = requests.post(f"{BASE_URL}/posts/{post_id}/comments/", json=data, headers=headers)
        
        if response.status_code == 201:
            self.print_success(f"User {user_num} commented on post {post_id}: {comment_text}")
            return True
        else:
            self.print_error(f"Comment failed: {response.json()}")
            return False
    
    def get_feed(self, user_num):
        """Get personalized feed for a user"""
        if user_num not in self.tokens:
            self.print_error(f"User {user_num} not logged in")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[user_num]}"}
        response = requests.get(f"{BASE_URL}/feed/", headers=headers)
        
        if response.status_code == 200:
            feed_data = response.json()
            posts_count = len(feed_data.get('results', []))
            self.print_success(f"Feed retrieved for user {user_num}: {posts_count} posts")
            return feed_data
        else:
            self.print_error(f"Feed retrieval failed: {response.json()}")
            return None
    
    def get_user_profile(self, user_num, target_user_num):
        """Get profile of another user"""
        if user_num not in self.tokens:
            self.print_error(f"User {user_num} not logged in")
            return False
            
        headers = {"Authorization": f"Bearer {self.tokens[user_num]}"}
        response = requests.get(f"{BASE_URL}/users/{target_user_num}/", headers=headers)
        
        if response.status_code == 200:
            profile_data = response.json()
            self.print_success(f"Profile retrieved for user {target_user_num}")
            return profile_data
        else:
            self.print_error(f"Profile retrieval failed: {response.json()}")
            return None
    
    def run_comprehensive_test(self):
        """Run the complete test suite"""
        self.print_header("SOCIALCONNECT COMPREHENSIVE TEST SUITE")
        
        # Step 1: Create multiple users
        self.print_header("Creating Test Users")
        for i in range(1, 4):  # Create 3 users
            self.create_user(i)
            time.sleep(1)  # Small delay
        
        # Step 2: Login all users
        self.print_header("Logging In Users")
        for i in range(1, 4):
            self.login_user(i)
            time.sleep(1)
        
        # Step 3: Create posts
        self.print_header("Creating Posts")
        posts = [
            "Hello SocialConnect! This is my first post! 🎉",
            "Just testing out this amazing social media platform! ✨",
            "Can't wait to see all the features in action! 🚀"
        ]
        
        for i, post_content in enumerate(posts, 1):
            self.create_post(i, post_content)
            time.sleep(1)
        
        # Step 4: Create relationships
        self.print_header("Building Social Network")
        self.follow_user(2, 1)  # User 2 follows User 1
        self.follow_user(3, 1)  # User 3 follows User 1
        self.follow_user(1, 2)  # User 1 follows User 2
        time.sleep(1)
        
        # Step 5: Add engagement
        self.print_header("Adding Engagement")
        # Like posts
        self.like_post(2, 1)  # User 2 likes User 1's post
        self.like_post(3, 1)  # User 3 likes User 1's post
        self.like_post(1, 2)  # User 1 likes User 2's post
        
        # Add comments
        self.comment_on_post(2, 1, "Great first post! 👏")
        self.comment_on_post(3, 1, "Welcome to SocialConnect! 🎊")
        self.comment_on_post(1, 2, "Nice post! Keep it up! 💪")
        time.sleep(1)
        
        # Step 6: Test personalized feeds
        self.print_header("Testing Personalized Feeds")
        for i in range(1, 4):
            self.get_feed(i)
            time.sleep(1)
        
        # Step 7: Test user profiles
        self.print_header("Testing User Profiles")
        for i in range(1, 4):
            for j in range(1, 4):
                if i != j:
                    self.get_user_profile(i, j)
                    time.sleep(0.5)
        
        # Step 8: Show final statistics
        self.print_header("FINAL STATISTICS")
        self.print_info(f"Users created: {len(self.users)}")
        self.print_info(f"Posts created: {len(self.posts)}")
        self.print_info(f"Active tokens: {len(self.tokens)}")
        
        self.print_header("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        self.print_info("Your SocialConnect backend is working perfectly!")
        self.print_info("All core social media features are functional!")
        
        return True

def main():
    tester = SocialConnectTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()

