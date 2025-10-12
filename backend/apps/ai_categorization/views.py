# backend/apps/ai_categorization/views.py
"""
AI categorization API views for smart transaction classification
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
import time
import random

from .models import CategoryPrediction, TrainingData, ModelPerformance
from .serializers import (
    CategoryPredictionSerializer,
    CategoryPredictionRequestSerializer,
    TrainingDataSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for AI categorization views"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class CategoryPredictionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing AI category predictions
    """
    serializer_class = CategoryPredictionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter predictions by user"""
        return CategoryPrediction.objects.filter(user=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set user when creating prediction"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def predict(self, request):
        """Get AI category prediction for input text"""
        serializer = CategoryPredictionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        text_input = serializer.validated_data['text_input']
        context = serializer.validated_data.get('context', {})
        
        # Simulate AI processing time
        start_time = time.time()
        
        # Mock AI prediction (in production, this would call the actual AI service)
        prediction_result = self._mock_ai_prediction(text_input, context)
        
        processing_time = int((time.time() - start_time) * 1000)  # Convert to milliseconds
        
        # Create prediction record
        prediction = CategoryPrediction.objects.create(
            user=request.user,
            input_text=text_input,
            preprocessed_text=self._preprocess_text(text_input),
            predicted_category=prediction_result['category'],
            confidence_score=prediction_result['confidence'],
            alternative_predictions=prediction_result['alternatives'],
            model_version='v1.0',
            processing_time_ms=processing_time,
            context_data=context
        )
        
        response_serializer = CategoryPredictionSerializer(prediction)
        return Response(response_serializer.data)
    
    def _mock_ai_prediction(self, text_input, context):
        """Mock AI prediction for demonstration"""
        # This is a simplified mock - in production, you'd call the actual AI service
        from apps.inventory.models import ProductCategory
        
        # Simple keyword matching for demonstration
        text_lower = text_input.lower()
        
        # Define keyword mappings
        keyword_mappings = {
            'food_beverages': ['food', 'drink', 'rice', 'bread', 'milk', 'water', 'indomie', 'milo'],
            'electronics': ['phone', 'charger', 'battery', 'tv', 'radio', 'computer'],
            'clothing': ['shirt', 'dress', 'shoe', 'cloth', 'fashion'],
            'household': ['soap', 'detergent', 'brush', 'broom', 'cleaning'],
            'cosmetics': ['cream', 'powder', 'makeup', 'perfume', 'lotion'],
            'stationery': ['pen', 'paper', 'book', 'notebook', 'pencil'],
            'pharmacy': ['medicine', 'drug', 'tablet', 'syrup', 'vitamin'],
            'services': ['service', 'repair', 'maintenance', 'consultation'],
            'airtime_data': ['airtime', 'data', 'credit', 'recharge', 'internet']
        }
        
        # Find best matching category
        best_category = None
        best_score = 0
        
        for category_type, keywords in keyword_mappings.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > best_score:
                best_score = score
                best_category = category_type
        
        # Get or create category
        if best_category:
            category = ProductCategory.objects.filter(category_type=best_category).first()
            if not category:
                category = ProductCategory.objects.create(
                    name=best_category.replace('_', ' ').title(),
                    category_type=best_category,
                    description=f"Auto-generated category for {best_category}"
                )
        else:
            # Default to 'other' category
            category = ProductCategory.objects.filter(category_type='other').first()
            if not category:
                category = ProductCategory.objects.create(
                    name='Other',
                    category_type='other',
                    description='Default category for uncategorized items'
                )
        
        # Calculate confidence based on keyword matches
        confidence = min(0.9, 0.3 + (best_score * 0.1))
        
        # Generate alternative predictions
        alternatives = []
        for alt_category_type, alt_keywords in keyword_mappings.items():
            if alt_category_type != best_category:
                alt_score = sum(1 for keyword in alt_keywords if keyword in text_lower)
                if alt_score > 0:
                    alt_category = ProductCategory.objects.filter(category_type=alt_category_type).first()
                    if alt_category:
                        alternatives.append({
                            'category_id': str(alt_category.id),
                            'category_name': alt_category.name,
                            'confidence': min(0.8, 0.2 + (alt_score * 0.1))
                        })
        
        return {
            'category': category,
            'confidence': confidence,
            'alternatives': alternatives[:3]  # Top 3 alternatives
        }
    
    def _preprocess_text(self, text):
        """Preprocess text for AI model"""
        # Simple preprocessing - in production, you'd do more sophisticated text cleaning
        return text.lower().strip()
    
    @action(detail=True, methods=['post'])
    def provide_feedback(self, request, pk=None):
        """Provide feedback on prediction accuracy"""
        prediction = self.get_object()
        actual_category_id = request.data.get('actual_category_id')
        feedback = request.data.get('feedback', '')
        
        if not actual_category_id:
            return Response(
                {'error': 'Actual category ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from apps.inventory.models import ProductCategory
            actual_category = ProductCategory.objects.get(id=actual_category_id)
            
            prediction.actual_category = actual_category
            prediction.user_feedback = feedback
            
            if actual_category == prediction.predicted_category:
                prediction.status = 'accepted'
            else:
                prediction.status = 'rejected'
            
            prediction.save()
            
            # Create training data from feedback
            TrainingData.objects.create(
                text_input=prediction.input_text,
                processed_text=prediction.preprocessed_text,
                category=actual_category,
                source='feedback',
                contributed_by=request.user,
                is_validated=True,
                validation_score=1.0
            )
            
            serializer = self.get_serializer(prediction)
            return Response(serializer.data)
            
        except ProductCategory.DoesNotExist:
            return Response(
                {'error': 'Category not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def accuracy_stats(self, request):
        """Get prediction accuracy statistics"""
        predictions = self.get_queryset().filter(
            actual_category__isnull=False
        )
        
        total_predictions = predictions.count()
        correct_predictions = predictions.filter(
            predicted_category=F('actual_category')
        ).count()
        
        accuracy = (correct_predictions / total_predictions * 100) if total_predictions > 0 else 0
        
        # Confidence distribution
        high_confidence = predictions.filter(confidence_score__gte=0.8).count()
        medium_confidence = predictions.filter(
            confidence_score__gte=0.5, 
            confidence_score__lt=0.8
        ).count()
        low_confidence = predictions.filter(confidence_score__lt=0.5).count()
        
        stats = {
            'total_predictions': total_predictions,
            'correct_predictions': correct_predictions,
            'accuracy_percentage': round(accuracy, 2),
            'confidence_distribution': {
                'high': high_confidence,
                'medium': medium_confidence,
                'low': low_confidence
            },
            'average_confidence': predictions.aggregate(avg_confidence=Avg('confidence_score'))['avg_confidence'] or 0
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def recent_predictions(self, request):
        """Get recent predictions"""
        days = int(request.query_params.get('days', 7))
        since_date = timezone.now() - timedelta(days=days)
        
        predictions = self.get_queryset().filter(created_at__gte=since_date)
        serializer = self.get_serializer(predictions, many=True)
        return Response(serializer.data)


class TrainingDataViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing AI training data
    """
    serializer_class = TrainingDataSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter training data by user contributions"""
        if self.request.user.user_type == 'admin':
            return TrainingData.objects.all().order_by('-created_at')
        else:
            return TrainingData.objects.filter(
                contributed_by=self.request.user
            ).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set contributor when creating training data"""
        serializer.save(contributed_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def validated(self, request):
        """Get validated training data"""
        data = self.get_queryset().filter(is_validated=True)
        serializer = self.get_serializer(data, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get training data grouped by category"""
        category_id = request.query_params.get('category_id')
        if not category_id:
            return Response(
                {'error': 'Category ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = self.get_queryset().filter(category_id=category_id)
        serializer = self.get_serializer(data, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """Validate training data (admin only)"""
        if request.user.user_type != 'admin':
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        training_data = self.get_object()
        is_valid = request.data.get('is_valid', True)
        validation_score = request.data.get('validation_score', 1.0)
        
        training_data.is_validated = is_valid
        training_data.validation_score = validation_score
        training_data.status = 'validated' if is_valid else 'discarded'
        training_data.save()
        
        serializer = self.get_serializer(training_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get training data statistics"""
        data = self.get_queryset()
        
        stats = {
            'total_samples': data.count(),
            'validated_samples': data.filter(is_validated=True).count(),
            'by_category': {},
            'by_language': {},
            'by_source': {}
        }
        
        # By category
        for category_data in data.values('category__name').annotate(count=Count('id')):
            stats['by_category'][category_data['category__name']] = category_data['count']
        
        # By language
        for lang_data in data.values('language').annotate(count=Count('id')):
            stats['by_language'][lang_data['language']] = lang_data['count']
        
        # By source
        for source_data in data.values('source').annotate(count=Count('id')):
            stats['by_source'][source_data['source']] = source_data['count']
        
        return Response(stats)


class ModelPerformanceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing AI model performance metrics
    """
    queryset = ModelPerformance.objects.all()
    serializer_class = None  # Will be defined inline
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter model performance by user type"""
        if self.request.user.user_type == 'admin':
            return ModelPerformance.objects.all().order_by('-created_at')
        else:
            # Regular users can only see deployed models
            return ModelPerformance.objects.filter(is_deployed=True).order_by('-created_at')
    
    def get_serializer_class(self):
        """Return appropriate serializer"""
        from .serializers import ModelPerformanceSerializer
        return ModelPerformanceSerializer
    
    @action(detail=False, methods=['get'])
    def current_model(self, request):
        """Get current deployed model performance"""
        current_model = self.get_queryset().filter(is_deployed=True).first()
        
        if not current_model:
            return Response(
                {'error': 'No deployed model found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(current_model)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def performance_history(self, request):
        """Get model performance history"""
        models = self.get_queryset().order_by('created_at')
        
        history = {
            'dates': [],
            'accuracy': [],
            'precision': [],
            'recall': [],
            'f1_score': []
        }
        
        for model in models:
            history['dates'].append(model.created_at.strftime('%Y-%m-%d'))
            history['accuracy'].append(model.accuracy)
            history['precision'].append(model.precision)
            history['recall'].append(model.recall)
            history['f1_score'].append(model.f1_score)
        
        return Response(history)