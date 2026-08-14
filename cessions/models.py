import uuid

from django.db import models


class ProduitAgricole(models.Model):
    """
    Référentiel simple des produits agricoles pouvant être cédés à DAMS
    Distribution. Distinct de `finance.Produit` (qui naît d'une opération
    de stock) : pas de FK vers `finance`, pas de lien avec `culture` — ce
    n'est qu'un référentiel nom → cession, volontairement minimal.
    """

    nom = models.CharField(
        max_length=150,
        unique=True
    )

    note = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Produit agricole'
        verbose_name_plural = 'Produits agricoles'
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Cession(models.Model):
    """
    Cession d'un produit agricole à DAMS Distribution. Trace
    transactionnelle historique uniquement : ne crée pas de
    `finance.Operation`, n'impacte pas le solde, ne génère aucune dette
    ni mécanisme de recouvrement (voir CLAUDE.md — invariants finance).
    """

    STATUT_LOCALE = 'locale'
    STATUT_TRANSMISE = 'transmise'
    STATUT_ECHEC = 'echec'

    STATUT_CHOICES = (
        (STATUT_LOCALE, 'Créée localement'),
        (STATUT_TRANSMISE, 'Transmise à DAMS Distribution'),
        (STATUT_ECHEC, 'Échec de transmission'),
    )

    produit = models.ForeignKey(
        ProduitAgricole,
        on_delete=models.PROTECT,
        related_name='cessions'
    )

    quantite = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    prix_cession = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Prix unitaire de cession (par unité de quantité, pas un montant total)."
    )

    date_cession = models.DateField()

    note = models.TextField(
        blank=True
    )

    # Identifiant stable et indépendant de la clé primaire Django, généré
    # à la création. Sert de clé d'idempotence lors de la transmission à
    # DAMS Distribution : renvoyer la même cession plusieurs fois ne doit
    # jamais faire créer plusieurs LotEntrepot côté DAMS.
    idempotency_key = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    # Statut de la transmission à DAMS Distribution. Volontairement minimal
    # (pas de file d'attente ni de retry automatique) : la création locale
    # de la cession reste toujours acquise, indépendamment du succès de
    # sa transmission — voir cessions/services.py.
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default=STATUT_LOCALE
    )

    transmise_le = models.DateTimeField(
        null=True,
        blank=True
    )

    derniere_erreur = models.TextField(
        blank=True,
        help_text="Message de la dernière erreur de transmission, le cas échéant."
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Cession'
        verbose_name_plural = 'Cessions'
        ordering = ['-date_cession', '-created_at']
        indexes = [
            models.Index(fields=['date_cession']),
            models.Index(fields=['produit']),
        ]

    def __str__(self):
        return f"Cession {self.produit} - {self.quantite}"
