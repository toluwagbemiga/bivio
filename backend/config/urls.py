"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Authentication
    path('api/auth/token/', obtain_auth_token, name='api_token_auth'),
    
    # App URLs
    path('api/users/', include('apps.users.urls')),
    path('api/inventory/', include('apps.inventory.urls')),
    path('api/transactions/', include('apps.transactions.urls')),
    path('api/loans/', include('apps.loans.urls')),
    path('api/savings/', include('apps.savings.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
    path('api/ai/', include('apps.ai_categorization.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
]
