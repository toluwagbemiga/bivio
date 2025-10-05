# Development Setup Guide

## Prerequisites
- Python 3.11+
- Node.js 18+
- Flutter 3.0+
- Docker & Docker Compose
- PostgreSQL (if running locally)

## Quick Start with Docker
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Manual Setup

### 1. Backend (Django)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Configure your settings
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### 2. Database Setup
```bash
# Using Docker
docker run --name pos-postgres -e POSTGRES_DB=pos_financial_db -e POSTGRES_USER=pos_user -e POSTGRES_PASSWORD=pos_password -p 5432:5432 -d postgres:15

# Or install PostgreSQL locally and create database
createdb pos_financial_db
```

### 3. AI Services
```bash
cd ai_services
python -m venv ai_env
source ai_env/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8001
```

### 4. Mobile App (Flutter)
```bash
cd mobile_app
flutter doctor  # Check Flutter installation
flutter pub get
flutter run
```

### 5. Web App (Vue.js PWA)
```bash
cd web_app
npm install
npm run dev
```

## Environment Variables

### Backend (.env)
```
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://pos_user:pos_password@localhost:5432/pos_financial_db
REDIS_URL=redis://localhost:6379/0
```

### AI Services (.env)
```
MODEL_PATH=./models/
DATA_PATH=./data/
DEBUG=True
```

## Testing
```bash
# Backend tests
cd backend
python manage.py test

# Flutter tests
cd mobile_app
flutter test

# Web app tests
cd web_app
npm test
```
