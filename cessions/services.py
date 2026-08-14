from django.conf import settings
from django.utils import timezone

import requests

from cessions.models import Cession


def construire_payload(cession):
    """
    Construit le payload conceptuel envoyé à DAMS Distribution pour une
    cession. Séparé de `transmettre_cession` pour rester testable sans
    réseau — c'est aussi le point unique à ajuster le jour où DAMS
    Distribution publie le contrat exact de son API (noms de champs,
    format des montants/dates, etc.).
    """
    return {
        'idempotency_key': str(cession.idempotency_key),
        'produit': cession.produit.nom,
        'quantite': str(cession.quantite),
        'prix_cession': str(cession.prix_cession),
        'date_cession': cession.date_cession.isoformat(),
    }


def transmettre_cession(cession):
    """
    Transmet une Cession à DAMS Distribution par POST HTTP. Point de
    branchement isolé : tant que `DAMS_DISTRIBUTION_CESSIONS_URL` n'est
    pas configurée (contrat API pas encore défini côté DAMS Distribution),
    la transmission échoue proprement.

    La création locale de la Cession est toujours acquise avant cet appel
    (voir cessions/views.py) — une panne réseau ou une absence de
    configuration ne supprime ni n'invalide jamais la trace historique
    locale, elle ne fait que marquer `statut='echec'`.

    Retourne True si la transmission a réussi, False sinon.
    """
    url = settings.DAMS_DISTRIBUTION_CESSIONS_URL

    if not url:
        cession.statut = Cession.STATUT_ECHEC
        cession.derniere_erreur = (
            "DAMS_DISTRIBUTION_CESSIONS_URL non configurée."
        )
        cession.save(update_fields=['statut', 'derniere_erreur'])
        return False

    payload = construire_payload(cession)

    headers = {
        'X-Api-Key': settings.DAMS_DISTRIBUTION_OUTBOUND_API_KEY,
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()

    except requests.RequestException as exc:
        cession.statut = Cession.STATUT_ECHEC
        cession.derniere_erreur = str(exc)
        cession.save(update_fields=['statut', 'derniere_erreur'])
        return False

    cession.statut = Cession.STATUT_TRANSMISE
    cession.transmise_le = timezone.now()
    cession.derniere_erreur = ''
    cession.save(update_fields=['statut', 'transmise_le', 'derniere_erreur'])
    return True
