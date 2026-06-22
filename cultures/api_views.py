from decimal import Decimal

from django.db.models import Avg, Count
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from rapports.api_views import DateFilterMixin
from cultures.models import BesoinCulture, FicheCulture
from cultures.serializers import BaseConnaissancesSerializer, FicheCultureSerializer


class CulturePagination(PageNumberPagination):
    page_size = 20


class FicheCultureListAPIView(DateFilterMixin, generics.ListAPIView):
    serializer_class = FicheCultureSerializer
    pagination_class = CulturePagination

    def get_queryset(self):
        qs = (
            FicheCulture.objects
            .select_related("technicien")
            .prefetch_related("besoins__culture")
            .order_by("-date_debut", "-created_at")
        )
        qs = self.apply_date_filters(qs, "date_debut")

        technicien = self.request.GET.get("technicien")
        if technicien:
            qs = qs.filter(technicien_id=technicien)

        # Filtrer par année/mois dérivés de date_debut (remplace l'ancien filtre saison)
        annee = self.request.GET.get("annee")
        if annee:
            qs = qs.filter(date_debut__year=annee)

        mois = self.request.GET.get("mois")
        if mois:
            qs = qs.filter(date_debut__month=mois)

        return qs


class FicheCultureDetailAPIView(generics.RetrieveAPIView):
    serializer_class = FicheCultureSerializer
    queryset = (
        FicheCulture.objects
        .select_related("technicien")
        .prefetch_related("besoins__culture")
    )


class BaseConnaissancesAPIView(APIView):
    def get(self, request):
        stats = (
            BesoinCulture.objects
            .filter(rendement_reel__isnull=False)
            .values("culture__nom", "culture__unite_rendement")
            .annotate(
                nb_campagnes=Count("id"),
                moy_estime=Avg("rendement_estime"),
                moy_reel=Avg("rendement_reel"),
            )
            .order_by("culture__nom")
        )

        lignes = []
        for s in stats:
            est = s["moy_estime"]
            reel = s["moy_reel"]
            ecart_pct = None
            if est and reel is not None:
                ecart_pct = round((reel - est) / est * Decimal("100"), 1)
            lignes.append({
                "culture": s["culture__nom"],
                "unite": s["culture__unite_rendement"],
                "nb_campagnes": s["nb_campagnes"],
                "moy_estime": est,
                "moy_reel": reel,
                "ecart_pct": ecart_pct,
            })

        serializer = BaseConnaissancesSerializer(lignes, many=True)
        return Response(serializer.data)
