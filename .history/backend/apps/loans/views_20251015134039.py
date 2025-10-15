# backend/apps/loans/views.py
"""
Loan management API views for loan applications, approvals, and repayments
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Sum, Count, F
from django.utils import timezone
from django.db import transaction as db_transaction
from datetime import datetime, timedelta
from decimal import Decimal

from .models import LoanProduct, Loan, LoanRepayment
from .serializers import (
    LoanProductSerializer,
    LoanSerializer,
    LoanRepaymentSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for loan views"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class LoanProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing loan products
    """
    queryset = LoanProduct.objects.all()
    serializer_class = LoanProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter loan products based on user type"""
        if self.request.user.user_type in ['admin', 'lender']:
            return LoanProduct.objects.all().order_by('-created_at')
        else:
            # Borrowers can only see active loan products
            return LoanProduct.objects.filter(is_active=True).order_by('name')
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get loan products available for user"""
        user = request.user
        
        if user.user_type not in ['borrower', 'agent']:
            return Response(
                {'error': 'Only borrowers and agents can apply for loans'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Filter products based on user eligibility
        available_products = LoanProduct.objects.filter(is_active=True)
        
        try:
            business_profile = user.business_profile
            # Filter by credit score and revenue requirements
            available_products = available_products.filter(
                min_credit_score__lte=business_profile.credit_score,
                min_monthly_revenue__lte=business_profile.estimated_monthly_revenue or 0
            )
        except:
            # If no business profile, show basic products only
            available_products = available_products.filter(min_credit_score=0)
        
        serializer = self.get_serializer(available_products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def calculate_loan(self, request, pk=None):
        """Calculate loan terms for a product"""
        loan_product = self.get_object()
        principal_amount = Decimal(str(request.data.get('principal_amount', 0)))
        
        if principal_amount < loan_product.min_amount or principal_amount > loan_product.max_amount:
            return Response(
                {'error': f'Amount must be between ₦{loan_product.min_amount} and ₦{loan_product.max_amount}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate loan terms
        processing_fee = (principal_amount * loan_product.processing_fee_rate) / 100
        
        if loan_product.interest_type == 'flat':
            total_interest = (principal_amount * loan_product.interest_rate * loan_product.min_tenure_days) / (365 * 100)
        else:  # reducing balance
            monthly_rate = loan_product.interest_rate / (12 * 100)
            months = loan_product.min_tenure_days / 30
            if monthly_rate > 0:
                monthly_installment = (principal_amount * monthly_rate * ((1 + monthly_rate) ** months)) / (((1 + monthly_rate) ** months) - 1)
                total_interest = (monthly_installment * months) - principal_amount
            else:
                monthly_installment = principal_amount / months
                total_interest = 0
        
        total_amount = principal_amount + total_interest + processing_fee
        
        calculation = {
            'principal_amount': principal_amount,
            'processing_fee': processing_fee,
            'total_interest': total_interest,
            'total_amount': total_amount,
            'monthly_installment': monthly_installment,
            'tenure_days': loan_product.min_tenure_days,
            'interest_rate': loan_product.interest_rate,
            'interest_type': loan_product.interest_type
        }
        
        return Response(calculation)


class LoanViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing loan applications and loans
    """
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter loans based on user type"""
        if self.request.user.user_type in ['admin', 'lender']:
            return Loan.objects.all().order_by('-created_at')
        else:
            # Borrowers can only see their own loans
            return Loan.objects.filter(borrower=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set borrower when creating loan"""
        serializer.save(borrower=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_loans(self, request):
        """Get current user's loans"""
        loans = self.get_queryset().filter(borrower=request.user)
        serializer = self.get_serializer(loans, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active loans"""
        loans = self.get_queryset().filter(status='active')
        serializer = self.get_serializer(loans, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue loans"""
        loans = self.get_queryset().filter(days_past_due__gt=0, outstanding_balance__gt=0)
        serializer = self.get_serializer(loans, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve loan application (admin/lender only)"""
        if request.user.user_type not in ['admin', 'lender']:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        loan = self.get_object()
        
        if loan.status != 'applied':
            return Response(
                {'error': 'Only applied loans can be approved'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        approval_notes = request.data.get('approval_notes', '')
        
        loan.status = 'approved'
        loan.approved_by = request.user
        loan.approved_date = timezone.now()
        loan.approval_notes = approval_notes
        loan.save()
        
        serializer = self.get_serializer(loan)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject loan application (admin/lender only)"""
        if request.user.user_type not in ['admin', 'lender']:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        loan = self.get_object()
        
        if loan.status != 'applied':
            return Response(
                {'error': 'Only applied loans can be rejected'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rejection_reason = request.data.get('rejection_reason', '')
        
        if not rejection_reason:
            return Response(
                {'error': 'Rejection reason is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        loan.status = 'rejected'
        loan.rejection_reason = rejection_reason
        loan.save()
        
        serializer = self.get_serializer(loan)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def disburse(self, request, pk=None):
        """Disburse approved loan (admin/lender only)"""
        if request.user.user_type not in ['admin', 'lender']:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        loan = self.get_object()
        
        if loan.status != 'approved':
            return Response(
                {'error': 'Only approved loans can be disbursed'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        loan.status = 'disbursed'
        loan.disbursed_date = timezone.now()
        loan.first_repayment_date = timezone.now().date() + timedelta(days=loan.loan_product.min_tenure_days)
        loan.final_repayment_date = timezone.now().date() + timedelta(days=loan.tenure_days)
        loan.save()
        
        # Create first repayment schedule
        self._create_repayment_schedule(loan)
        
        serializer = self.get_serializer(loan)
        return Response(serializer.data)
    
    def _create_repayment_schedule(self, loan):
        """Create repayment schedule for loan"""
        # This is a simplified version - in production, you'd create multiple repayment records
        LoanRepayment.objects.create(
            loan=loan,
            repayment_type='scheduled',
            scheduled_amount=loan.monthly_installment,
            due_date=loan.first_repayment_date,
            payment_date=loan.first_repayment_date,
            status='pending'
        )
    
    @action(detail=True, methods=['get'])
    def repayments(self, request, pk=None):
        """Get loan repayments"""
        loan = self.get_object()
        repayments = loan.repayments.all().order_by('-payment_date')
        serializer = LoanRepaymentSerializer(repayments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def make_payment(self, request, pk=None):
        """Make loan payment"""
        loan = self.get_object()
        
        if loan.status not in ['disbursed', 'active']:
            return Response(
                {'error': 'Loan is not active'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment_amount = Decimal(str(request.data.get('payment_amount', 0)))
        payment_method = request.data.get('payment_method', 'cash')
        notes = request.data.get('notes', '')
        
        if payment_amount <= 0:
            return Response(
                {'error': 'Payment amount must be positive'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if payment_amount > loan.outstanding_balance:
            return Response(
                {'error': 'Payment amount exceeds outstanding balance'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with db_transaction.atomic():
            # Create repayment record
            repayment = LoanRepayment.objects.create(
                loan=loan,
                repayment_type='manual',
                scheduled_amount=loan.monthly_installment,
                paid_amount=payment_amount,
                principal_amount=payment_amount * 0.7,  # Simplified allocation
                interest_amount=payment_amount * 0.3,
                payment_method=payment_method,
                due_date=timezone.now().date(),
                payment_date=timezone.now(),
                status='completed',
                notes=notes,
                processed_by=request.user
            )
            
            # Update loan balance
            loan.amount_paid += payment_amount
            loan.outstanding_balance -= payment_amount
            
            if loan.outstanding_balance <= 0:
                loan.status = 'completed'
            
            loan.save()
        
        serializer = LoanRepaymentSerializer(repayment)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get loan dashboard statistics"""
        if request.user.user_type in ['admin', 'lender']:
            loans = Loan.objects.all()
        else:
            loans = Loan.objects.filter(borrower=request.user)
        
        stats = {
            'total_loans': loans.count(),
            'active_loans': loans.filter(status='active').count(),
            'overdue_loans': loans.filter(days_past_due__gt=0, outstanding_balance__gt=0).count(),
            'total_disbursed': sum(l.principal_amount for l in loans.filter(status__in=['disbursed', 'active', 'completed'])),
            'total_outstanding': sum(l.outstanding_balance for l in loans.filter(status__in=['disbursed', 'active'])),
            'total_repaid': sum(l.amount_paid for l in loans.filter(status__in=['disbursed', 'active', 'completed'])),
            'recent_applications': loans.filter(status='applied').count()
        }
        
        return Response(stats)


class LoanRepaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing loan repayments
    """
    serializer_class = LoanRepaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter repayments based on user type"""
        if self.request.user.user_type in ['admin', 'lender']:
            return LoanRepayment.objects.all().order_by('-payment_date')
        else:
            # Borrowers can only see their own repayments
            return LoanRepayment.objects.filter(
                loan__borrower=self.request.user
            ).order_by('-payment_date')
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending repayments"""
        repayments = self.get_queryset().filter(status='pending')
        serializer = self.get_serializer(repayments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue repayments"""
        repayments = self.get_queryset().filter(
            status='pending',
            due_date__lt=timezone.now().date()
        )
        serializer = self.get_serializer(repayments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def process_payment(self, request, pk=None):
        """Process repayment payment (admin/lender only)"""
        if request.user.user_type not in ['admin', 'lender']:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        repayment = self.get_object()
        
        if repayment.status != 'pending':
            return Response(
                {'error': 'Only pending repayments can be processed'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        paid_amount = Decimal(str(request.data.get('paid_amount', repayment.scheduled_amount)))
        payment_method = request.data.get('payment_method', 'cash')
        notes = request.data.get('notes', '')
        
        repayment.paid_amount = paid_amount
        repayment.payment_method = payment_method
        repayment.payment_date = timezone.now()
        repayment.status = 'completed'
        repayment.notes = notes
        repayment.processed_by = request.user
        repayment.save()
        
        # Update loan balance
        loan = repayment.loan
        loan.amount_paid += paid_amount
        loan.outstanding_balance -= paid_amount
        
        if loan.outstanding_balance <= 0:
            loan.status = 'completed'
        
        loan.save()
        
        serializer = self.get_serializer(repayment)
        return Response(serializer.data)