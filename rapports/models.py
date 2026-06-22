from django.conf import settings
from django.db import models

from users.models import Agent


class RapportJournalier(models.Model):

    superviseur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rapports"
    )

    date = models.DateField()

    activite_realisee = models.TextField()

    probleme = models.TextField(
        blank=True
    )

    solution = models.TextField(
        blank=True
    )
    resultat_obtenu = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"Rapport du {self.date}"
    

class ParticipationAgent(models.Model):

    class NiveauImplication(models.IntegerChoices):
        FAIBLE = 1, "1 - Faible"
        MOYENNE = 2, "2 - Moyenne"
        BONNE = 3, "3 - Bonne"
        TRES_BONNE = 4, "4 - Très bonne"
        EXCELLENTE = 5, "5 - Excellente"

    class NiveauMaitrise(models.IntegerChoices):
        DEBUTANT = 1, "1 - Débutant"
        APPRENTISSAGE = 2, "2 - En apprentissage"
        AUTONOME = 3, "3 - Autonome"
        BONNE_MAITRISE = 4, "4 - Bonne maîtrise"
        EXPERT = 5, "5 - Expert"

    rapport = models.ForeignKey(
        RapportJournalier,
        on_delete=models.CASCADE,
        related_name="participants"
    )

    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name="participations"
    )

    implication = models.PositiveSmallIntegerField(
        choices=NiveauImplication.choices,
        default=NiveauImplication.BONNE
    )

    maitrise = models.PositiveSmallIntegerField(
        choices=NiveauMaitrise.choices,
        default=NiveauMaitrise.AUTONOME
    )

    observation = models.CharField(
        max_length=255,
        blank=True
    )

    class Meta:
        unique_together = (
            "rapport",
            "agent"
        )

    def __str__(self):
        return f"{self.agent} - {self.rapport}"