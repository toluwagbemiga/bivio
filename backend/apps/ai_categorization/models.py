# backend/apps/ai_categorization/models.py
"""
AI categorization models for smart transaction classification
"""

import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from apps.users.models import User
from apps.inventory.models import ProductCategory


class CategoryPrediction(models.Model):
    """
    AI predictions for transaction categorization
    """
    
    PREDICTION_STATUS = [
        ('pending', 'Pending Review'),
        ('accepted', 'Accepted by User'),
        ('rejected', 'Rejected by User'),
        ('auto_applied', 'Auto-applied'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='category_predictions'
    )
    
    # Input Data
    input_text = models.TextField(
        help_text='Original text input by user (product name, description, etc.)'
    )
    preprocessed_text = models.TextField(
        blank=True,
        help_text='Cleaned and preprocessed text for ML model'
    )
    
    # AI Predictions
    predicted_category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name='predictions'
    )
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text='AI confidence score (0.0 to 1.0)'
    )
    
    # Alternative Predictions
    alternative_predictions = models.JSONField(
        default=list,
        blank=True,
        help_text='List of alternative category predictions with scores'
    )
    
    # User Feedback
    actual_category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='actual_classifications',
        help_text='Category chosen by user (for training)'
    )
    status = models.CharField(max_length=20, choices=PREDICTION_STATUS, default='pending')
    user_feedback = models.TextField(blank=True)
    
    # Model Information
    model_version = models.CharField(
        max_length=50,
        default='v1.0',
        help_text='Version of ML model used for prediction'
    )
    processing_time_ms = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Time taken for prediction in milliseconds'
    )
    
    # Context Information
    context_data = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional context (user history, location, etc.)'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'category_predictions'
        verbose_name = _('Category Prediction')
        verbose_name_plural = _('Category Predictions')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['predicted_category']),
            models.Index(fields=['confidence_score']),
            models.Index(fields=['model_version']),
        ]
    
    def __str__(self):
        return f"Prediction: '{self.input_text[:50]}' -> {self.predicted_category.name}"
    
    @property
    def is_high_confidence(self):
        """Check if prediction has high confidence (>= 0.8)"""
        return self.confidence_score >= 0.8
    
    @property
    def is_correct_prediction(self):
        """Check if AI prediction matched user's choice"""
        return (
            self.actual_category and 
            self.predicted_category == self.actual_category
        )


class TrainingData(models.Model):
    """
    Training data for improving AI categorization
    """
    
    DATA_SOURCES = [
        ('user_input', 'Direct User Input'),
        ('transaction', 'Transaction Data'),
        ('inventory', 'Inventory Data'),
        ('feedback', 'User Feedback'),
        ('manual', 'Manual Entry'),
        ('bulk_import', 'Bulk Import'),
    ]
    
    DATA_STATUS = [
        ('raw', 'Raw Data'),
        ('processed', 'Processed'),
        ('validated', 'Validated'),
        ('used_for_training', 'Used for Training'),
        ('discarded', 'Discarded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Text Data
    text_input = models.TextField(
        help_text='Original text (product names, descriptions, local names)'
    )
    processed_text = models.TextField(
        blank=True,
        help_text='Cleaned and normalized text'
    )
    
    # Category Information
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name='training_data'
    )
    
    # Metadata
    source = models.CharField(max_length=20, choices=DATA_SOURCES, default='user_input')
    language = models.CharField(
        max_length=20,
        default='en',
        help_text='Language of the text (en, ha, ig, yo, pidgin)'
    )
    region = models.CharField(
        max_length=50,
        blank=True,
        help_text='Nigerian region/state where this term is common'
    )
    
    # Quality and Validation
    is_validated = models.BooleanField(default=False)
    validation_score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text='Quality score for this training example'
    )
    
    # Usage Tracking
    usage_count = models.PositiveIntegerField(
        default=0,
        help_text='How many times this data point has been used in training'
    )
    status = models.CharField(max_length=20, choices=DATA_STATUS, default='raw')
    
    # User Information
    contributed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contributed_training_data'
    )
    
    # Additional Features
    features = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional features for ML (price range, context, etc.)'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'training_data'
        verbose_name = _('Training Data')
        verbose_name_plural = _('Training Data')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'status']),
            models.Index(fields=['source']),
            models.Index(fields=['language']),
            models.Index(fields=['is_validated']),
            models.Index(fields=['validation_score']),
        ]
    
    def __str__(self):
        return f"Training: '{self.text_input[:50]}' -> {self.category.name}"


class ModelPerformance(models.Model):
    """
    Track AI model performance metrics
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Model Information
    model_version = models.CharField(max_length=50)
    model_type = models.CharField(
        max_length=50,
        default='category_classifier',
        help_text='Type of model (category_classifier, fraud_detection, etc.)'
    )
    
    # Performance Metrics
    accuracy = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text='Overall accuracy score'
    )
    precision = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text='Precision score'
    )
    recall = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text='Recall score'
    )
    f1_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text='F1 score'
    )
    
    # Detailed Metrics
    confusion_matrix = models.JSONField(
        default=dict,
        help_text='Confusion matrix for detailed analysis'
    )
    class_metrics = models.JSONField(
        default=dict,
        help_text='Per-class precision, recall, f1-score'
    )
    
    # Training Information
    training_samples = models.PositiveIntegerField(
        help_text='Number of samples used for training'
    )
    validation_samples = models.PositiveIntegerField(
        help_text='Number of samples used for validation'
    )
    training_time_seconds = models.PositiveIntegerField(
        help_text='Time taken to train model in seconds'
    )
    
    # Deployment Information
    is_deployed = models.BooleanField(default=False)
    deployed_at = models.DateTimeField(null=True, blank=True)
    
    # Additional Metadata
    hyperparameters = models.JSONField(
        default=dict,
        help_text='Model hyperparameters used'
    )
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'model_performance'
        verbose_name = _('Model Performance')
        verbose_name_plural = _('Model Performance')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['model_version']),
            models.Index(fields=['model_type']),
            models.Index(fields=['accuracy']),
            models.Index(fields=['is_deployed']),
        ]
    
    def __str__(self):
        return f"{self.model_version} - Accuracy: {self.accuracy:.2%}"


