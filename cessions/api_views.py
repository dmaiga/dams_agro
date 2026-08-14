from decimal import Decimal

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response

from finance.api_views import DateFilterMixin
from cessions.models import Cession
from cessions.serializers import CessionSerializer


class CessionListAPIView(DateFilterMixin, APIView):
    """
    GET /api/cessions/   liste des cessions déclarées vers DAMS Distribution
    (DateFilter sur `date_cession`). Lecture seule — consommateur `dams`.
    """

    def get(self, request):
        queryset = Cession.objects.select_related('produit').order_by(
            '-date_cession', '-created_at'
        )

        queryset = self.apply_date_filters(queryset, 'date_cession')

        produit_id = request.GET.get('produit')
        if produit_id:
            queryset = queryset.filter(produit_id=produit_id)

        return Response(CessionSerializer(queryset, many=True).data)


class CessionDashboardAPIView(DateFilterMixin, APIView):
    """
    GET /api/cessions/dashboard/   indicateurs agrégés (DateFilter sur
    `date_cession`) — même logique que finance.DashboardAPIView et
    engagements.EngagementDashboardAPIView. Sert notamment à `dams`
    (analyse_champ) à calculer un « CA total » (revenus finance + cessions)
    sans que dams_champs n'expose une notion de chiffre d'affaires
    dupliquée : c'est ce dashboard qui fait le calcul de la valeur des
    cessions, `dams` ne fait qu'additionner.

    `montant_total` est calculé sur TOUTES les cessions de la période, quel
    que soit `statut` (locale/transmise/echec) — une cession enregistrée
    est un fait économique du champ dès sa création ; son statut de
    transmission à DAMS Distribution n'a aucune incidence sur ce calcul
    (voir cessions/APP_CESSIONS.md — règle 5).
    """

    def get(self, request):
        queryset = Cession.objects.all()
        queryset = self.apply_date_filters(queryset, 'date_cession')

        montant_total = Decimal('0')
        quantite_totale = Decimal('0')

        for cession in queryset:
            montant_total += cession.quantite * cession.prix_cession
            quantite_totale += cession.quantite

        return Response({
            'nombre_cessions': queryset.count(),
            'quantite_totale': quantite_totale,
            'montant_total': montant_total,
        })


class CessionDetailAPIView(APIView):
    """
    GET /api/cessions/<pk>/   détail d'une cession.
    """

    def get(self, request, pk):
        cession = get_object_or_404(
            Cession.objects.select_related('produit'),
            pk=pk
        )
        return Response(CessionSerializer(cession).data)
