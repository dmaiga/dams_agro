from django.contrib import admin

from cultures.models import Culture, FicheCulture, BesoinCulture


@admin.register(Culture)
class CultureAdmin(admin.ModelAdmin):
    list_display = ("nom", "unite_rendement", "actif")
    list_editable = ("unite_rendement", "actif")


class BesoinCultureInline(admin.TabularInline):
    model = BesoinCulture
    fk_name = "fiche"
    extra = 0


@admin.register(FicheCulture)
class FicheCultureAdmin(admin.ModelAdmin):
    list_display = ("saison_label", "technicien", "superficie_ha", "date_debut")
    list_filter = ("date_debut",)
    inlines = [BesoinCultureInline]


@admin.register(BesoinCulture)
class BesoinCultureAdmin(admin.ModelAdmin):
    list_display = ("culture", "fiche", "rendement_estime", "rendement_reel", "date_recolte")
    list_filter = ("culture",)
