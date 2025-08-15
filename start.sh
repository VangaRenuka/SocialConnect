#!/bin/bash

echo "🚀 Starting SocialConnect Project Setup..."
echo "=========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip first."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating environment file..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your configuration before proceeding."
    echo "   Press Enter when you're ready to continue..."
    read
fi

# Check if PostgreSQL is running
echo "🗄️  Checking database connection..."
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL client not found. Please install PostgreSQL or use Docker."
    echo "   You can use: docker-compose up -d db"
else
    # Try to connect to database
    if ! psql -h localhost -U postgres -d socialconnect -c "SELECT 1;" &> /dev/null; then
        echo "⚠️  Cannot connect to database. Please ensure PostgreSQL is running."
        echo "   You can use: docker-compose up -d db"
    else
        echo "✅ Database connection successful"
    fi
fi

# Check if Redis is running
echo "🔴 Checking Redis connection..."
if ! command -v redis-cli &> /dev/null; then
    echo "⚠️  Redis client not found. Please install Redis or use Docker."
    echo "   You can use: docker-compose up -d redis"
else
    if ! redis-cli ping &> /dev/null; then
        echo "⚠️  Cannot connect to Redis. Please ensure Redis is running."
        echo "   You can use: docker-compose up -d redis"
    else
        echo "✅ Redis connection successful"
    fi
fi

# Run migrations
echo "🔄 Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser if none exists
echo "👤 Checking for superuser..."
if ! python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('Superuser exists' if User.objects.filter(is_superuser=True).exists() else 'No superuser')" 2>/dev/null | grep -q "Superuser exists"; then
    echo "👑 Creating superuser..."
    python manage.py createsuperuser
else
    echo "✅ Superuser already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Start the development server: python manage.py runserver"
echo "2. Access the admin panel: http://localhost:8000/admin/"
echo "3. Test the API endpoints: http://localhost:8000/api/"
echo "4. Run the test script: python test_api.py"
echo ""
echo "Alternative: Use Docker for easy setup:"
echo "  docker-compose up -d"
echo ""
echo "Happy coding! 🚀"


