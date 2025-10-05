# backend/apps/ai_categorization/admin.py
"""
AI Categorization admin configuration
"""

from django.contrib import admin
from .models import CategoryPrediction, TrainingData, ModelPerformance


@admin.register(CategoryPrediction)
class CategoryPredictionAdmin(admin.ModelAdmin):
    list_display = ['input_text', 'predicted_category', 'confidence_score', 'status', 'is_correct_prediction', 'created_at']
    list_filter = ['status', 'model_version', 'created_at']
    search_fields = ['input_text', 'user__email']
    readonly_fields = ['predicted_category', 'confidence_score', 'model_version', 'processing_time_ms', 'is_high_confidence', 'is_correct_prediction', 'created_at']


@admin.register(TrainingData)
class TrainingDataAdmin(admin.ModelAdmin):
    list_display = ['text_input', 'category', 'source', 'language', 'is_validated', 'validation_score', 'usage_count']
    list_filter = ['category', 'source', 'language', 'is_validated', 'status']
    search_fields = ['text_input', 'processed_text']
    readonly_fields = ['usage_count', 'created_at', 'updated_at']


@admin.register(ModelPerformance)
class ModelPerformanceAdmin(admin.ModelAdmin):
    list_display = ['model_version', 'model_type', 'accuracy', 'precision', 'recall', 'f1_score', 'is_deployed', 'created_at']
    list_filter = ['model_type', 'is_deployed', 'created_at']
    search_fields = ['model_version']
    readonly_fields = ['created_at']


