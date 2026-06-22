from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
from django.shortcuts import render, redirect, get_object_or_404

from cultures.forms import (
    CultureForm,
    FicheCultureForm,
    BesoinCultureFormSet,
    SuiviRendementForm,
)
from cultures.models import Culture, FicheCulture, BesoinCulture


@login_required
def culture_list_create(request):
    """Liste des cultures disponibles + formulaire d'ajout rapide."""
    if request.method == "POST":
        form = CultureForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Culture « {form.cleaned_data['nom']} » ajoutée.")
            return redirect("culture_list_create")
    else:
        form = CultureForm()

    cultures = Culture.objects.order_by("nom")
    return render(request, "cultures/culture_list_create.html", {
        "form": form,
        "cultures": cultures,
    })


@login_required
def fiche_list(request):
    fiches = (
        FicheCulture.objects
        .select_related("technicien")
        .annotate(
            nb_cultures=Count("besoins"),
            nb_recoltes=Count("besoins", filter=Q(besoins__date_recolte__isnull=False)),
        )
        .order_by("-date_debut", "-created_at")
    )
    return render(request, "cultures/fiche_list.html", {"fiches": fiches})


@login_required
def fiche_create(request):
    if request.method == "POST":
        form = FicheCultureForm(request.POST)
        formset = BesoinCultureFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            fiche = form.save(commit=False)
            fiche.technicien = request.user
            fiche.save()
            formset.instance = fiche
            formset.save()
            messages.success(request, "Fiche culture enregistrée.")
            return redirect("fiche_detail", pk=fiche.pk)
    else:
        form = FicheCultureForm()
        formset = BesoinCultureFormSet()

    return render(
        request,
        "cultures/fiche_create.html",
        {"form": form, "formset": formset},
    )


@login_required
def fiche_detail(request, pk):
    fiche = get_object_or_404(
        FicheCulture.objects.prefetch_related("besoins__culture"),
        pk=pk,
    )
    return render(request, "cultures/fiche_detail.html", {"fiche": fiche})


@login_required
def saisir_rendement(request, pk):
    """Saisie du rendement obtenu après récolte."""
    besoin = get_object_or_404(
        BesoinCulture.objects.select_related("culture", "fiche"),
        pk=pk,
    )

    if request.method == "POST":
        form = SuiviRendementForm(request.POST, instance=besoin)
        if form.is_valid():
            form.save()
            messages.success(request, "Rendement enregistré.")
            return redirect("fiche_detail", pk=besoin.fiche.pk)
    else:
        form = SuiviRendementForm(instance=besoin)

    return render(
        request,
        "cultures/saisir_rendement.html",
        {"form": form, "besoin": besoin},
    )


@login_required
def base_connaissances(request):
    """
    Historique personnel : objectif vs obtenu par culture pour l'agent connecté.
    Filtré sur request.user — chaque technicien voit sa propre précision d'estimation.
    L'agrégat global multi-agents est exposé côté API pour la direction.
    """
    stats = (
        BesoinCulture.objects
        .filter(rendement_reel__isnull=False, fiche__technicien=request.user)
        .values("culture__nom", "culture__unite_rendement")
        .annotate(
            nb_cycles=Count("id"),
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
            ecart_pct = (reel - est) / est * Decimal("100")
        lignes.append({
            "culture": s["culture__nom"],
            "unite": s["culture__unite_rendement"],
            "nb_cycles": s["nb_cycles"],
            "moy_estime": est,
            "moy_reel": reel,
            "ecart_pct": ecart_pct,
        })

    return render(request, "cultures/base_connaissances.html", {"lignes": lignes})
