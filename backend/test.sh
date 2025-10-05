#!/bin/bash

# POS Financial App - Backend Test Script
# Run this to setup and test the Django backend

set -e

echo "🚀 POS Financial Management - Backend Setup & Test"
echo "=================================================="
echo ""

# Check if we're in the backend directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: Please run this script from the backend directory"
    echo "   cd pos_financial_app/backend"
    exit 1
fi

# Check Python version
echo "📍 Checking Python version..."
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create logs directory
mkdir -p logs

# Environment setup
if [ ! -f ".env" ]; then
    echo ""
    echo "⚙️  Creating .env file..."
    cat > .env << 'EOF'
DEBUG=True
SECRET_KEY=django-insecure-pos-financial-dev-key-change-in-production
DATABASE_URL=postgresql://pos_user:pos_password@localhost:5432/pos_financial_db
DB_NAME=pos_financial_db
DB_USER=pos_user
DB_PASSWORD=pos_password
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
AI_SERVICE_URL=http://localhost:8001
EOF
    echo "✅ .env file created"
fi

# Database setup
echo ""
echo "🗄️  Setting up database..."
echo "   Note: Make sure PostgreSQL is running!"
echo "   If not installed, run: brew install postgresql (Mac) or apt-get install postgresql (Linux)"
echo ""

# Try to create database (may fail if already exists, that's okay)
psql -U postgres -c "CREATE DATABASE pos_financial_db;" 2>/dev/null || echo "   Database may already exist, continuing..."
psql -U postgres -c "CREATE USER pos_user WITH PASSWORD 'pos_password';" 2>/dev/null || echo "   User may already exist, continuing..."
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE pos_financial_db TO pos_user;" 2>/dev/null || true

# Run migrations
echo ""
echo "🔄 Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Create setup script if it doesn't exist
if [ ! -f "setup_and_test.py" ]; then
    echo ""
    echo "⚠️  setup_and_test.py not found"
    echo "   Please make sure the setup script is in the backend directory"
    exit 1
fi

# Run setup script
echo ""
echo "📊 Populating database with test data..."
python setup_and_test.py

# Collect static files
echo ""
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "=================================================="
echo "✅ BACKEND SETUP COMPLETE!"
echo "=================================================="
echo ""
echo "🎯 What's Ready:"
echo "   • Database created and migrated"
echo "   • Test data populated"
echo "   • Admin user created"
echo "   • Sample transactions created"
echo ""
echo "🔐 Credentials:"
echo "   Admin: admin@posfinancial.com / admin123"
echo "   User1: trader@test.com / test123"
echo "   User2: shopowner@test.com / test123"
echo ""
echo "🚀 Start the server:"
echo "   python manage.py runserver"
echo ""
echo "🌐 Then access:"
echo "   • Admin Panel: http://localhost:8000/admin"
echo "   • API Root: http://localhost:8000/api/v1/"
echo ""
echo "📝 Test the API:"
echo "   1. Login via /api/v1/auth/login/"
echo "   2. Get token"
echo "   3. Use token in Authorization header"
echo ""
echo "=================================================="