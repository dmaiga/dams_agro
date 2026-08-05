from decimal import Decimal

from django.core.exceptions import ValidationError
from django.utils import timezone

from finance.models import Categorie, Operation
from engagements.models import EngagementFinancier, RemboursementEngagement

CATEGORIE_AVANCE_NOM = "Avance superviseur (engagement)"
CATEGORIE_REMBOURSEMENT_NOM = "Remboursement engagement"


def creer_engagement(
    *,
    nature,
    montant_initial,
    label,
    reference_superviseur,
    reference_externe='',
    technicien=None,
    date_engagement=None,
    note='',
):
    """
    Crée un EngagementFinancier. Si la nature est 'avance_tresorerie',
    génère en plus une Operation revenu pour matérialiser l'entrée de
    cash dans les fonds disponibles du champ. Une 'depense_compte' ne
    génère aucune Operation : le champ ne reçoit jamais cet argent.
    """
    date_engagement = date_engagement or timezone.now().date()

    engagement = EngagementFinancier.objects.create(
        nature=nature,
        montant_initial=montant_initial,
        label=label,
        reference_superviseur=reference_superviseur,
        reference_externe=reference_externe,
        technicien=technicien,
        date_engagement=date_engagement,
        note=note,
    )

    if nature == 'avance_tresorerie':
        categorie, _ = Categorie.objects.get_or_create(
            nom=CATEGORIE_AVANCE_NOM,
            defaults={'usage_type': 'revenu'}
        )
        operation = Operation.objects.create(
            operation_type='revenu',
            categorie=categorie,
            label=f"Avance de trésorerie — {reference_superviseur}",
            amount=montant_initial,
            is_manual_amount=True,
            operation_date=date_engagement,
            note=f"Généré automatiquement depuis l'engagement #{engagement.pk}.",
        )
        engagement.operation_generee = operation
        engagement.save(update_fields=['operation_generee'])

    return engagement


def enregistrer_remboursement(
    *,
    engagement,
    montant,
    date_remboursement=None,
    reference_externe='',
    note='',
):
    """
    Enregistre un remboursement (partiel ou total) d'un engagement.
    Crée systématiquement une Operation dépense : que l'engagement soit
    une avance ou une dépense pour compte, le remboursement est toujours
    une sortie de cash réelle du champ vers le superviseur.
    """
    montant = Decimal(montant)

    if montant <= 0:
        raise ValidationError("Le montant du remboursement doit être positif.")

    if montant > engagement.reste_a_rembourser:
        raise ValidationError(
            "Le montant du remboursement dépasse le reste à rembourser "
            f"({engagement.reste_a_rembourser})."
        )

    date_remboursement = date_remboursement or timezone.now().date()

    categorie, _ = Categorie.objects.get_or_create(
        nom=CATEGORIE_REMBOURSEMENT_NOM,
        defaults={'usage_type': 'depense'}
    )
    operation = Operation.objects.create(
        operation_type='depense',
        categorie=categorie,
        label=f"Remboursement — {engagement.get_nature_display()} #{engagement.pk}",
        amount=montant,
        is_manual_amount=True,
        operation_date=date_remboursement,
        note=note,
    )

    return RemboursementEngagement.objects.create(
        engagement=engagement,
        montant=montant,
        date_remboursement=date_remboursement,
        reference_externe=reference_externe,
        note=note,
        operation_generee=operation,
    )
