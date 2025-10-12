# backend/apps/ai_categorization/urls.py
"""
URL configuration for AI categorization
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryPredictionViewSet, TrainingDataViewSet, ModelPerformanceViewSet

router = DefaultRouter()
router.register(r'predictions', CategoryPredictionViewSet)
router.register(r'training-data', TrainingDataViewSet)
router.register(r'model-performance', ModelPerformanceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
