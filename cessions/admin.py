from django.contrib import admin

from cessions.models import ProduitAgricole, Cession


@admin.register(ProduitAgricole)
class ProduitAgricoleAdmin(admin.ModelAdmin):
    list_display = ('nom', 'created_at')
    search_fields = ('nom',)


@admin.register(Cession)
class CessionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'produit', 'quantite', 'prix_cession', 'date_cession')
    list_filter = ('produit',)
    readonly_fields = ('created_at',)
