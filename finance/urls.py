from django.urls import path
from finance.views import *



urlpatterns = [

    path('', operation_list, name='operation_list' ),

    path(
        'operations/create/',
        operation_entry,
        name='operation_entry'
    ),

    path(
        'operations/revenu/create/',
        revenue_create,
        name='revenue_create'
    ),

    path(
        'operations/depense/create/',
        expense_create,
        name='expense_create'
    ),

    path(
        'operations/stock/create/',
        stock_create,
        name='stock_create'
    ),
    path('<int:pk>/',operation_detail,name='operation_detail' ),

    path('<int:pk>/correct/', operation_correct,name='operation_correct' ),

    path('categories/', category_list, name='category_list' ),

    path(
        'produits/',
        product_list,
        name='product_list'
    ),

    path(
        'produits/<int:pk>/',
        product_detail,
        name='product_detail'
    ),

    path(
        'produits/<int:pk>/update/',
        product_update,
        name='product_update'
    ),
    path(
    'produits/<int:produit_id>/production/ajouter/',
    production_create,
    name='production_create'
    ),
    
    path(
        'production/<int:pk>/modifier/',
        production_update,
        name='production_update'
    ),
]
