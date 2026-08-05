from decimal import Decimal

from django.db import models

from users.models import User


class EngagementFinancier(models.Model):
    """
    Engagement financier pris par un superviseur DAMS Distribution
    au profit du champ (avance de trésorerie ou dépense payée pour
    son compte). Le superviseur n'a pas de compte dans dams_agro :
    il est identifié par une référence libre transmise par l'API.
    """

    NATURE_CHOICES = (
        ('avance_tresorerie', 'Avance de trésorerie'),
        ('depense_compte', 'Dépense pour le compte du champ'),
    )

    nature = models.CharField(
        max_length=30,
        choices=NATURE_CHOICES
    )

    reference_superviseur = models.CharField(
        max_length=150,
        help_text="Identifiant ou nom du superviseur côté DAMS Distribution."
    )

    reference_externe = models.CharField(
        max_length=100,
        blank=True,
        help_text="Référence de l'engagement côté DAMS Distribution."
    )

    technicien = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='engagements_recus',
        help_text="Technicien dams_agro concerné, si connu."
    )

    montant_initial = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    label = models.CharField(
        max_length=255
    )

    date_engagement = models.DateField()

    note = models.TextField(
        blank=True
    )

    operation_generee = models.ForeignKey(
        'finance.Operation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='engagement_origine',
        help_text="Operation revenu créée automatiquement (avance de trésorerie uniquement)."
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Engagement financier'
        verbose_name_plural = 'Engagements financiers'
        ordering = ['-date_engagement', '-created_at']
        indexes = [
            models.Index(fields=['nature']),
            models.Index(fields=['date_engagement']),
        ]

    def __str__(self):
        return f"{self.get_nature_display()} - {self.label}"

    @property
    def montant_rembourse(self):
        # `.all()` (et non `.aggregate()`) pour profiter du cache de
        # prefetch_related('remboursements') — .aggregate() déclenche
        # toujours une requête SQL, même si les remboursements sont déjà
        # préchargés, ce qui provoquerait un N+1 sur les listes.
        return sum(
            (remboursement.montant for remboursement in self.remboursements.all()),
            Decimal('0')
        )

    @property
    def reste_a_rembourser(self):
        return self.montant_initial - self.montant_rembourse

    @property
    def etat(self):
        if self.montant_rembourse <= 0:
            return 'ouvert'
        if self.reste_a_rembourser <= 0:
            return 'solde'
        return 'partiel'


class RemboursementEngagement(models.Model):
    """
    Remboursement (partiel ou total) d'un EngagementFinancier.
    Un même engagement peut recevoir plusieurs remboursements.
    """

    engagement = models.ForeignKey(
        EngagementFinancier,
        on_delete=models.CASCADE,
        related_name='remboursements'
    )

    montant = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    date_remboursement = models.DateField()

    reference_externe = models.CharField(
        max_length=100,
        blank=True,
        help_text="Référence du remboursement côté DAMS Distribution."
    )

    note = models.TextField(
        blank=True
    )

    operation_generee = models.ForeignKey(
        'finance.Operation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='remboursement_origine',
        help_text="Operation dépense créée automatiquement."
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Remboursement d\'engagement'
        verbose_name_plural = 'Remboursements d\'engagements'
        ordering = ['-date_remboursement', '-created_at']

    def __str__(self):
        return f"Remboursement {self.montant} - {self.engagement}"

