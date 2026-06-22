from django.contrib import admin
from finance.models import (
    Operation,
    Categorie,
    Produit,
    ProductionAgent,
    ParametreFinancier,
)


admin.site.register(Operation)
admin.site.register(Categorie)
admin.site.register(Produit)
admin.site.register(ProductionAgent)


@admin.register(ParametreFinancier)
class ParametreFinancierAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'solde_ajuster', 'updated_at')
    readonly_fields = ('updated_at',)

    def has_add_permission(self, request):
        # Singleton : on n'ajoute pas, on édite l'unique instance.
        return not ParametreFinancier.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
