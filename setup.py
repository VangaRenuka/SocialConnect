#!/usr/bin/env python
"""
Setup script for SocialConnect project.
This script helps with initial project setup and database initialization.
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'socialconnect.settings')

# Setup Django
django.setup()

from django.contrib.auth import get_user_model
from django.core.management import execute_from_command_line
from users.models import User

def create_superuser():
    """Create a superuser if none exists."""
    User = get_user_model()
    
    if not User.objects.filter(is_superuser=True).exists():
        print("Creating superuser...")
        username = input("Enter username: ")
        email = input("Enter email: ")
        password = input("Enter password: ")
        
        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name="Admin",
                last_name="User",
                role="admin"
            )
            print(f"Superuser '{username}' created successfully!")
            return user
        except Exception as e:
            print(f"Error creating superuser: {e}")
            return None
    else:
        print("Superuser already exists.")
        return None

def create_sample_data():
    """Create sample data for testing."""
    User = get_user_model()
    
    print("Creating sample data...")
    
    # Create sample users
    users_data = [
        {
            'username': 'john_doe',
            'email': 'john@example.com',
            'password': 'testpass123',
            'first_name': 'John',
            'last_name': 'Doe',
            'bio': 'Software developer and tech enthusiast',
            'role': 'user'
        },
        {
            'username': 'jane_smith',
            'email': 'jane@example.com',
            'password': 'testpass123',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'bio': 'Digital marketer and social media expert',
            'role': 'user'
        },
        {
            'username': 'mike_wilson',
            'email': 'mike@example.com',
            'password': 'testpass123',
            'first_name': 'Mike',
            'last_name': 'Wilson',
            'bio': 'Photographer and travel blogger',
            'role': 'user'
        }
    ]
    
    created_users = []
    for user_data in users_data:
        try:
            if not User.objects.filter(username=user_data['username']).exists():
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    bio=user_data['bio'],
                    role=user_data['role'],
                    is_email_verified=True
                )
                created_users.append(user)
                print(f"Created user: {user.username}")
            else:
                print(f"User {user_data['username']} already exists")
        except Exception as e:
            print(f"Error creating user {user_data['username']}: {e}")
    
    return created_users

def main():
    """Main setup function."""
    print("🚀 SocialConnect Project Setup")
    print("=" * 40)
    
    # Check if migrations need to be run
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM django_migrations LIMIT 1")
        print("✅ Database is set up and migrations are applied")
    except Exception as e:
        print("❌ Database setup required. Please run:")
        print("   python manage.py makemigrations")
        print("   python manage.py migrate")
        return
    
    # Create superuser
    superuser = create_superuser()
    
    # Ask if user wants to create sample data
    create_sample = input("\nCreate sample data for testing? (y/n): ").lower().strip()
    if create_sample == 'y':
        sample_users = create_sample_data()
        print(f"\n✅ Created {len(sample_users)} sample users")
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Start the development server: python manage.py runserver")
    print("2. Access the admin panel: http://localhost:8000/admin/")
    print("3. Test the API endpoints: http://localhost:8000/api/")
    print("4. Check the README.md for API documentation")

if __name__ == '__main__':
    main()


