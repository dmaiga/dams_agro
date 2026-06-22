from django.urls import path

from cultures import views

urlpatterns = [
    path("", views.fiche_list, name="fiche_list"),
    path("nouvelle/", views.fiche_create, name="fiche_create"),
    path("types/", views.culture_list_create, name="culture_list_create"),
    path("connaissances/", views.base_connaissances, name="base_connaissances"),
    path("<int:pk>/", views.fiche_detail, name="fiche_detail"),
    path("besoin/<int:pk>/rendement/", views.saisir_rendement, name="saisir_rendement"),
]
