import hmac

from django.conf import settings
from rest_framework.permissions import BasePermission


class HasDamsDistributionAPIKey(BasePermission):
    """
    Autorise uniquement les requêtes portant la clé API DAMS Distribution
    dans l'en-tête 'X-Api-Key'. Ce module est le seul du repo consommé en
    écriture par une application externe — les autres endpoints /api/ sont
    en lecture seule pour `dams` (voir rules/ARCHITECTURE.md).
    """

    def has_permission(self, request, view):
        expected = getattr(settings, 'DAMS_DISTRIBUTION_API_KEY', '')
        provided = request.headers.get('X-Api-Key', '')

        if not expected or not provided:
            return False

        return hmac.compare_digest(provided, expected)
