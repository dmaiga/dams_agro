from django.contrib import admin

from cultures.models import (
    Culture, FicheCulture, BesoinCulture, PassageRecolte,
    RapportCulture, ParticipationCulture,
)


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


class PassageRecolteInline(admin.TabularInline):
    model = PassageRecolte
    extra = 0
    fields = ("date_passage", "quantite", "observation")
    readonly_fields = ("created_at",)


@admin.register(BesoinCulture)
class BesoinCultureAdmin(admin.ModelAdmin):
    list_display = ("culture", "fiche", "rendement_estime", "rendement_reel", "recolte_cloturee", "date_recolte")
    list_filter = ("culture", "recolte_cloturee")
    inlines = [PassageRecolteInline]


class ParticipationCultureInline(admin.TabularInline):
    model = ParticipationCulture
    extra = 0
    fields = ("agent", "implication", "maitrise", "observation")


@admin.register(RapportCulture)
class RapportCultureAdmin(admin.ModelAdmin):
    list_display = ("besoin", "created_at")
    list_filter = ("besoin__culture",)
    inlines = [ParticipationCultureInline]
