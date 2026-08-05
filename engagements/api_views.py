from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from finance.api_views import DateFilterMixin
from engagements.models import EngagementFinancier, RemboursementEngagement
from engagements.permissions import HasDamsDistributionAPIKey
from engagements.serializers import (
    EngagementFinancierSerializer,
    EngagementFinancierDetailSerializer,
    RemboursementEngagementSerializer,
)


class EngagementListCreateAPIView(DateFilterMixin, APIView):
    """
    GET  /api/engagements/   liste (filtres nature, technicien, reference_superviseur, etat + DateFilter sur date_engagement)
    POST /api/engagements/   création d'un engagement (avance_tresorerie ou depense_compte)
    """
    permission_classes = [HasDamsDistributionAPIKey]

    def get(self, request):
        queryset = EngagementFinancier.objects.select_related(
            'technicien', 'operation_generee'
        ).prefetch_related('remboursements')

        queryset = self.apply_date_filters(queryset, 'date_engagement')

        nature = request.GET.get('nature')
        if nature:
            queryset = queryset.filter(nature=nature)

        technicien_id = request.GET.get('technicien')
        if technicien_id:
            queryset = queryset.filter(technicien_id=technicien_id)

        # Permet à un superviseur de DAMS Distribution de ne récupérer que
        # ses propres engagements sans devoir tout lister puis filtrer.
        reference_superviseur = request.GET.get('reference_superviseur')
        if reference_superviseur:
            queryset = queryset.filter(reference_superviseur=reference_superviseur)

        etat = request.GET.get('etat')
        if etat:
            queryset = [engagement for engagement in queryset if engagement.etat == etat]

        serializer = EngagementFinancierSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EngagementFinancierSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        engagement = serializer.save()
        return Response(
            EngagementFinancierSerializer(engagement).data,
            status=status.HTTP_201_CREATED
        )


class EngagementDashboardAPIView(DateFilterMixin, APIView):
    """
    GET /api/engagements/dashboard/   indicateurs agrégés (direction, ou
    superviseur via ?reference_superviseur=) — même logique que
    finance.DashboardAPIView, pour éviter à un consommateur de tout
    paginer et recalculer côté client.
    """
    permission_classes = [HasDamsDistributionAPIKey]

    def get(self, request):
        queryset = EngagementFinancier.objects.prefetch_related('remboursements')

        queryset = self.apply_date_filters(queryset, 'date_engagement')

        reference_superviseur = request.GET.get('reference_superviseur')
        if reference_superviseur:
            queryset = queryset.filter(reference_superviseur=reference_superviseur)

        total_avance_tresorerie = queryset.filter(
            nature='avance_tresorerie'
        ).aggregate(total=Sum('montant_initial'))['total'] or Decimal('0')

        total_depense_compte = queryset.filter(
            nature='depense_compte'
        ).aggregate(total=Sum('montant_initial'))['total'] or Decimal('0')

        total_engage = total_avance_tresorerie + total_depense_compte

        total_rembourse = RemboursementEngagement.objects.filter(
            engagement__in=queryset
        ).aggregate(total=Sum('montant'))['total'] or Decimal('0')

        etats = [engagement.etat for engagement in queryset]

        return Response({
            'nombre_engagements': len(etats),
            'total_engage': total_engage,
            'total_avance_tresorerie': total_avance_tresorerie,
            'total_depense_compte': total_depense_compte,
            'total_rembourse': total_rembourse,
            'reste_a_rembourser': total_engage - total_rembourse,
            'nombre_ouverts': etats.count('ouvert'),
            'nombre_partiels': etats.count('partiel'),
            'nombre_soldes': etats.count('solde'),
        })


class EngagementDetailAPIView(APIView):
    """
    GET /api/engagements/<pk>/   détail d'un engagement avec ses remboursements
    """
    permission_classes = [HasDamsDistributionAPIKey]

    def get(self, request, pk):
        engagement = get_object_or_404(
            EngagementFinancier.objects
            .select_related('technicien', 'operation_generee')
            .prefetch_related('remboursements'),
            pk=pk
        )
        return Response(EngagementFinancierDetailSerializer(engagement).data)


class RemboursementListCreateAPIView(APIView):
    """
    GET  /api/engagements/<pk>/remboursements/   liste des remboursements d'un engagement
    POST /api/engagements/<pk>/remboursements/   enregistrement d'un remboursement partiel ou total
    """
    permission_classes = [HasDamsDistributionAPIKey]

    def get(self, request, pk):
        engagement = get_object_or_404(EngagementFinancier, pk=pk)
        remboursements = engagement.remboursements.all()
        return Response(RemboursementEngagementSerializer(remboursements, many=True).data)

    def post(self, request, pk):
        engagement = get_object_or_404(EngagementFinancier, pk=pk)
        serializer = RemboursementEngagementSerializer(
            data=request.data,
            context={'engagement': engagement}
        )
        serializer.is_valid(raise_exception=True)

        try:
            remboursement = serializer.save()
        except ValidationError as exc:
            return Response(
                {'detail': exc.message if hasattr(exc, 'message') else str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            RemboursementEngagementSerializer(remboursement).data,
            status=status.HTTP_201_CREATED
        )
