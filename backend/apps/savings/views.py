# backend/apps/savings/views.py
"""
Savings management API views for savings accounts, transactions, and goals
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.db import transaction as db_transaction
from datetime import datetime, timedelta
from decimal import Decimal

from .models import SavingsAccount, SavingsTransaction, SavingsGoal
from .serializers import (
    SavingsAccountSerializer,
    SavingsTransactionSerializer,
    SavingsGoalSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for savings views"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class SavingsAccountViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing savings accounts
    """
    serializer_class = SavingsAccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter savings accounts by user"""
        return SavingsAccount.objects.filter(user=self.request.user).order_by('-is_default', 'account_name')
    
    def perform_create(self, serializer):
        """Set user when creating savings account"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active savings accounts"""
        accounts = self.get_queryset().filter(status='active')
        serializer = self.get_serializer(accounts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def deposit(self, request, pk=None):
        """Make a deposit to savings account"""
        account = self.get_object()
        amount = Decimal(str(request.data.get('amount', 0)))
        reference = request.data.get('reference', 'Manual deposit')
        notes = request.data.get('notes', '')
        
        if amount <= 0:
            return Response(
                {'error': 'Deposit amount must be positive'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if account.status != 'active':
            return Response(
                {'error': 'Account is not active'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        account.add_funds(amount, 'deposit', reference)
        
        # Create transaction record
        SavingsTransaction.objects.create(
            savings_account=account,
            transaction_type='deposit',
            amount=amount,
            reference=reference,
            balance_after=account.current_balance,
            notes=notes,
            processed_by=request.user
        )
        
        serializer = self.get_serializer(account)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def withdraw(self, request, pk=None):
        """Make a withdrawal from savings account"""
        account = self.get_object()
        amount = Decimal(str(request.data.get('amount', 0)))
        reference = request.data.get('reference', 'Manual withdrawal')
        notes = request.data.get('notes', '')
        
        if amount <= 0:
            return Response(
                {'error': 'Withdrawal amount must be positive'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if account.status != 'active':
            return Response(
                {'error': 'Account is not active'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not account.can_withdraw(amount):
            return Response(
                {'error': 'Insufficient funds or below minimum balance'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success = account.withdraw_funds(amount, 'withdrawal', reference)
        
        if success:
            # Create transaction record
            SavingsTransaction.objects.create(
                savings_account=account,
                transaction_type='withdrawal',
                amount=-amount,
                reference=reference,
                balance_after=account.current_balance,
                notes=notes,
                processed_by=request.user
            )
            
            serializer = self.get_serializer(account)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'Withdrawal failed'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        """Get savings account transactions"""
        account = self.get_object()
        transactions = account.transactions.all().order_by('-transaction_date')
        
        # Filter by date range
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        if start_date:
            transactions = transactions.filter(transaction_date__date__gte=start_date)
        if end_date:
            transactions = transactions.filter(transaction_date__date__lte=end_date)
        
        serializer = SavingsTransactionSerializer(transactions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set account as default for auto-save"""
        account = self.get_object()
        
        # Remove default from other accounts
        SavingsAccount.objects.filter(user=request.user, is_default=True).update(is_default=False)
        
        # Set this account as default
        account.is_default = True
        account.save()
        
        serializer = self.get_serializer(account)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get savings dashboard statistics"""
        accounts = self.get_queryset()
        
        stats = {
            'total_accounts': accounts.count(),
            'active_accounts': accounts.filter(status='active').count(),
            'total_balance': sum(account.current_balance for account in accounts),
            'total_interest_earned': sum(account.total_interest_earned for account in accounts),
            'auto_save_enabled': accounts.filter(auto_save_enabled=True).count(),
            'accounts_with_targets': accounts.filter(target_amount__gt=0).count(),
            'total_target_amount': sum(account.target_amount for account in accounts if account.target_amount),
            'monthly_auto_save': sum(
                account.current_balance * account.auto_save_percentage / 100 
                for account in accounts.filter(auto_save_enabled=True)
            )
        }
        
        return Response(stats)


class SavingsTransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing savings transactions
    """
    serializer_class = SavingsTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter savings transactions by user's accounts"""
        return SavingsTransaction.objects.filter(
            savings_account__user=self.request.user
        ).order_by('-transaction_date')
    
    @action(detail=False, methods=['get'])
    def deposits(self, request):
        """Get deposit transactions"""
        deposits = self.get_queryset().filter(amount__gt=0)
        serializer = self.get_serializer(deposits, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def withdrawals(self, request):
        """Get withdrawal transactions"""
        withdrawals = self.get_queryset().filter(amount__lt=0)
        serializer = self.get_serializer(withdrawals, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def auto_saves(self, request):
        """Get auto-save transactions"""
        auto_saves = self.get_queryset().filter(transaction_type='auto_save')
        serializer = self.get_serializer(auto_saves, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's transactions"""
        today = timezone.now().date()
        transactions = self.get_queryset().filter(transaction_date__date=today)
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get transaction summary"""
        days = int(request.query_params.get('days', 30))
        since_date = timezone.now() - timedelta(days=days)
        
        transactions = self.get_queryset().filter(transaction_date__gte=since_date)
        
        summary = {
            'total_transactions': transactions.count(),
            'total_deposits': sum(t.amount for t in transactions.filter(amount__gt=0)),
            'total_withdrawals': abs(sum(t.amount for t in transactions.filter(amount__lt=0))),
            'net_flow': sum(t.amount for t in transactions),
            'transactions_by_type': {},
            'daily_breakdown': []
        }
        
        # Transactions by type
        for transaction_type, _ in SavingsTransaction.TRANSACTION_TYPES:
            type_transactions = transactions.filter(transaction_type=transaction_type)
            summary['transactions_by_type'][transaction_type] = {
                'count': type_transactions.count(),
                'amount': sum(t.amount for t in type_transactions)
            }
        
        # Daily breakdown
        for i in range(days):
            date = (timezone.now() - timedelta(days=i)).date()
            day_transactions = transactions.filter(transaction_date__date=date)
            
            daily_data = {
                'date': date,
                'deposits': sum(t.amount for t in day_transactions.filter(amount__gt=0)),
                'withdrawals': abs(sum(t.amount for t in day_transactions.filter(amount__lt=0))),
                'transactions_count': day_transactions.count()
            }
            daily_data['net_flow'] = daily_data['deposits'] - daily_data['withdrawals']
            summary['daily_breakdown'].append(daily_data)
        
        return Response(summary)


class SavingsGoalViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing savings goals
    """
    serializer_class = SavingsGoalSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter savings goals by user's accounts"""
        return SavingsGoal.objects.filter(
            savings_account__user=self.request.user
        ).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set processed_by when creating goal"""
        serializer.save()
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active savings goals"""
        goals = self.get_queryset().filter(status='active')
        serializer = self.get_serializer(goals, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def completed(self, request):
        """Get completed savings goals"""
        goals = self.get_queryset().filter(status='completed')
        serializer = self.get_serializer(goals, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def contribute(self, request, pk=None):
        """Contribute to savings goal"""
        goal = self.get_object()
        amount = Decimal(str(request.data.get('amount', 0)))
        reference = request.data.get('reference', 'Goal contribution')
        
        if amount <= 0:
            return Response(
                {'error': 'Contribution amount must be positive'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if goal.status != 'active':
            return Response(
                {'error': 'Goal is not active'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if goal.current_amount + amount > goal.target_amount:
            return Response(
                {'error': 'Contribution would exceed target amount'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with db_transaction.atomic():
            # Update goal amount
            goal.current_amount += amount
            if goal.current_amount >= goal.target_amount:
                goal.status = 'completed'
                goal.completed_date = timezone.now()
            goal.save()
            
            # Add funds to savings account
            account = goal.savings_account
            account.add_funds(amount, 'deposit', reference)
            
            # Create transaction record
            SavingsTransaction.objects.create(
                savings_account=account,
                transaction_type='deposit',
                amount=amount,
                reference=reference,
                balance_after=account.current_balance,
                notes=f"Contribution to goal: {goal.name}",
                processed_by=request.user
            )
        
        serializer = self.get_serializer(goal)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """Pause savings goal"""
        goal = self.get_object()
        
        if goal.status != 'active':
            return Response(
                {'error': 'Only active goals can be paused'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        goal.status = 'paused'
        goal.save()
        
        serializer = self.get_serializer(goal)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        """Resume paused savings goal"""
        goal = self.get_object()
        
        if goal.status != 'paused':
            return Response(
                {'error': 'Only paused goals can be resumed'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        goal.status = 'active'
        goal.save()
        
        serializer = self.get_serializer(goal)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get savings goals dashboard statistics"""
        goals = self.get_queryset()
        
        stats = {
            'total_goals': goals.count(),
            'active_goals': goals.filter(status='active').count(),
            'completed_goals': goals.filter(status='completed').count(),
            'paused_goals': goals.filter(status='paused').count(),
            'total_target_amount': sum(goal.target_amount for goal in goals),
            'total_current_amount': sum(goal.current_amount for goal in goals),
            'total_remaining': sum(goal.remaining_amount for goal in goals),
            'average_progress': sum(goal.progress_percentage for goal in goals) / goals.count() if goals.count() > 0 else 0,
            'goals_due_soon': goals.filter(
                status='active',
                target_date__lte=timezone.now().date() + timedelta(days=30)
            ).count()
        }
        
        return Response(stats)