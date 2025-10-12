# backend/apps/users/views.py
"""
User management API views for authentication and profile management
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta

from .models import User, BusinessProfile, Guarantor
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    BusinessProfileSerializer,
    GuarantorSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for user views"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user management
    """
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter users based on permissions"""
        if self.request.user.user_type == 'admin':
            return User.objects.all().order_by('-created_at')
        elif self.request.user.user_type == 'super_agent':
            # Super agents can see agents and borrowers under them
            return User.objects.filter(
                Q(user_type='agent') | Q(user_type='borrower')
            ).order_by('-created_at')
        else:
            # Regular users can only see their own profile
            return User.objects.filter(id=self.request.user.id)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'register':
            return UserRegistrationSerializer
        elif self.action == 'login':
            return UserLoginSerializer
        return UserProfileSerializer
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        """User registration endpoint"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Create auth token
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'user': UserProfileSerializer(user).data,
                'token': token.key,
                'message': 'User registered successfully'
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        """User login endpoint"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Create or get auth token
            token, created = Token.objects.get_or_create(user=user)
            
            # Update last login
            user.last_login = timezone.now()
            user.save()
            
            return Response({
                'user': UserProfileSerializer(user).data,
                'token': token.key,
                'message': 'Login successful'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def logout(self, request):
        """User logout endpoint"""
        try:
            request.user.auth_token.delete()
            return Response({'message': 'Logout successful'})
        except:
            return Response({'message': 'Logout successful'})
    
    @action(detail=True, methods=['get'])
    def profile(self, request, pk=None):
        """Get user profile with business information"""
        user = self.get_object()
        
        profile_data = UserProfileSerializer(user).data
        
        try:
            business_profile = user.business_profile
            profile_data['business_profile'] = BusinessProfileSerializer(business_profile).data
        except BusinessProfile.DoesNotExist:
            profile_data['business_profile'] = None
        
        return Response(profile_data)
    
    @action(detail=True, methods=['put'])
    def update_profile(self, request, pk=None):
        """Update user profile"""
        user = self.get_object()
        
        # Ensure user can only update their own profile
        if user != request.user and request.user.user_type not in ['admin', 'super_agent']:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def dashboard_stats(self, request, pk=None):
        """Get user dashboard statistics"""
        user = self.get_object()
        
        stats = {
            'user_info': {
                'full_name': user.full_name,
                'user_type': user.user_type,
                'verification_status': user.verification_status,
                'is_profile_complete': user.is_profile_complete
            },
            'business_stats': {},
            'financial_stats': {},
            'recent_activity': []
        }
        
        # Business profile stats
        try:
            business_profile = user.business_profile
            stats['business_stats'] = {
                'business_name': business_profile.business_name,
                'business_type': business_profile.business_type,
                'credit_score': business_profile.credit_score,
                'risk_level': business_profile.risk_level,
                'is_verified': business_profile.is_business_verified
            }
        except BusinessProfile.DoesNotExist:
            stats['business_stats'] = None
        
        # Financial stats (if user has transactions)
        try:
            from apps.transactions.models import Transaction
            from apps.loans.models import Loan
            from apps.savings.models import SavingsAccount
            
            # Transaction stats
            transactions = Transaction.objects.filter(user=user)
            stats['financial_stats']['total_transactions'] = transactions.count()
            stats['financial_stats']['total_sales'] = sum(
                t.total_amount for t in transactions.filter(transaction_type='sale')
            )
            
            # Loan stats
            loans = Loan.objects.filter(borrower=user)
            stats['financial_stats']['active_loans'] = loans.filter(status='active').count()
            stats['financial_stats']['total_borrowed'] = sum(
                l.principal_amount for l in loans.filter(status__in=['disbursed', 'active'])
            )
            
            # Savings stats
            savings_accounts = SavingsAccount.objects.filter(user=user)
            stats['financial_stats']['total_savings'] = sum(
                sa.current_balance for sa in savings_accounts
            )
            
        except ImportError:
            stats['financial_stats'] = {}
        
        return Response(stats)
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify user account (admin only)"""
        if request.user.user_type != 'admin':
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = self.get_object()
        verification_status = request.data.get('verification_status')
        
        if verification_status not in ['verified', 'rejected']:
            return Response(
                {'error': 'Invalid verification status'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.verification_status = verification_status
        user.save()
        
        serializer = self.get_serializer(user)
        return Response(serializer.data)


class BusinessProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for business profile management
    """
    serializer_class = BusinessProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter business profiles by user"""
        if self.request.user.user_type == 'admin':
            return BusinessProfile.objects.all().order_by('-created_at')
        else:
            return BusinessProfile.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set user when creating business profile"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify business profile (admin only)"""
        if request.user.user_type != 'admin':
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        business_profile = self.get_object()
        is_verified = request.data.get('is_verified', True)
        verification_notes = request.data.get('verification_notes', '')
        
        business_profile.is_business_verified = is_verified
        business_profile.save()
        
        # Update user verification status
        user = business_profile.user
        if is_verified:
            user.verification_status = 'verified'
        else:
            user.verification_status = 'rejected'
        user.save()
        
        serializer = self.get_serializer(business_profile)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def calculate_credit_score(self, request, pk=None):
        """Recalculate credit score"""
        business_profile = self.get_object()
        
        # Ensure user can only update their own profile
        if business_profile.user != request.user and request.user.user_type not in ['admin', 'super_agent']:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        old_score = business_profile.credit_score
        new_score = business_profile.calculate_credit_score()
        
        serializer = self.get_serializer(business_profile)
        return Response({
            'business_profile': serializer.data,
            'old_score': old_score,
            'new_score': new_score,
            'score_change': new_score - old_score
        })


class GuarantorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for guarantor management
    """
    serializer_class = GuarantorSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter guarantors by borrower"""
        return Guarantor.objects.filter(borrower=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set borrower when creating guarantor"""
        serializer.save(borrower=self.request.user)
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify guarantor (admin only)"""
        if request.user.user_type != 'admin':
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        guarantor = self.get_object()
        is_verified = request.data.get('is_verified', True)
        verification_notes = request.data.get('verification_notes', '')
        
        guarantor.is_verified = is_verified
        guarantor.verification_notes = verification_notes
        guarantor.save()
        
        serializer = self.get_serializer(guarantor)
        return Response(serializer.data)