from datetime import timedelta
from django.db.models import Sum, Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response

from finance.models import Categorie, Operation, Produit, ProductionAgent
from .serializers import AgentPerformanceSerializer, CategorieSerializer, OperationDetailSerializer, OperationSerializer, ProduitSerializer

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

    
class DashboardAPIView(DateFilterMixin,APIView):
    def get(self, request):

        qs = (
            self.apply_date_filters(
                Operation.objects.prefetch_related(
                    'corrections'
                ),
                'operation_date'
            )
        )
        revenus = sum(
            operation.real_amount
            for operation in qs
            if operation.operation_type
            == 'revenu'
        )
        depenses = sum(
            operation.real_amount
            for operation in qs
            if operation.operation_type
            in [
                'depense',
                'stock'
            ]
        )
        return Response({
            'revenus': revenus,
            'depenses': depenses,
            'resultat':
                revenus - depenses,
            'nombre_operations':
                qs.count(),
            'nombre_produits':
                Produit.objects.count(),
            'nombre_agents':
                ProductionAgent.objects
                .values('agent')
                .distinct()
                .count(),
        })

class OperationListAPIView(DateFilterMixin, APIView):
    def get(self, request):
        queryset = Operation.objects.select_related('categorie').prefetch_related('corrections').order_by('-operation_date', '-created_at')
        queryset = self.apply_date_filters(queryset, 'operation_date')
        
        op_type = request.GET.get('type')
        if op_type == 'revenu':
            queryset = queryset.filter(operation_type='revenu')
        elif op_type == 'depense':
            queryset = queryset.filter(operation_type__in=['depense', 'stock'])
        categorie_id = request.GET.get(
            'categorie'
        )
        
        if categorie_id:
        
            queryset = queryset.filter(
                categorie_id=categorie_id
            )
        return Response(OperationSerializer(queryset, many=True).data)

class OperationDetailAPIView(APIView):
    def get( self,request, pk):

        operation = get_object_or_404(
            Operation.objects
            .select_related('categorie')
            .prefetch_related('corrections'),
            pk=pk
        )

        serializer = (
            OperationDetailSerializer(
                operation
            )
        )

        return Response(
            serializer.data
        )

class CategorieListAPIView(
    APIView
):

    def get(
        self,
        request
    ):

        serializer = (
            CategorieSerializer(
                Categorie.objects.all(),
                many=True
            )
        )

        return Response(
            serializer.data
        )
    
class ProduitListAPIView(DateFilterMixin, APIView):
    def get(self, request):
        queryset = Produit.objects.select_related(
            'operation_stock', 'operation_stock__categorie'
        ).prefetch_related('contributions__agent').order_by('-operation_stock__operation_date')
        
        queryset = self.apply_date_filters(queryset, 'operation_stock__operation_date')
        return Response(ProduitSerializer(queryset, many=True).data)



class ProduitDetailAPIView(APIView):
    def get(self, request, pk):
        produit = get_object_or_404(
            Produit.objects.select_related(
                'operation_stock', 'operation_stock__categorie'
            ).prefetch_related('contributions__agent'),
            pk=pk
        )
        return Response(ProduitSerializer(produit).data)


from django.db.models import (
    Count,
    Sum
)

from rest_framework.views import APIView
from rest_framework.response import Response


class AgentPerformanceAPIView(
    DateFilterMixin,
    APIView
):

    def get(
        self,
        request
    ):

        queryset = self.apply_date_filters(
            ProductionAgent.objects.select_related(
                'agent'
            ),
            'created_at'
        )

        data = (

            queryset

            .values(
                'agent__id',
                'agent__prenom',
                'agent__nom'
            )

            .annotate(

                nombre_interventions=
                    Count('id'),

                quantite_totale=
                    Sum(
                        'quantite_attachee'
                    )
            )

            .order_by(
                '-quantite_totale'
            )
        )

        serializer = AgentPerformanceSerializer(

            [

                {

                    'agent_id':
                        row['agent__id'],

                    'agent_nom':
                        (
                            f"{row['agent__prenom']} "
                            f"{row['agent__nom']}"
                        ),

                    'nombre_interventions':
                        row[
                            'nombre_interventions'
                        ],

                    'quantite_totale':
                        row[
                            'quantite_totale'
                        ]
                }

                for row in data

            ],

            many=True
        )

        return Response(
            serializer.data
        )