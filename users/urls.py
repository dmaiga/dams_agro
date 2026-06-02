from django.urls import path

from . import views


urlpatterns = [

    path(
        'login/',
        views.login_view,
        name='login'
    ),

    path(
        'logout/',
        views.logout_view,
        name='logout'
    ),
    path(
        'agents/',
        views.agent_list,
        name='agent_list'
    ),

    path(
        'agents/ajouter/',
        views.agent_create,
        name='agent_create'
    ),
    path(
    'agents/<int:pk>/modifier/',
    views.agent_update,
    name='agent_update'
),
]