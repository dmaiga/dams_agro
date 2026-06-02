from django.contrib import admin
from finance.models import Operation,Categorie, Produit,ProductionAgent


admin.site.register(Operation)
admin.site.register(Categorie)
admin.site.register(Produit)
admin.site.register(ProductionAgent)