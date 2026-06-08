from django import forms

from rapports.models import RapportJournalier,ParticipationAgent
from django.forms import inlineformset_factory

class RapportJournalierForm(forms.ModelForm):

    class Meta:
        model = RapportJournalier
        fields = (
            "date",
            "activite_realisee",
            "probleme",
            "solution",
            "commentaire",
        )

        widgets = {
            "date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),
            "activite_realisee": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                }
            ),
            "probleme": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
            "solution": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
            "commentaire": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
        }


class ParticipationAgentForm(forms.ModelForm):

    class Meta:
        model = ParticipationAgent

        fields = (
            "agent",
            "implication",
            "maitrise",
            "observation",
        )

        widgets = {
            "agent": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "implication": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "maitrise": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "observation": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
        }


ParticipationAgentFormSet = inlineformset_factory(
    RapportJournalier,
    ParticipationAgent,
    form=ParticipationAgentForm,
    extra=5,
    can_delete=True
)