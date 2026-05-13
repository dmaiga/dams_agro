from django.urls import path
from finance.views import *


urlpatterns = [

    path('', operation_list, name='operation_list' ),

    path('create/', operation_create, name='operation_create'),

    path('<int:pk>/',operation_detail,name='operation_detail' ),

    path('<int:pk>/correct/', operation_correct,name='operation_correct' ),

    path('categories/', category_list, name='category_list' ),
]