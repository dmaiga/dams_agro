from decimal import Decimal

from django.db import models



class Categorie(models.Model):

    nom = models.CharField(
        max_length=100,
        unique=True
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
    

class Operation(models.Model):

    TYPE_CHOICES = (
        ('', 'Sélectionner un type'),
        ('revenu', 'Revenu'),
        ('depense', 'Dépense'),
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
