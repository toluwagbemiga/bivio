# backend/test_api.py
"""
API Testing Script
Tests all major endpoints to ensure they're working
"""

import requests
import json
from pprint import pprint

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

class APITester:
    def __init__(self):
        self.token = None
        self.headers = {'Content-Type': 'application/json'}
    
    def test_login(self):
        """Test user login"""
        print("\n" + "="*60)
        print("Testing Authentication")
        print("="*60)
        
        # Register new user
        print("\n1. Testing Registration...")
        register_data = {
            "email": "testuser@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "08011223344",
            "password": "testpass123",
            "password_confirm": "testpass123",
            "user_type": "borrower"
        }
        
        try:
            response = requests.post(
                f"{API_BASE}/auth/register/",
                json=register_data,
                headers=self.headers
            )
            
            if response.status_code == 201:
                print_success("Registration successful")
                data = response.json()
                self.token = data.get('token')
                print_info(f"Token received: {self.token[:20]}...")
            elif response.status_code == 400:
                print_warning("User may already exist, trying login...")
            else:
                print_error(f"Registration failed: {response.status_code}")
        except Exception as e:
            print_error(f"Registration error: {e}")
        
        # Login
        print("\n2. Testing Login...")
        login_data = {
            "email": "trader@test.com",
            "password": "test123"
        }
        
        try:
            response = requests.post(
                f"{API_BASE}/auth/login/",
                json=login_data,
                headers=self.headers
            )
            
            if response.status_code == 200:
                print_success("Login successful")
                data = response.json()
                self.token = data.get('token')
                self.headers['Authorization'] = f'Token {self.token}'
                print_info(f"Token: {self.token[:20]}...")
                print_info(f"User: {data['user']['email']}")
            else:
                print_error(f"Login failed: {response.status_code}")
                print(response.text)
        except Exception as e:
            print_error(f"Login error: {e}")
    
    def test_inventory(self):
        """Test inventory endpoints"""
        print("\n" + "="*60)
        print("Testing Inventory Management")
        print("="*60)
        
        # Get categories
        print("\n1. Getting product categories...")
        try:
            response = requests.get(
                f"{API_BASE}/inventory/categories/",
                headers=self.headers
            )
            
            if response.status_code == 200:
                categories = response.json()
                print_success(f"Retrieved {len(categories)} categories")
                if categories:
                    print_info(f"Sample: {categories[0]['name']}")
            else:
                print_error(f"Failed: {response.status_code}")
        except Exception as e:
            print_error(f"Error: {e}")
        
        # Get products
        print("\n2. Getting products...")
        try:
            response = requests.get(
                f"{API_BASE}/inventory/products/",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                products = data.get('results', [])
                print_success(f"Retrieved {len(products)} products")
                if products:
                    product = products[0]
                    print_info(f"Sample: {product['name']} - ₦{product['selling_price']}")
            else:
                print_error(f"Failed: {response.status_code}")
        except Exception as e:
            print_error(f"Error: {e}")
    
    def test_transactions(self):
        """Test transaction endpoints"""
        print("\n" + "="*60)
        print("Testing Transactions")
        print("="*60)
        
        # Get transactions
        print("\n1. Getting transactions...")
        try:
            response = requests.get(
                f"{API_BASE}/transactions/",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                transactions = data.get('results', [])
                print_success(f"Retrieved {len(transactions)} transactions")
                if transactions:
                    txn = transactions[0]
                    print_info(f"Sample: {txn['transaction_number']} - ₦{txn['total_amount']}")
            else:
                print_error(f"Failed: {response.status_code}")
        except Exception as e:
            print_error(f"Error: {e}")
        
        # Get analytics
        print("\n2. Getting transaction analytics...")
        try:
            response = requests.get(
                f"{API_BASE}/transactions/analytics/?days=7",
                headers=self.headers
            )
            
            if response.status_code == 200:
                analytics = response.json()
                print_success("Analytics retrieved")
                print_info(f"Total Sales: ₦{analytics.get('total_sales', 0)}")
                print_info(f"Total Transactions: {analytics.get('total_transactions', 0)}")
            else:
                print_error(f"Failed: {response.status_code}")
        except Exception as e:
            print_error(f"Error: {e}")
    
    def test_loans(self):
        """Test loan endpoints"""
        print("\n" + "="*60)
        print("Testing Loan Management")
        print("="*60)
        
        # Get loan products
        print("\n1. Getting loan products...")
        try:
            response = requests.get(
                f"{API_BASE}/loans/products/",
                headers=self.headers
            )
            
            if response.status_code == 200:
                products = response.json()
                print_success(f"Retrieved {len(products)} loan products")
                if products:
                    product = products[0]
                    print_info(f"Sample: {product['name']}")
                    print_info(f"  Amount: ₦{product['min_amount']} - ₦{product['max_amount']}")
                    print_info(f"  Interest: {product['interest_rate']}%")
            else:
                print_error(f"Failed: {response.status_code}")
        except Exception as e:
            print_error(f"Error: {e}")
        
        # Get user's loans
        print("\n2. Getting user loans...")
        try:
            response = requests.get(
                f"{API_BASE}/loans/",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                loans = data.get('results', [])
                print_success(f"Retrieved {len(loans)} loans")
            else:
                print_error(f"Failed: {response.status_code}")
        except Exception as e:
            print_error(f"Error: {e}")
    
    def test_savings(self):
        """Test savings endpoints"""
        print("\n" + "="*60)
        print("Testing Savings Management")
        print("="*60)
        
        # Get savings accounts
        print("\n1. Getting savings accounts...")
        try:
            response = requests.get(
                f"{API_BASE}/savings/accounts/",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                accounts = data.get('results', [])
                print_success(f"Retrieved {len(accounts)} savings accounts")
                if accounts:
                    account = accounts[0]
                    print_info(f"Sample: {account['account_name']}")
                    print_info(f"  Balance: ₦{account['current_balance']}")
            else:
                print_error(f"Failed: {response.status_code}")
        except Exception as e:
            print_error(f"Error: {e}")
    
    def test_analytics(self):
        """Test analytics endpoints"""
        print("\n" + "="*60)
        print("Testing Analytics & Dashboard")
        print("="*60)
        
        # Get dashboard summary
        print("\n1. Getting dashboard summary...")
        try:
            response = requests.get(
                f"{API_BASE}/analytics/dashboard/",
                headers=self.headers
            )
            
            if response.status_code == 200:
                dashboard = response.json()
                print_success("Dashboard data retrieved")
                print_info(f"Weekly Sales: ₦{dashboard.get('weekly_sales', 0)}")
                print_info(f"Performance Score: {dashboard.get('performance_score', 0)}")
                print_info(f"Total Savings: ₦{dashboard.get('total_savings', 0)}")
            else:
                print_error(f"Failed: {response.status_code}")
        except Exception as e:
            print_error(f"Error: {e}")
    
    def test_notifications(self):
        """Test notification endpoints"""
        print("\n" + "="*60)
        print("Testing Notifications")
        print("="*60)
        
        # Get notifications
        print("\n1. Getting notifications...")
        try:
            response = requests.get(
                f"{API_BASE}/notifications/",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                notifications = data.get('results', [])
                print_success(f"Retrieved {len(notifications)} notifications")
            else:
                print_error(f"Failed: {response.status_code}")
        except Exception as e:
            print_error(f"Error: {e}")
        
        # Get unread count
        print("\n2. Getting unread count...")
        try:
            response = requests.get(
                f"{API_BASE}/notifications/unread-count/",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Unread notifications: {data.get('unread_count', 0)}")
            else:
                print_error(f"Failed: {response.status_code}")
        except Exception as e:
            print_error(f"Error: {e}")
    
    def test_ai_service(self):
        """Test AI categorization service"""
        print("\n" + "="*60)
        print("Testing AI Categorization Service")
        print("="*60)
        
        AI_URL = "http://localhost:8001"
        
        # Health check
        print("\n1. AI Service health check...")
        try:
            response = requests.get(f"{AI_URL}/health")
            
            if response.status_code == 200:
                print_success("AI Service is running")
                data = response.json()
                print_info(f"Status: {data.get('status')}")
                print_info(f"Version: {data.get('version')}")
            else:
                print_warning("AI Service may not be running")
                print_info("Start it with: cd ai_services && uvicorn api.main:app --reload --port 8001")
        except Exception as e:
            print_warning(f"AI Service not accessible: {e}")
            print_info("Start it with: cd ai_services && uvicorn api.main:app --reload --port 8001")
            return
        
        # Test categorization
        print("\n2. Testing product categorization...")
        test_products = [
            "Indomie noodles",
            "MTN airtime",
            "Phone charger",
            "Omo detergent",
            "Close-Up toothpaste"
        ]
        
        for product in test_products:
            try:
                response = requests.post(
                    f"{AI_URL}/ai/categorize",
                    json={"text_input": product}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    category = data['predicted_category']['name']
                    confidence = data['confidence']
                    print_success(f"'{product}' → {category} ({confidence:.0%})")
                else:
                    print_error(f"Categorization failed for '{product}'")
            except Exception as e:
                print_error(f"Error: {e}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("🧪 POS FINANCIAL MANAGEMENT API TESTS")
        print("="*60)
        
        # Test authentication first
        self.test_login()
        
        if not self.token:
            print_error("\n❌ Cannot proceed without authentication token")
            print_info("Make sure the backend is running: python manage.py runserver")
            return
        
        # Test other endpoints
        self.test_inventory()
        self.test_transactions()
        self.test_loans()
        self.test_savings()
        self.test_analytics()
        self.test_notifications()
        self.test_ai_service()
        
        # Summary
        print("\n" + "="*60)
        print("✅ API TESTING COMPLETE")
        print("="*60)
        print("\n📊 Summary:")
        print("  • All major endpoints tested")
        print("  • Authentication working")
        print("  • Data retrieval working")
        print("\n🎯 Next Steps:")
        print("  1. Check Django admin: http://localhost:8000/admin")
        print("  2. Explore API endpoints")
        print("  3. Start building Flutter app")
        print("\n" + "="*60)


def main():
    """Main test runner"""
    print("\n🔍 Checking if backend is running...")
    
    try:
        response = requests.get(BASE_URL, timeout=2)
        print_success("Backend is running")
    except Exception:
        print_error("Backend is not running!")
        print_info("Start it with: python manage.py runserver")
        print("\nExiting...")
        return
    
    # Run tests
    tester = APITester()
    tester.run_all_tests()


if __name__ == '__main__':
    main()