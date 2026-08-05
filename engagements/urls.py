from django.urls import path
from engagements.views import *


urlpatterns = [

    path('', engagement_list, name='engagement_list'),

    path('<int:pk>/', engagement_detail, name='engagement_detail'),

    path(
        '<int:pk>/rembourser/',
        remboursement_create,
        name='remboursement_create'
    ),
]
