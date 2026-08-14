from django.urls import path
from cessions.views import *


urlpatterns = [

    path('', cession_list, name='cession_list'),

    path('creer/', cession_create, name='cession_create'),
]
