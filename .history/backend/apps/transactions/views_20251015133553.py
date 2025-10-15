# backend/apps/transactions/views.py
"""
Transaction management API views for POS system
Handles sales, purchases, and transaction categorization
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

from .models import Transaction, TransactionItem, TransactionCategory
from .serializers import (
    TransactionSerializer, 
    TransactionCreateSerializer,
    TransactionItemSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for transaction views"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class TransactionCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing transaction categories
    """
    queryset = TransactionCategory.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_serializer_class(self):
        """Return appropriate serializer"""
        from .serializers import TransactionCategorySerializer
        return TransactionCategorySerializer
    
    def get_queryset(self):
        """Filter categories by user's transactions"""
        return TransactionCategory.objects.filter(
            transactions__user=self.request.user
        ).distinct().order_by('name')
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active categories"""
        categories = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        """Get transactions in this category"""
        category = self.get_object()
        transactions = Transaction.objects.filter(
            transaction_category=category,
            user=request.user
        ).order_by('-transaction_date')
        
        serializer = TransactionSerializer(transactions, many=True, context={'request': request})
        return Response(serializer.data)


class TransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing POS transactions
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter transactions by user"""
        queryset = Transaction.objects.filter(user=self.request.user)
        
        # Filter by transaction type
        transaction_type = self.request.query_params.get('type', None)
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        
        # Filter by payment method
        payment_method = self.request.query_params.get('payment_method', None)
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date:
            queryset = queryset.filter(transaction_date__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(transaction_date__date__lte=end_date)
        
        # Search by transaction number or customer
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(transaction_number__icontains=search) |
                Q(counterparty_name__icontains=search) |
                Q(counterparty_phone__icontains=search)
            )
        
        return queryset.order_by('-transaction_date')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return TransactionCreateSerializer
        return TransactionSerializer
    
    def perform_create(self, serializer):
        """Set user when creating transaction"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's transactions"""
        today = timezone.now().date()
        transactions = self.get_queryset().filter(transaction_date__date=today)
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def sales(self, request):
        """Get sales transactions"""
        sales = self.get_queryset().filter(transaction_type='sale')
        serializer = self.get_serializer(sales, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def purchases(self, request):
        """Get purchase transactions"""
        purchases = self.get_queryset().filter(transaction_type='purchase')
        serializer = self.get_serializer(purchases, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get transaction dashboard statistics"""
        today = timezone.now().date()
        this_month = timezone.now().replace(day=1).date()
        
        transactions = self.get_queryset()
        today_transactions = transactions.filter(transaction_date__date=today)
        month_transactions = transactions.filter(transaction_date__date__gte=this_month)
        
        stats = {
            'today': {
                'total_transactions': today_transactions.count(),
                'total_amount': sum(t.total_amount for t in today_transactions),
                'sales_count': today_transactions.filter(transaction_type='sale').count(),
                'sales_amount': sum(t.total_amount for t in today_transactions.filter(transaction_type='sale')),
            },
            'this_month': {
                'total_transactions': month_transactions.count(),
                'total_amount': sum(t.total_amount for t in month_transactions),
                'sales_count': month_transactions.filter(transaction_type='sale').count(),
                'sales_amount': sum(t.total_amount for t in month_transactions.filter(transaction_type='sale')),
            },
            'payment_methods': {},
            'top_categories': []
        }
        
        # Payment method breakdown
        for method, _ in Transaction.PAYMENT_METHODS:
            count = month_transactions.filter(payment_method=method).count()
            amount = sum(t.total_amount for t in month_transactions.filter(payment_method=method))
            stats['payment_methods'][method] = {'count': count, 'amount': amount}
        
        # Top transaction categories
        category_stats = month_transactions.values('transaction_category__name').annotate(
            count=Count('id'),
            total_amount=Sum('total_amount')
        ).order_by('-total_amount')[:5]
        
        stats['top_categories'] = list(category_stats)
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def cash_flow(self, request):
        """Get cash flow data"""
        days = int(request.query_params.get('days', 30))
        since_date = timezone.now() - timedelta(days=days)
        
        transactions = self.get_queryset().filter(transaction_date__gte=since_date)
        
        cash_flow = {
            'inflows': sum(t.total_amount for t in transactions.filter(flow_direction='inward')),
            'outflows': sum(t.total_amount for t in transactions.filter(flow_direction='outward')),
            'net_flow': 0,
            'daily_breakdown': []
        }
        
        cash_flow['net_flow'] = cash_flow['inflows'] - cash_flow['outflows']
        
        # Daily breakdown
        for i in range(days):
            date = (timezone.now() - timedelta(days=i)).date()
            day_transactions = transactions.filter(transaction_date__date=date)
            
            daily_data = {
                'date': date,
                'inflows': sum(t.total_amount for t in day_transactions.filter(flow_direction='inward')),
                'outflows': sum(t.total_amount for t in day_transactions.filter(flow_direction='outward')),
                'transactions_count': day_transactions.count()
            }
            daily_data['net_flow'] = daily_data['inflows'] - daily_data['outflows']
            cash_flow['daily_breakdown'].append(daily_data)
        
        return Response(cash_flow)
    
    @action(detail=True, methods=['post'])
    def categorize(self, request, pk=None):
        """Manually categorize a transaction"""
        transaction = self.get_object()
        category_id = request.data.get('category_id')
        
        if not category_id:
            return Response(
                {'error': 'Category ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            category = TransactionCategory.objects.get(id=category_id)
            transaction.transaction_category = category
            transaction.save()
            
            serializer = self.get_serializer(transaction)
            return Response(serializer.data)
        except TransactionCategory.DoesNotExist:
            return Response(
                {'error': 'Category not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        """Process a refund for a transaction"""
        transaction = self.get_object()
        refund_amount = Decimal(str(request.data.get('refund_amount', transaction.total_amount)))
        reason = request.data.get('reason', 'Refund')
        
        if refund_amount > transaction.total_amount:
            return Response(
                {'error': 'Refund amount cannot exceed transaction amount'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if transaction.transaction_type != 'sale':
            return Response(
                {'error': 'Only sales transactions can be refunded'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with db_transaction.atomic():
            # Create refund transaction
            refund_transaction = Transaction.objects.create(
                user=transaction.user,
                transaction_category=transaction.transaction_category,
                transaction_type='return',
                flow_direction='outward',
                total_amount=refund_amount,
                payment_method=transaction.payment_method,
                amount_paid=refund_amount,
                counterparty_name=transaction.counterparty_name,
                counterparty_phone=transaction.counterparty_phone,
                notes=f"Refund for {transaction.transaction_number}: {reason}",
                status='completed'
            )
            
            # Reverse stock movements for refunded items
            for item in transaction.items.all():
                if item.product and item.product.track_inventory:
                    # Create return stock movement
                    from apps.inventory.models import StockMovement
                    StockMovement.objects.create(
                        product=item.product,
                        movement_type='return',
                        quantity=item.quantity,
                        unit_cost=item.unit_cost,
                        stock_before=item.product.current_stock,
                        stock_after=item.product.current_stock + item.quantity,
                        reference_number=refund_transaction.transaction_number,
                        notes=f"Refund for {transaction.transaction_number}",
                        created_by=request.user
                    )
                    
                    # Update product stock
                    item.product.current_stock += item.quantity
                    item.product.save()
            
            serializer = self.get_serializer(refund_transaction)
            return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def bulk_categorize(self, request):
        """Bulk categorize multiple transactions"""
        transaction_ids = request.data.get('transaction_ids', [])
        category_id = request.data.get('category_id')
        
        if not transaction_ids or not category_id:
            return Response(
                {'error': 'Transaction IDs and category ID are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            category = TransactionCategory.objects.get(id=category_id)
            transactions = Transaction.objects.filter(
                id__in=transaction_ids,
                user=request.user
            )
            
            updated_count = transactions.update(transaction_category=category)
            
            return Response({
                'message': f'Successfully categorized {updated_count} transactions',
                'updated_count': updated_count
            })
        except TransactionCategory.DoesNotExist:
            return Response(
                {'error': 'Category not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class TransactionItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing transaction items
    """
    serializer_class = TransactionItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter transaction items by user's transactions"""
        return TransactionItem.objects.filter(
            transaction__user=self.request.user
        ).order_by('-transaction__transaction_date')
    
    @action(detail=False, methods=['get'])
    def top_selling(self, request):
        """Get top selling items"""
        days = int(request.query_params.get('days', 30))
        since_date = timezone.now() - timedelta(days=days)
        
        items = self.get_queryset().filter(
            transaction__transaction_date__gte=since_date,
            transaction__transaction_type='sale'
        ).values('product_name').annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('line_total'),
            transaction_count=Count('transaction')
        ).order_by('-total_quantity')[:10]
        
        return Response(items)
    
    @action(detail=False, methods=['get'])
    def by_product(self, request):
        """Get transaction items grouped by product"""
        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response(
                {'error': 'Product ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        items = self.get_queryset().filter(product_id=product_id)
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)