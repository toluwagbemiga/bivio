# backend/apps/users/urls.py
"""
URL configuration for user management
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, BusinessProfileViewSet, GuarantorViewSet

router = DefaultRouter()
# Register the UserViewSet at the empty prefix because this urls.py is already
# included under the 'api/users/' path in the project URLs. That makes the
# registration endpoint available at /api/users/register/ instead of
# /api/users/users/register/.
router.register(r'', UserViewSet, basename='users')
router.register(r'business-profiles', BusinessProfileViewSet)
router.register(r'guarantors', GuarantorViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
