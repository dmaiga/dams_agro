"""
URL configuration for dams_champs project.

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

from users.views import login_view
from finance.api_views import *
from rapports.api_views import *

urlpatterns = [
    path('admin/', admin.site.urls ),
    path('', login_view, name='login' ),
    path('users/', include('users.urls') ),
    path('finance/', include('finance.urls')),
    path('rapports/', include('rapports.urls')),

    path(
        'api/dashboard/',
        DashboardAPIView.as_view()
    ),

    path(
        'api/operations/',
        OperationListAPIView.as_view()
    ),
    path(
    'api/operations/<int:pk>/',
    OperationDetailAPIView.as_view() ),
    
    path(
        'api/categories/',
        CategorieListAPIView.as_view(),
        name='api_categories'
    ),
    path(
        'api/produits/',
        ProduitListAPIView.as_view()
    ),

    path(
        'api/produits/<int:pk>/',
        ProduitDetailAPIView.as_view()
    ),

    path(
        'api/agents/',
        AgentPerformanceAPIView.as_view()
    ),
    
    path(
        "api/rapports/",
        RapportListAPIView.as_view(),
        
    ),

    path(
        "api/rapports/<int:pk>/",
        RapportDetailAPIView.as_view(),
        ),
    path(
        "api/superviseurs/",
        SuperviseurListAPIView.as_view(),
        ),




]
