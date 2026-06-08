
from datetime import timedelta
from django.utils import timezone

from rest_framework import generics
from rest_framework.pagination import PageNumberPagination

from rapports.models import RapportJournalier
from rapports.serializers import RapportJournalierSerializer,SuperviseurSerializer

from users.models import User

class RapportPagination( PageNumberPagination):
    page_size = 20

class DateFilterMixin:
    """
    Mixin pour centraliser la logique de filtrage par dates.
    """
    def apply_period_filter(self, queryset, field_name):
        period = self.request.GET.get('period')
        today = timezone.now().date()
        
        filters = {
            'today': today,
            'week': today - timedelta(days=7),
            'month': today - timedelta(days=30),
            'year': today - timedelta(days=365)
        }
        
        if period in filters:
            if period == 'today':
                return queryset.filter(**{field_name: today})
            return queryset.filter(**{f'{field_name}__gte': filters[period]})
        return queryset

    def apply_custom_date_filter(self, queryset, field_name):
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        if date_from:
            queryset = queryset.filter(**{f'{field_name}__gte': date_from})
        if date_to:
            queryset = queryset.filter(**{f'{field_name}__lte': date_to})
        return queryset

    def apply_date_filters(self, queryset, field_name):
        queryset = self.apply_period_filter(queryset, field_name)
        queryset = self.apply_custom_date_filter(queryset, field_name)
        return queryset


class RapportListAPIView(DateFilterMixin, generics.ListAPIView):
    serializer_class = RapportJournalierSerializer
    pagination_class = RapportPagination
    def get_queryset(self):
        queryset = (
            RapportJournalier.objects
            .select_related("superviseur")
            .prefetch_related(
                "participants",
                "participants__agent"
            )
            .order_by("-date")
        )
        queryset = self.apply_date_filters(
            queryset,
            "date"
        )
        superviseur = self.request.GET.get(
            "superviseur"
        )
        if superviseur:
            queryset = queryset.filter(
                superviseur_id=superviseur
            )
        return queryset
    

class RapportDetailAPIView( generics.RetrieveAPIView):
    serializer_class = RapportJournalierSerializer
    queryset = (
        RapportJournalier.objects
        .select_related("superviseur")
        .prefetch_related(
            "participants",
            "participants__agent"
        )
    )

class SuperviseurListAPIView( generics.ListAPIView):

    serializer_class = ( SuperviseurSerializer)

    queryset = (
        User.objects
        .filter(
            rapports__isnull=False
        )
        .distinct()
    )