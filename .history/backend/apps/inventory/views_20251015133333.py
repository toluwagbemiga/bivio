# backend/apps/inventory/views.py
"""
Inventory management API views for POS system
Handles products, categories, and stock movements
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import ProductCategory, Product, StockMovement
from .serializers import (
    ProductCategorySerializer, 
    ProductSerializer, 
    StockMovementSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for inventory views"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product categories
    """
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter categories by user's products"""
        return ProductCategory.objects.filter(
            products__user=self.request.user
        ).distinct().order_by('name')
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active categories"""
        categories = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Get products in this category"""
        category = self.get_object()
        products = Product.objects.filter(
            category=category,
            user=request.user,
            is_active=True
        ).order_by('name')
        
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get category statistics"""
        category = self.get_object()
        products = Product.objects.filter(
            category=category,
            user=request.user
        )
        
        stats = {
            'total_products': products.count(),
            'active_products': products.filter(is_active=True).count(),
            'low_stock_products': products.filter(is_low_stock=True).count(),
            'out_of_stock_products': products.filter(is_out_of_stock=True).count(),
            'total_inventory_value': sum(p.current_stock * p.cost_price for p in products),
            'total_sales_today': sum(
                p.total_sold for p in products 
                if p.last_sold_date and p.last_sold_date.date() == timezone.now().date()
            )
        }
        
        return Response(stats)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing products with inventory tracking
    """
     queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter products by user"""
        queryset = Product.objects.filter(user=self.request.user)
        
        # Filter by category if provided
        category_id = self.request.query_params.get('category', None)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Filter by stock status
        stock_status = self.request.query_params.get('stock_status', None)
        if stock_status == 'low':
            queryset = queryset.filter(is_low_stock=True)
        elif stock_status == 'out':
            queryset = queryset.filter(is_out_of_stock=True)
        elif stock_status == 'in_stock':
            queryset = queryset.filter(is_out_of_stock=False, is_low_stock=False)
        
        # Filter by product type
        product_type = self.request.query_params.get('product_type', None)
        if product_type:
            queryset = queryset.filter(product_type=product_type)
        
        # Search by name or SKU
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(sku__icontains=search) |
                Q(barcode__icontains=search) |
                Q(local_names__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set user when creating product"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get products with low stock"""
        products = self.get_queryset().filter(is_low_stock=True)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def out_of_stock(self, request):
        """Get out of stock products"""
        products = self.get_queryset().filter(is_out_of_stock=True)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def top_selling(self, request):
        """Get top selling products"""
        days = int(request.query_params.get('days', 30))
        since_date = timezone.now() - timedelta(days=days)
        
        products = self.get_queryset().filter(
            last_sold_date__gte=since_date
        ).order_by('-total_sold')[:10]
        
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def slow_moving(self, request):
        """Get slow moving products"""
        days = int(request.query_params.get('days', 90))
        since_date = timezone.now() - timedelta(days=days)
        
        products = self.get_queryset().filter(
            Q(last_sold_date__lt=since_date) | Q(last_sold_date__isnull=True),
            is_active=True
        ).order_by('last_sold_date')
        
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def adjust_stock(self, request, pk=None):
        """Adjust product stock level"""
        product = self.get_object()
        quantity_change = Decimal(str(request.data.get('quantity_change', 0)))
        movement_type = request.data.get('movement_type', 'adjustment')
        notes = request.data.get('notes', '')
        
        if not quantity_change:
            return Response(
                {'error': 'Quantity change is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create stock movement record
        stock_before = product.current_stock
        product.current_stock += quantity_change
        
        if product.current_stock < 0 and not product.allow_negative_stock:
            return Response(
                {'error': 'Stock cannot go negative'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        product.save()
        
        # Create stock movement
        StockMovement.objects.create(
            product=product,
            movement_type=movement_type,
            quantity=abs(quantity_change),
            stock_before=stock_before,
            stock_after=product.current_stock,
            notes=notes,
            created_by=request.user
        )
        
        serializer = self.get_serializer(product)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def restock(self, request, pk=None):
        """Restock product"""
        product = self.get_object()
        quantity = Decimal(str(request.data.get('quantity', 0)))
        unit_cost = Decimal(str(request.data.get('unit_cost', product.cost_price)))
        notes = request.data.get('notes', 'Restock')
        
        if quantity <= 0:
            return Response(
                {'error': 'Quantity must be positive'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update product stock and cost
        stock_before = product.current_stock
        product.current_stock += quantity
        product.cost_price = unit_cost  # Update cost price
        product.last_restocked_date = timezone.now()
        product.save()
        
        # Create stock movement
        StockMovement.objects.create(
            product=product,
            movement_type='purchase',
            quantity=quantity,
            unit_cost=unit_cost,
            stock_before=stock_before,
            stock_after=product.current_stock,
            notes=notes,
            created_by=request.user
        )
        
        serializer = self.get_serializer(product)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stock_history(self, request, pk=None):
        """Get stock movement history for product"""
        product = self.get_object()
        movements = StockMovement.objects.filter(product=product).order_by('-created_at')
        
        serializer = StockMovementSerializer(movements, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get inventory dashboard statistics"""
        products = self.get_queryset()
        
        stats = {
            'total_products': products.count(),
            'active_products': products.filter(is_active=True).count(),
            'low_stock_products': products.filter(is_low_stock=True).count(),
            'out_of_stock_products': products.filter(is_out_of_stock=True).count(),
            'total_inventory_value': sum(p.current_stock * p.cost_price for p in products),
            'total_sales_today': sum(
                p.total_sold for p in products 
                if p.last_sold_date and p.last_sold_date.date() == timezone.now().date()
            ),
            'categories_count': ProductCategory.objects.filter(
                products__user=request.user
            ).distinct().count()
        }
        
        return Response(stats)


class StockMovementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing stock movements
    """
    serializer_class = StockMovementSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter stock movements by user's products"""
        return StockMovement.objects.filter(
            product__user=self.request.user
        ).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set created_by when creating stock movement"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's stock movements"""
        today = timezone.now().date()
        movements = self.get_queryset().filter(created_at__date=today)
        serializer = self.get_serializer(movements, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get stock movements by type"""
        movement_type = request.query_params.get('type', None)
        if not movement_type:
            return Response(
                {'error': 'Movement type is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        movements = self.get_queryset().filter(movement_type=movement_type)
        serializer = self.get_serializer(movements, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get stock movement summary"""
        days = int(request.query_params.get('days', 30))
        since_date = timezone.now() - timedelta(days=days)
        
        movements = self.get_queryset().filter(created_at__gte=since_date)
        
        summary = {
            'total_movements': movements.count(),
            'movements_by_type': {},
            'total_quantity_in': 0,
            'total_quantity_out': 0,
            'net_movement': 0
        }
        
        for movement in movements:
            movement_type = movement.movement_type
            if movement_type not in summary['movements_by_type']:
                summary['movements_by_type'][movement_type] = 0
            summary['movements_by_type'][movement_type] += 1
            
            if movement_type in ['purchase', 'return']:
                summary['total_quantity_in'] += movement.quantity
            elif movement_type in ['sale', 'damage']:
                summary['total_quantity_out'] += movement.quantity
        
        summary['net_movement'] = summary['total_quantity_in'] - summary['total_quantity_out']
        
        return Response(summary)