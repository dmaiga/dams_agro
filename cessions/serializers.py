from rest_framework import serializers

from cessions.models import Cession, ProduitAgricole


class ProduitAgricoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProduitAgricole
        fields = ['id', 'nom']


class CessionSerializer(serializers.ModelSerializer):
    """
    Cession consommée en lecture par `dams` / DAMS Distribution.
    Aucune Operation, aucun solde : c'est une trace transactionnelle
    historique isolée de `finance`. Voir cessions/APP_CESSIONS.md.
    """
    produit_nom = serializers.CharField(
        source='produit.nom',
        read_only=True
    )
    statut_display = serializers.CharField(
        source='get_statut_display',
        read_only=True
    )

    class Meta:
        model = Cession
        fields = [
            'id',
            'idempotency_key',
            'produit',
            'produit_nom',
            'quantite',
            'prix_cession',
            'date_cession',
            'statut',
            'statut_display',
            'transmise_le',
            'note',
            'created_at',
        ]
