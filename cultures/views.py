import datetime as dt
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
from django.shortcuts import render, redirect, get_object_or_404

from users.models import Agent
from cultures.forms import (
    CultureForm,
    FicheCultureForm,
    BesoinCultureFormSet,
    SuiviRendementForm,
    PassageRecolteForm,
    RapportCultureForm,
    ParticipationCultureFormSet,
)
from cultures.models import (
    Culture, FicheCulture, BesoinCulture, PassageRecolte,
    RapportCulture, ParticipationCulture,
)


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
            nb_recoltes=Count("besoins", filter=Q(besoins__recolte_cloturee=True)),
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
        FicheCulture.objects.prefetch_related(
            "besoins__culture",
            "besoins__passages_recolte",
            "besoins__rapport_culture__participations__agent",
        ),
        pk=pk,
    )
    return render(request, "cultures/fiche_detail.html", {"fiche": fiche})


@login_required
def ajouter_passage(request, pk):
    """Enregistre un passage de récolte (date + quantité) sur un besoin."""
    besoin = get_object_or_404(
        BesoinCulture.objects.select_related("culture", "fiche"),
        pk=pk,
        fiche__technicien=request.user,
    )
    if besoin.recolte_cloturee:
        messages.warning(request, "La récolte est déjà clôturée, aucun passage ne peut être ajouté.")
        return redirect("fiche_detail", pk=besoin.fiche.pk)

    form = PassageRecolteForm(request.POST or None)
    if form.is_valid():
        passage = form.save(commit=False)
        passage.besoin = besoin
        passage.save()
        messages.success(request, "Passage de récolte enregistré.")
        return redirect("fiche_detail", pk=besoin.fiche.pk)

    return render(
        request,
        "cultures/ajouter_passage.html",
        {"form": form, "besoin": besoin},
    )


@login_required
def cloturer_recolte(request, pk):
    """
    Clôture la récolte d'un besoin : somme les passages, fixe rendement_reel
    et marque recolte_cloturee=True. Redirige ensuite vers le rapport de clôture.
    """
    besoin = get_object_or_404(
        BesoinCulture.objects.select_related("culture", "fiche")
                             .prefetch_related("passages_recolte"),
        pk=pk,
        fiche__technicien=request.user,
    )
    if besoin.recolte_cloturee:
        messages.info(request, "La récolte est déjà clôturée.")
        return redirect("fiche_detail", pk=besoin.fiche.pk)

    passages = list(besoin.passages_recolte.all())
    if not passages:
        messages.warning(request, "Aucun passage de récolte enregistré. Ajoutez au moins un passage avant de clôturer.")
        return redirect("fiche_detail", pk=besoin.fiche.pk)

    total = besoin.total_passages()

    if request.method == "POST":
        observation = request.POST.get("observation_direction", "")
        besoin.rendement_reel = total
        besoin.date_recolte = dt.date.today()
        besoin.recolte_cloturee = True
        besoin.observation_direction = observation
        besoin.save()
        messages.success(request, f"Récolte clôturée — rendement total : {total} {besoin.unite_rendement}.")
        return redirect("rapport_culture_create", pk=besoin.pk)

    return render(
        request,
        "cultures/cloturer_recolte.html",
        {
            "besoin": besoin,
            "passages": passages,
            "total": total,
        },
    )


@login_required
def saisir_rendement(request, pk):
    """Conservé pour compatibilité URL — redirige vers cloturer_recolte."""
    return redirect("cloturer_recolte", pk=pk)


@login_required
def rapport_culture_create(request, pk):
    """
    Saisie du rapport de clôture d'un besoin : bilan + participants.
    Accessible immédiatement après cloturer_recolte, et depuis fiche_detail
    pour les besoins déjà clôturés sans rapport.
    """
    besoin = get_object_or_404(
        BesoinCulture.objects.select_related("culture", "fiche"),
        pk=pk,
        fiche__technicien=request.user,
    )
    if not besoin.recolte_cloturee:
        messages.warning(request, "La récolte doit être clôturée avant de rédiger le rapport.")
        return redirect("fiche_detail", pk=besoin.fiche.pk)

    rapport, _ = RapportCulture.objects.get_or_create(besoin=besoin)

    agents_qs = Agent.objects.filter(superviseur=request.user, actif=True)

    form = RapportCultureForm(request.POST or None, instance=rapport)
    formset = ParticipationCultureFormSet(
        request.POST or None,
        instance=rapport,
    )
    for f in formset.forms:
        f.fields["agent"].queryset = agents_qs

    if form.is_valid() and formset.is_valid():
        form.save()
        formset.save()
        messages.success(request, "Rapport de clôture enregistré.")
        return redirect("fiche_detail", pk=besoin.fiche.pk)

    return render(
        request,
        "cultures/rapport_culture_create.html",
        {
            "besoin": besoin,
            "rapport": rapport,
            "form": form,
            "formset": formset,
        },
    )


@login_required
def base_connaissances(request):
    """
    Base de connaissances globale : rendements + évaluations agents par culture.
    Tous agents confondus — l'isolation par agent est réservée aux filtres de fiche_list.
    """
    stats_rendement = (
        BesoinCulture.objects
        .filter(recolte_cloturee=True)
        .values("culture__nom", "culture__unite_rendement")
        .annotate(
            nb_cycles=Count("id"),
            moy_estime=Avg("rendement_estime"),
            moy_reel=Avg("rendement_reel"),
        )
        .order_by("culture__nom")
    )

    stats_agents = (
        ParticipationCulture.objects
        .values(
            "rapport__besoin__culture__nom",
            "agent__id",
            "agent__prenom",
            "agent__nom",
        )
        .annotate(
            nb_cycles=Count("id"),
            moy_implication=Avg("implication"),
            moy_maitrise=Avg("maitrise"),
        )
        .order_by("rapport__besoin__culture__nom", "-moy_maitrise")
    )

    agents_par_culture = {}
    for row in stats_agents:
        culture = row["rapport__besoin__culture__nom"]
        agents_par_culture.setdefault(culture, []).append(row)

    lignes = []
    for s in stats_rendement:
        culture = s["culture__nom"]
        est = s["moy_estime"]
        reel = s["moy_reel"]
        ecart_pct = None
        if est and reel is not None:
            ecart_pct = (reel - est) / est * Decimal("100")
        lignes.append({
            "culture":           culture,
            "unite":             s["culture__unite_rendement"],
            "nb_cycles":         s["nb_cycles"],
            "moy_estime":        est,
            "moy_reel":          reel,
            "ecart_pct":         ecart_pct,
            "agents":            agents_par_culture.get(culture, []),
        })

    return render(request, "cultures/base_connaissances.html", {"lignes": lignes})
