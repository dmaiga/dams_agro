from decimal import Decimal

from django.db import models

from users.models import Agent

class Categorie(models.Model):

    TYPE_CHOICES = (
        ('depense', 'Dépense'),
        ('revenu', 'Revenu'),
        ('stock', 'Stock'),
        ('both', 'Les deux'),
    )

    nom = models.CharField(
        max_length=100,
        unique=True
    )

    usage_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='both'
    )

    description = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'

    def __str__(self):
        return self.nom
    
class ParametreFinancier(models.Model):
    """
    Paramètres financiers globaux (modèle singleton).

    Permet au responsable financier / superuser d'ajuster manuellement
    le solde via l'admin. Quand `solde_ajuster` est renseigné, c'est cette
    valeur qui est exposée au lieu du calcul naïf (revenus - dépenses).
    """

    solde_ajuster = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name="Ajustement du solde",
        help_text=(
            "Montant (+/-) ajouté au solde calculé. "
            "Solde exposé = revenus - dépenses + ajustement."
        )
    )

    note = models.TextField(
        blank=True,
        help_text="Raison / justification de l'ajustement."
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Paramètre financier"
        verbose_name_plural = "Paramètres financiers"

    def __str__(self):
        return "Paramètres financiers"

    def save(self, *args, **kwargs):
        # Force le singleton : toujours pk=1
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Operation(models.Model):
    TYPE_CHOICES = (
        ('', 'Sélectionner un type'),
        ('revenu', 'Revenu'),
        ('depense', 'Dépense'),
        ('stock', 'Stock'),

    )

    operation_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES
    )

    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='operations'
    )

    label = models.CharField(
        max_length=255
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    operation_date = models.DateField()

    note = models.TextField(
        blank=True
    )

    corrects_operation = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='corrections'
    )
    is_manual_amount = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = [
            '-operation_date',
            '-created_at'
        ]

        indexes = [

            models.Index(
                fields=['operation_type']
            ),

            models.Index(
                fields=['operation_date']
            ),

            models.Index(
                fields=['categorie']
            ),

            models.Index(
                fields=[
                    'operation_type',
                    'operation_date'
                ]
            ),
        ]

    from decimal import Decimal


    def save(self, *args, **kwargs):

        if not self.is_manual_amount:

            quantity = self.quantity or Decimal('0')

            unit_price = self.unit_price or Decimal('0')

            self.amount = quantity * unit_price
        

        super().save(*args, **kwargs)

    def __str__(self):
        return self.label

    @property
    def is_correction(self):
        return self.corrects_operation is not None

    @property
    def real_amount(self):

        latest_correction = (
            self.corrections
            .order_by('-created_at')
            .first()
        )

        if latest_correction:
            return latest_correction.amount

        return self.amount


class Produit(models.Model):
    nom = models.CharField(
        max_length=150
    )
    operation_stock = models.OneToOneField(
        Operation,
        on_delete=models.CASCADE,
        related_name='produit'
    )
    quantite_initiale = models.PositiveIntegerField(
        default=0
    )
    quantite_vendue = models.PositiveIntegerField(
        default=0
    )
    quantite_perdue = models.PositiveIntegerField(
        default=0
    )
    quantite_offerte = models.PositiveIntegerField(
        default=0
    )
    note = models.TextField(
        blank=True
    )    
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    @property
    def stock_restant(self):

        return (
            self.quantite_initiale
            - self.quantite_vendue
            - self.quantite_perdue
        )

    @property
    def quantite_attachee_totale(self):
    
        return sum(
            contribution.quantite_attachee
            for contribution in self.contributions.all()
        )
    
    @property
    def production_est_equilibree(self):
    
        return (
            self.quantite_attachee_totale
            ==
            self.quantite_theorique
        )

    @property
    def quantite_attendue_agents(self):

        return ( 
              self.quantite_vendue
            + self.quantite_offerte    
        )

    def __str__(self):

        return self.nom
    
class ProductionAgent(models.Model):
    produit = models.ForeignKey(
        Produit,
        on_delete=models.CASCADE,
        related_name='contributions'
    )
    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name='productions'
    )
    quantite_attachee = models.PositiveIntegerField()
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.agent} - "
            f"{self.quantite_attachee}"
        )