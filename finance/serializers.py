from rest_framework import serializers

from finance.models import (
    Categorie,
    Operation,
    Produit,
    ProductionAgent
)

# =========================
# CATEGORIES
# =========================

class CategorieSerializer(serializers.ModelSerializer):
    """
    Sérialiseur de base pour le modèle Categorie.
    Convertit directement les champs du modèle en JSON.
    """
    class Meta:
        model = Categorie
        fields = ['id', 'nom', 'usage_type']

# =========================
# CORRECTIONS
# =========================

class CorrectionSerializer(serializers.ModelSerializer):
    """
    Sérialiseur simplifié pour afficher les détails des corrections (issues du modèle Operation).
    Utilisé généralement comme champ imbriqué dans d'autres sérialiseurs.
    """
    class Meta:
        model = Operation
        fields = ['id', 'amount', 'note', 'created_at']

# =========================
# OPERATIONS
# =========================
class OperationSerializer(serializers.ModelSerializer):
    categorie_nom = serializers.CharField(
        source='categorie.nom',
        read_only=True,
        default='-'
    )
    montant_initial = serializers.DecimalField(
        source='amount',
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    montant_reel = serializers.SerializerMethodField()
    montant_ecart = serializers.SerializerMethodField()
    is_corrected = serializers.SerializerMethodField()
    class Meta:
        model = Operation
        fields = [
            'id',

            'operation_type',

            'categorie',

            'categorie_nom',

            'label',

            'montant_initial',

            'montant_reel',

            'montant_ecart',

            'is_corrected',

            'operation_date',
        ]

    def get_is_corrected(self, obj):

        return obj.corrections.exists()

    def get_montant_ecart(self, obj):

        return obj.real_amount - obj.amount
    
    def get_montant_reel(self,obj):
        return obj.real_amount


class OperationDetailSerializer( serializers.ModelSerializer):

    categorie_nom = serializers.CharField(
        source='categorie.nom',
        read_only=True,
        default='Non catégorisé'
    )

    montant_initial = serializers.DecimalField(
        source='amount',
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    montant_reel = serializers.SerializerMethodField()

    montant_ecart = serializers.SerializerMethodField()

    is_corrected = serializers.SerializerMethodField()

    corrections = CorrectionSerializer(
        many=True,
        read_only=True
    )

    class Meta:

        model = Operation

        fields = [

            'id',

            'operation_type',

            'categorie',

            'categorie_nom',

            'label',

            'quantity',

            'unit_price',

            'montant_initial',

            'montant_reel',

            'montant_ecart',

            'is_corrected',

            'operation_date',

            'note',

            'created_at',

            'corrections',
        ]

    def get_is_corrected(self, obj):

        return obj.corrections.exists()

    def get_montant_ecart(self, obj):

        return obj.real_amount - obj.amount
    
    def get_montant_reel(self,obj):
        return obj.real_amount


# =========================
# AGENTS
# =========================

class ProductionAgentSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour les agents de production.
    Ajoute un champ calculé 'agent_nom' pour formater le nom complet de l'agent.
    """
    agent_nom = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductionAgent
        fields = ['id', 'agent', 'agent_nom', 'quantite_attachee', 'created_at']

    def get_agent_nom(self, obj):
        # Concaténation du prénom et nom de l'agent lié
        return f"{obj.agent.prenom} {obj.agent.nom}"

class AgentPerformanceSerializer(
    serializers.Serializer
):

    agent_id = serializers.IntegerField()

    agent_nom = serializers.CharField()

    nombre_interventions = (
        serializers.IntegerField()
    )

    quantite_totale = (
        serializers.IntegerField()
    )
    
# =========================
# PRODUITS
# =========================

class ProduitSerializer(serializers.ModelSerializer):
    """
    Sérialiseur principal pour les Produits.
    - Aggregue des données provenant d'un modèle lié (operation_stock).
    - Affiche des champs ReadOnlyField qui sont supposés être calculés au niveau du modèle.
    - Imbrique le ProductionAgentSerializer pour montrer les contributions par agent.
    """
    categorie_nom = serializers.CharField(source='operation_stock.categorie.nom', read_only=True)
    operation_date = serializers.DateField(source='operation_stock.operation_date', read_only=True)
    montant_achat = serializers.ReadOnlyField(source='operation_stock.real_amount')
    
    stock_restant = serializers.ReadOnlyField()
    quantite_attachee_totale = serializers.ReadOnlyField()
    
    production_est_equilibree = serializers.ReadOnlyField()
    quantite_theorique=serializers.SerializerMethodField()
    # Liste imbriquée des contributions des agents à ce produit
    contributions = ProductionAgentSerializer(many=True, read_only=True)

    class Meta:
        model = Produit
        fields = [
            'id', 'nom', 'categorie_nom', 'operation_date', 'montant_achat', 
            'quantite_initiale', 'quantite_vendue', 'quantite_offerte', 
            'quantite_perdue', 'stock_restant', 'quantite_attachee_totale', 
            'quantite_theorique', 'production_est_equilibree', 'note', 
            'created_at', 'contributions',
        ]
    def get_quantite_theorique(self,obj):
        return obj.quantite_vendue + obj.quantite_offerte