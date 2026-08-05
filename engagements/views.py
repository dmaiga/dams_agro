from decimal import Decimal

from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied

from engagements.forms import RemboursementForm
from engagements.models import EngagementFinancier, RemboursementEngagement


@login_required
def engagement_list(request):

    # Gestion des engagements/dettes réservée au responsable financier.
    # La création reste exclusive à l'API DAMS Distribution.
    if request.user.est_superviseur:
        raise PermissionDenied

    engagements = EngagementFinancier.objects.select_related(
        'technicien', 'operation_generee'
    ).prefetch_related('remboursements')

    # Pour se situer d'un coup d'œil, les 3 totaux doivent rester cohérents
    # entre eux (reste = engagé - remboursé), toutes natures confondues :
    # une avance_tresorerie et une depense_compte créent la même dette,
    # seule la génération d'Operation en finance diffère (voir services.py).
    total_engage = engagements.aggregate(
        total=Sum('montant_initial')
    )['total'] or Decimal('0')

    total_rembourse = RemboursementEngagement.objects.filter(
        engagement__in=engagements
    ).aggregate(total=Sum('montant'))['total'] or Decimal('0')

    context = {
        'engagements': engagements,
        'total_engage': total_engage,
        'total_rembourse': total_rembourse,
        'total_reste_a_rembourser': total_engage - total_rembourse,
    }

    return render(
        request,
        'engagements/list.html',
        context
    )


@login_required
def engagement_detail(request, pk):

    if request.user.est_superviseur:
        raise PermissionDenied

    engagement = get_object_or_404(
        EngagementFinancier.objects
        .select_related('technicien', 'operation_generee')
        .prefetch_related('remboursements'),
        pk=pk
    )

    context = {
        'engagement': engagement,
        'remboursements': engagement.remboursements.all(),
    }

    return render(
        request,
        'engagements/detail.html',
        context
    )


@login_required
def remboursement_create(request, pk):

    if request.user.est_superviseur:
        raise PermissionDenied

    engagement = get_object_or_404(EngagementFinancier, pk=pk)

    if request.method == 'POST':

        form = RemboursementForm(
            request.POST,
            engagement=engagement
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Remboursement enregistré."
            )

            return redirect(
                'engagement_detail',
                pk=engagement.pk
            )

    else:

        form = RemboursementForm(
            engagement=engagement
        )

    context = {
        'form': form,
        'engagement': engagement,
    }

    return render(
        request,
        'engagements/remboursement_form.html',
        context
    )
