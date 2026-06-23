from decimal import Decimal

from django.db.models import Avg, Count
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from rapports.api_views import DateFilterMixin
from cultures.models import BesoinCulture, FicheCulture, ParticipationCulture, RapportCulture
from cultures.serializers import (
    BaseConnaissancesSerializer,
    FicheCultureSerializer,
    RapportCultureListSerializer,
)


class CulturePagination(PageNumberPagination):
    page_size = 20


class FicheCultureListAPIView(DateFilterMixin, generics.ListAPIView):
    serializer_class = FicheCultureSerializer
    pagination_class = CulturePagination

    def get_queryset(self):
        qs = (
            FicheCulture.objects
            .select_related("technicien")
            .prefetch_related(
                "besoins__culture",
                "besoins__passages_recolte",
                "besoins__rapport_culture__participations__agent",
            )
            .order_by("-date_debut", "-created_at")
        )
        qs = self.apply_date_filters(qs, "date_debut")

        technicien = self.request.GET.get("technicien")
        if technicien:
            qs = qs.filter(technicien_id=technicien)

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
        .prefetch_related(
            "besoins__culture",
            "besoins__passages_recolte",
            "besoins__rapport_culture__participations__agent",
        )
    )


class RapportCultureListAPIView(generics.ListAPIView):
    """
    Liste paginée de tous les RapportCulture pour la direction (dams).
    Filtre : ?culture=Maïs  ?technicien=<id>
    """
    serializer_class = RapportCultureListSerializer
    pagination_class = CulturePagination

    def get_queryset(self):
        qs = (
            RapportCulture.objects
            .select_related(
                "besoin__culture",
                "besoin__fiche__technicien",
            )
            .prefetch_related("participations__agent")
            .order_by("-created_at")
        )
        culture = self.request.GET.get("culture")
        if culture:
            qs = qs.filter(besoin__culture__nom__icontains=culture)

        technicien = self.request.GET.get("technicien")
        if technicien:
            qs = qs.filter(besoin__fiche__technicien_id=technicien)

        return qs


class BaseConnaissancesAPIView(APIView):
    def get(self, request):
        rendements = {
            row["culture__nom"]: row
            for row in (
                BesoinCulture.objects
                .filter(recolte_cloturee=True)
                .values("culture__nom", "culture__unite_rendement")
                .annotate(
                    nb_campagnes=Count("id"),
                    moy_estime=Avg("rendement_estime"),
                    moy_reel=Avg("rendement_reel"),
                )
            )
        }

        agents_par_culture = {}
        for row in (
            ParticipationCulture.objects
            .values(
                "rapport__besoin__culture__nom",
                "agent__id", "agent__prenom", "agent__nom",
            )
            .annotate(
                nb_cycles=Count("id"),
                moy_implication=Avg("implication"),
                moy_maitrise=Avg("maitrise"),
            )
            .order_by("rapport__besoin__culture__nom", "-moy_maitrise")
        ):
            culture = row["rapport__besoin__culture__nom"]
            agents_par_culture.setdefault(culture, []).append({
                "agent_id":        row["agent__id"],
                "prenom":          row["agent__prenom"],
                "nom":             row["agent__nom"],
                "nb_cycles":       row["nb_cycles"],
                "moy_implication": round(row["moy_implication"], 2),
                "moy_maitrise":    round(row["moy_maitrise"], 2),
            })

        toutes_cultures = set(rendements) | set(agents_par_culture)
        result = []
        for culture in sorted(toutes_cultures):
            r = rendements.get(culture, {})
            moy_estime = r.get("moy_estime")
            moy_reel   = r.get("moy_reel")
            ecart_pct  = None
            if moy_estime and moy_reel and moy_estime != 0:
                ecart_pct = round(
                    (moy_reel - moy_estime) / moy_estime * Decimal("100"), 1
                )
            result.append({
                "culture":      culture,
                "unite":        r.get("culture__unite_rendement", "t"),
                "nb_campagnes": r.get("nb_campagnes", 0),
                "moy_estime":   moy_estime,
                "moy_reel":     moy_reel,
                "ecart_pct":    ecart_pct,
                "agents":       agents_par_culture.get(culture, []),
            })

        serializer = BaseConnaissancesSerializer(result, many=True)
        return Response(serializer.data)
