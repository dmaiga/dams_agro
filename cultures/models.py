import datetime
from decimal import Decimal

from django.conf import settings
from django.db import models


MOIS_FR = [
    "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre",
]


class Culture(models.Model):
    """Référentiel des cultures (maïs, arachide, niébé, oignon, ...)."""

    nom = models.CharField(max_length=100, unique=True)
    unite_rendement = models.CharField(
        max_length=10,
        default="t",
        help_text="Unité du rendement (t, kg, ...)"
    )
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ["nom"]

    def __str__(self):
        return self.nom


class FicheCulture(models.Model):
    """
    Historisation d'une culture : de la mise en terre à la récolte.

    Remplace le flux WhatsApp. Chaque fiche couvre une superficie donnée
    avec plusieurs lignes cultures (BesoinCulture), chacune avec ses intrants,
    son objectif de rendement et, après récolte, le rendement réellement obtenu.
    """

    technicien = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="fiches_culture"
    )
    date_debut = models.DateField(
        verbose_name="Date de démarrage",
        help_text="Date réelle de mise en culture (peut être renseignée après coup)"
    )
    superficie_ha = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.5"),
        verbose_name="Superficie (ha)"
    )
    note = models.TextField(blank=True, verbose_name="Observations")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_debut", "-created_at"]

    def __str__(self):
        return f"{self.saison_label} · {self.superficie_ha} ha · {self.technicien}"

    @property
    def saison_label(self):
        """Libellé lisible dérivé de date_debut : 'Juin 2026'."""
        return f"{MOIS_FR[self.date_debut.month - 1]} {self.date_debut.year}"


class BesoinCulture(models.Model):
    """
    Ligne d'une fiche : une culture avec ses intrants et ses rendements.

    Intrants (texte libre, format WhatsApp) + rendement objectif au démarrage,
    puis rendement réellement obtenu après récolte.
    """

    fiche = models.ForeignKey(
        FicheCulture,
        on_delete=models.CASCADE,
        related_name="besoins"
    )
    culture = models.ForeignKey(
        Culture,
        on_delete=models.PROTECT,
        related_name="besoins"
    )

    semence_quantite = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="Quantité semences"
    )
    semence_unite = models.CharField(
        max_length=10, default="kg"
    )
    engrais = models.TextField(blank=True, verbose_name="Engrais fournis")
    produit_phyto = models.TextField(
        blank=True,
        verbose_name="Produits phytosanitaires"
    )
    rendement_estime = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="Objectif de rendement"
    )

    rendement_reel = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="Rendement obtenu"
    )
    date_recolte = models.DateField(null=True, blank=True, verbose_name="Date de récolte")
    observation_direction = models.TextField(
        blank=True, verbose_name="Observation"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["culture__nom"]

    def __str__(self):
        return f"{self.culture} — {self.fiche}"

    @property
    def unite_rendement(self):
        return self.culture.unite_rendement

    @property
    def duree_cycle_jours(self):
        """Durée du cycle en jours (None si récolte non renseignée)."""
        if self.date_recolte is None:
            return None
        return (self.date_recolte - self.fiche.date_debut).days

    @property
    def ecart_rendement(self):
        """Rendement obtenu - objectif (None si non renseigné)."""
        if self.rendement_reel is None or self.rendement_estime is None:
            return None
        return self.rendement_reel - self.rendement_estime

    @property
    def ecart_pct(self):
        """Écart en % par rapport à l'objectif."""
        if self.rendement_reel is None or not self.rendement_estime:
            return None
        return (
            (self.rendement_reel - self.rendement_estime)
            / self.rendement_estime * Decimal("100")
        )
