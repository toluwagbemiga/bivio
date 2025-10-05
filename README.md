# POS-Integrated Financial Management App

A comprehensive POS system with AI-powered features designed for low-income borrowers and micro-lenders in Nigeria.

## 🚀 Features
- **Smart Transaction Categorization** - AI-powered product recognition
- **Inventory Management** - Real-time stock tracking
- **Loan Management** - Flexible repayment tracking
- **Savings Wallet** - Automated micro-savings
- **Offline-First** - Works without internet connection
- **Multi-Platform** - Mobile app + PWA web interface

## 🏗️ Tech Stack
- **Backend**: Django REST Framework + PostgreSQL + Redis
- **Mobile**: Flutter (iOS/Android)
- **Web**: Vue.js PWA with offline support
- **AI/ML**: FastAPI + scikit-learn
- **Infrastructure**: Docker + Nginx

## 🚀 Quick Start

### Using Docker (Recommended)
```bash
# Clone and setup
git clone <repo-url>
cd pos_financial_app

# Start all services
docker-compose up -d

# Access the applications
# - Backend API: http://localhost:8000
# - AI Services: http://localhost:8001
# - Web App: http://localhost:3000
# - Full App: http://localhost (via Nginx)
```

### Manual Setup
```bash
# 1. Backend (Django)
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# 2. AI Services
cd ai_services
python -m venv ai_env
source ai_env/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8001

# 3. Mobile App (Flutter)
cd mobile_app
flutter pub get
flutter run

# 4. Web App (Vue.js)
cd web_app
npm install
npm run dev
```

## 📱 Mobile App Development
```bash
# Development
cd mobile_app
flutter pub get
flutter run

# Build APK
flutter build apk --release
```

## 🌐 PWA Development
```bash
# Development
cd web_app  
npm run dev

# Build for production
npm run build
```

## 🤖 AI Services
The AI service handles:
- Transaction categorization
- Product recognition for Nigerian market
- Fraud detection
- Cash flow predictions

## 📊 Database Schema
- Users & Authentication
- Transactions & POS data
- Inventory & Products
- Loans & Repayments
- Savings & Wallets

## 🚀 Deployment
See `docs/deployment/` for production deployment guides.

## 📖 Documentation
- API Documentation: `docs/api/`
- Setup Guides: `docs/setup/`
- Deployment: `docs/deployment/`

## 🤝 Contributing
1. Fork the repository
2. Create feature branch
3. Make changes
4. Submit pull request

## 📄 License
MIT License - see LICENSE file for details.
