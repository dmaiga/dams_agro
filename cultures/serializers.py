from decimal import Decimal

from rest_framework import serializers

from cultures.models import Culture, FicheCulture, BesoinCulture


class CultureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Culture
        fields = ["id", "nom", "unite_rendement", "actif"]


class BesoinCultureSerializer(serializers.ModelSerializer):
    culture_nom = serializers.CharField(source="culture.nom", read_only=True)
    unite_rendement = serializers.CharField(source="culture.unite_rendement", read_only=True)
    ecart_rendement = serializers.SerializerMethodField()
    ecart_pct = serializers.SerializerMethodField()
    duree_cycle_jours = serializers.SerializerMethodField()
    observation = serializers.CharField(source="observation_direction", read_only=True)

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
            "date_recolte",
            "observation",
            "ecart_rendement",
            "ecart_pct",
            "duree_cycle_jours",
            "unite_rendement",
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
    besoins = BesoinCultureSerializer(many=True, read_only=True)
    nb_cultures = serializers.SerializerMethodField()
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
    culture = serializers.CharField()
    unite = serializers.CharField()
    nb_campagnes = serializers.IntegerField()
    moy_estime = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    moy_reel = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    ecart_pct = serializers.DecimalField(max_digits=6, decimal_places=1, allow_null=True)
