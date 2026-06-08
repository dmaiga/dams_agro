from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from django.shortcuts import render, redirect, get_object_or_404

from users.models import Agent

from rapports.forms import (
    RapportJournalierForm,
    ParticipationAgentForm,
)
from rapports.models import (
    RapportJournalier,
    ParticipationAgent,
)

@login_required
def rapport_list(request):
    rapports = RapportJournalier.objects.filter(
        superviseur=request.user
    )
    context = {
        "rapports": rapports,
    }
    return render(
        request,
        "rapports/rapport_list.html",
        context,
    )

@login_required
def rapport_create(request):
    ParticipationFormSet = modelformset_factory(
        ParticipationAgent,
        form=ParticipationAgentForm,
        extra=3,
        can_delete=False,
    )
    if request.method == "POST":
        form = RapportJournalierForm(request.POST)
        formset = ParticipationFormSet(
            request.POST,
            queryset=ParticipationAgent.objects.none()
        )
        agents = Agent.objects.filter(
            superviseur=request.user,
            actif=True,
        )
        for form_participant in formset:
            form_participant.fields[
                "agent"
            ].queryset = agents

        if form.is_valid() and formset.is_valid():
            rapport = form.save(commit=False)
            rapport.superviseur = request.user
            rapport.save()

            participations = formset.save(commit=False)

            for participation in participations:

                if participation.agent_id:

                    participation.rapport = rapport
                    participation.save()

            return redirect(
                "rapport_detail",
                pk=rapport.pk
            )
    else:
        form = RapportJournalierForm()
        formset = ParticipationFormSet(
            queryset=ParticipationAgent.objects.none()
        )
        agents = Agent.objects.filter(
            superviseur=request.user,
            actif=True,
        )
        for form_participant in formset:
            form_participant.fields[
                "agent"
            ].queryset = agents

    context = {
        "form": form,
        "formset": formset,
    }

    return render(
        request,
        "rapports/rapport_create.html",
        context,
    )


@login_required
def rapport_detail(request, pk):

    rapport = get_object_or_404(
        RapportJournalier,
        pk=pk,
        superviseur=request.user,
    )
    participants = rapport.participants.select_related(
        "agent"
    )
    context = {
        "rapport": rapport,
        "participants": participants,
    }
    return render(
        request,
        "rapports/rapport_detail.html",
        context,
    )