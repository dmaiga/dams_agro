from decimal import Decimal

from rest_framework import serializers

from cultures.models import (
    Culture, FicheCulture, BesoinCulture, PassageRecolte,
    RapportCulture, ParticipationCulture,
)


class CultureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Culture
        fields = ["id", "nom", "unite_rendement", "actif"]


class PassageRecolteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassageRecolte
        fields = ["id", "date_passage", "quantite", "observation", "created_at"]


class ParticipationCultureSerializer(serializers.ModelSerializer):
    agent_prenom        = serializers.CharField(source="agent.prenom", read_only=True)
    agent_nom           = serializers.CharField(source="agent.nom", read_only=True)
    implication_display = serializers.CharField(source="get_implication_display", read_only=True)
    maitrise_display    = serializers.CharField(source="get_maitrise_display", read_only=True)

    class Meta:
        model = ParticipationCulture
        fields = [
            "id", "agent", "agent_prenom", "agent_nom",
            "implication", "implication_display",
            "maitrise", "maitrise_display",
            "observation",
        ]


class RapportCultureSerializer(serializers.ModelSerializer):
    participations = ParticipationCultureSerializer(many=True, read_only=True)

    class Meta:
        model = RapportCulture
        fields = [
            "id",
            "bilan_activites",
            "problemes",
            "solutions",
            "resultats",
            "perspectives",
            "participations",
            "created_at",
        ]


class RapportCultureListSerializer(serializers.ModelSerializer):
    """Sérialiseur pour l'endpoint liste direction — inclut le contexte besoin/culture."""
    participations   = ParticipationCultureSerializer(many=True, read_only=True)
    culture_nom      = serializers.CharField(source="besoin.culture.nom", read_only=True)
    unite_rendement  = serializers.CharField(source="besoin.culture.unite_rendement", read_only=True)
    rendement_reel   = serializers.DecimalField(
        source="besoin.rendement_reel", max_digits=10, decimal_places=2, read_only=True
    )
    saison_label     = serializers.CharField(source="besoin.fiche.saison_label", read_only=True)
    technicien_id    = serializers.IntegerField(source="besoin.fiche.technicien_id", read_only=True)

    class Meta:
        model = RapportCulture
        fields = [
            "id",
            "culture_nom",
            "unite_rendement",
            "rendement_reel",
            "saison_label",
            "technicien_id",
            "bilan_activites",
            "problemes",
            "solutions",
            "resultats",
            "perspectives",
            "participations",
            "created_at",
        ]


class BesoinCultureSerializer(serializers.ModelSerializer):
    culture_nom         = serializers.CharField(source="culture.nom", read_only=True)
    unite_rendement     = serializers.CharField(source="culture.unite_rendement", read_only=True)
    ecart_rendement     = serializers.SerializerMethodField()
    ecart_pct           = serializers.SerializerMethodField()
    duree_cycle_jours   = serializers.SerializerMethodField()
    observation         = serializers.CharField(source="observation_direction", read_only=True)
    passages_recolte    = PassageRecolteSerializer(many=True, read_only=True)
    rapport_culture     = RapportCultureSerializer(read_only=True)

    class Meta:
        model = BesoinCulture
        fields = [
            "id",
            "culture",
            "culture_nom",
            "semence_quantite",
            "semence_unite",
            "engrais",
            "produit_phyto",
            "rendement_estime",
            "rendement_reel",
            "recolte_cloturee",
            "date_recolte",
            "observation",
            "ecart_rendement",
            "ecart_pct",
            "duree_cycle_jours",
            "unite_rendement",
            "passages_recolte",
            "rapport_culture",
        ]

    def get_ecart_rendement(self, obj):
        return obj.ecart_rendement

    def get_ecart_pct(self, obj):
        v = obj.ecart_pct
        if v is None:
            return None
        return round(v, 1)

    def get_duree_cycle_jours(self, obj):
        return obj.duree_cycle_jours


class FicheCultureSerializer(serializers.ModelSerializer):
    besoins      = BesoinCultureSerializer(many=True, read_only=True)
    nb_cultures  = serializers.SerializerMethodField()
    saison_label = serializers.CharField(read_only=True)

    class Meta:
        model = FicheCulture
        fields = [
            "id",
            "technicien",
            "date_debut",
            "saison_label",
            "superficie_ha",
            "note",
            "created_at",
            "besoins",
            "nb_cultures",
        ]

    def get_nb_cultures(self, obj):
        return obj.besoins.count()


class BaseConnaissancesSerializer(serializers.Serializer):
    culture      = serializers.CharField()
    unite        = serializers.CharField()
    nb_campagnes = serializers.IntegerField()
    moy_estime   = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    moy_reel     = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    ecart_pct    = serializers.DecimalField(max_digits=6, decimal_places=1, allow_null=True)
    agents       = serializers.ListField(child=serializers.DictField(), default=list)
