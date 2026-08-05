from rest_framework import serializers

from engagements.models import EngagementFinancier, RemboursementEngagement
from engagements.services import creer_engagement, enregistrer_remboursement

# =========================
# REMBOURSEMENTS
# =========================

class RemboursementEngagementSerializer(serializers.ModelSerializer):
    """
    Sérialiseur des remboursements d'un engagement.
    En lecture : détail complet. En écriture : montant, date, référence, note.
    """
    date_remboursement = serializers.DateField(required=False)

    class Meta:
        model = RemboursementEngagement
        fields = [
            'id',
            'montant',
            'date_remboursement',
            'reference_externe',
            'note',
            'operation_generee',
            'created_at',
        ]
        read_only_fields = ['id', 'operation_generee', 'created_at']

    def create(self, validated_data):
        engagement = self.context['engagement']
        return enregistrer_remboursement(
            engagement=engagement,
            montant=validated_data['montant'],
            date_remboursement=validated_data.get('date_remboursement'),
            reference_externe=validated_data.get('reference_externe', ''),
            note=validated_data.get('note', ''),
        )


# =========================
# ENGAGEMENTS
# =========================

class EngagementFinancierSerializer(serializers.ModelSerializer):
    nature_display = serializers.CharField(
        source='get_nature_display',
        read_only=True
    )
    technicien_nom = serializers.SerializerMethodField()
    date_engagement = serializers.DateField(required=False)

    # DecimalField (pas SerializerMethodField) pour rendre ces montants en
    # string au même format que montant_initial ("50000.00"), plutôt qu'en
    # float — un client ne doit pas voir deux types différents pour des
    # montants sur le même objet.
    montant_rembourse = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    reste_a_rembourser = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    etat = serializers.CharField(read_only=True)

    class Meta:
        model = EngagementFinancier
        fields = [
            'id',
            'nature',
            'nature_display',
            'reference_superviseur',
            'reference_externe',
            'technicien',
            'technicien_nom',
            'montant_initial',
            'montant_rembourse',
            'reste_a_rembourser',
            'etat',
            'label',
            'date_engagement',
            'note',
            'operation_generee',
            'created_at',
        ]
        read_only_fields = ['id', 'operation_generee', 'created_at']

    def get_technicien_nom(self, obj):
        return obj.technicien.full_name if obj.technicien else None

    def create(self, validated_data):
        return creer_engagement(**validated_data)


class EngagementFinancierDetailSerializer(EngagementFinancierSerializer):
    remboursements = RemboursementEngagementSerializer(
        many=True,
        read_only=True
    )

    class Meta(EngagementFinancierSerializer.Meta):
        fields = EngagementFinancierSerializer.Meta.fields + ['remboursements']
