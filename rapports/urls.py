from django.urls import path

from rapports import views

urlpatterns = [
    path(
        "",
        views.rapport_list,
        name="rapport_list"
    ),

    path(
        "nouveau/",
        views.rapport_create,
        name="rapport_create"
    ),

    path(
        "<int:pk>/",
        views.rapport_detail,
        name="rapport_detail"
    ),
]