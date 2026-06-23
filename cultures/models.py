import datetime
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Sum

from users.models import Agent


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
    date_recolte = models.DateField(null=True, blank=True, verbose_name="Date de clôture récolte")
    observation_direction = models.TextField(
        blank=True, verbose_name="Observation"
    )
    recolte_cloturee = models.BooleanField(
        default=False,
        verbose_name="Récolte clôturée",
        help_text="Marqué vrai quand le technicien signale la fin de la récolte."
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

    def total_passages(self):
        """Somme des quantités de tous les passages de récolte enregistrés."""
        total = self.passages_recolte.aggregate(total=Sum("quantite"))["total"]
        return total or Decimal("0")


class PassageRecolte(models.Model):
    """Un passage de récolte sur un besoin : date et quantité récoltée ce jour."""

    besoin = models.ForeignKey(
        BesoinCulture,
        on_delete=models.CASCADE,
        related_name="passages_recolte"
    )
    date_passage = models.DateField(verbose_name="Date du passage")
    quantite = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name="Quantité récoltée"
    )
    observation = models.CharField(max_length=255, blank=True, verbose_name="Observation")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date_passage"]

    def __str__(self):
        return f"{self.besoin.culture} — {self.date_passage} — {self.quantite} {self.besoin.unite_rendement}"


class RapportCulture(models.Model):
    """Bilan de fin de cycle pour un besoin clôturé : activités, problèmes, participants."""

    besoin = models.OneToOneField(
        BesoinCulture,
        on_delete=models.CASCADE,
        related_name="rapport_culture",
        verbose_name="Culture concernée"
    )
    bilan_activites = models.TextField(blank=True, verbose_name="Bilan des activités")
    problemes = models.TextField(blank=True, verbose_name="Difficultés rencontrées")
    solutions = models.TextField(blank=True, verbose_name="Solutions appliquées")
    resultats = models.TextField(blank=True, verbose_name="Résultats obtenus")
    perspectives = models.TextField(blank=True, verbose_name="Perspectives")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rapport — {self.besoin.culture} ({self.besoin.fiche.saison_label})"


class ParticipationCulture(models.Model):
    """Évaluation d'un agent sur un cycle de culture clôturé."""

    class NiveauImplication(models.IntegerChoices):
        FAIBLE     = 1, "1 - Faible"
        MOYENNE    = 2, "2 - Moyenne"
        BONNE      = 3, "3 - Bonne"
        TRES_BONNE = 4, "4 - Très bonne"
        EXCELLENTE = 5, "5 - Excellente"

    class NiveauMaitrise(models.IntegerChoices):
        DEBUTANT       = 1, "1 - Débutant"
        APPRENTISSAGE  = 2, "2 - En apprentissage"
        AUTONOME       = 3, "3 - Autonome"
        BONNE_MAITRISE = 4, "4 - Bonne maîtrise"
        EXPERT         = 5, "5 - Expert"

    rapport = models.ForeignKey(
        RapportCulture,
        on_delete=models.CASCADE,
        related_name="participations"
    )
    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name="participations_culture"
    )
    implication = models.PositiveSmallIntegerField(
        choices=NiveauImplication.choices,
        default=NiveauImplication.BONNE,
        verbose_name="Niveau d'implication"
    )
    maitrise = models.PositiveSmallIntegerField(
        choices=NiveauMaitrise.choices,
        default=NiveauMaitrise.AUTONOME,
        verbose_name="Maîtrise de la culture"
    )
    observation = models.CharField(max_length=255, blank=True, verbose_name="Observation")

    class Meta:
        unique_together = ("rapport", "agent")

    def __str__(self):
        return f"{self.agent} — {self.rapport.besoin.culture}"
