# backend/apps/ai_categorization/serializers.py
"""
AI categorization serializers
"""

from rest_framework import serializers
from .models import CategoryPrediction, TrainingData, ModelPerformance


class CategoryPredictionSerializer(serializers.ModelSerializer):
    """
    Serializer for AI category predictions
    """
    category_name = serializers.ReadOnlyField(source='predicted_category.name')
    actual_category_name = serializers.ReadOnlyField(source='actual_category.name')
    is_high_confidence = serializers.ReadOnlyField()
    is_correct_prediction = serializers.ReadOnlyField()
    
    class Meta:
        model = CategoryPrediction
        fields = [
            'id', 'input_text', 'predicted_category', 'category_name',
            'confidence_score', 'alternative_predictions', 'actual_category',
            'actual_category_name', 'status', 'user_feedback', 'model_version',
            'processing_time_ms', 'context_data', 'is_high_confidence',
            'is_correct_prediction', 'created_at'
        ]
        read_only_fields = [
            'id', 'category_name', 'actual_category_name', 'predicted_category',
            'confidence_score', 'alternative_predictions', 'model_version',
            'processing_time_ms', 'is_high_confidence', 'is_correct_prediction',
            'created_at'
        ]


class CategoryPredictionRequestSerializer(serializers.Serializer):
    """
    Serializer for category prediction requests
    """
    text_input = serializers.CharField(max_length=500)
    context = serializers.DictField(required=False, default=dict)
    
    def validate_text_input(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Input text must be at least 2 characters long")
        return value.strip()


class ModelPerformanceSerializer(serializers.ModelSerializer):
    """
    Serializer for AI model performance metrics
    """
    
    class Meta:
        model = ModelPerformance
        fields = [
            'id', 'model_version', 'model_type', 'accuracy', 'precision',
            'recall', 'f1_score', 'confusion_matrix', 'class_metrics',
            'training_samples', 'validation_samples', 'training_time_seconds',
            'is_deployed', 'deployed_at', 'hyperparameters', 'notes', 'created_at'
        ]
        read_only_fields = [
            'id', 'accuracy', 'precision', 'recall', 'f1_score',
            'confusion_matrix', 'class_metrics', 'training_samples',
            'validation_samples', 'training_time_seconds', 'is_deployed',
            'deployed_at', 'created_at'
        ]


