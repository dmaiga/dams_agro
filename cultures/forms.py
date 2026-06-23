from django import forms
from django.forms import inlineformset_factory

from cultures.models import (
    Culture, FicheCulture, BesoinCulture, PassageRecolte,
    RapportCulture, ParticipationCulture,
)


class CultureForm(forms.ModelForm):
    class Meta:
        model = Culture
        fields = ("nom", "unite_rendement")
        widgets = {
            "nom": forms.TextInput(
                attrs={"class": "form-control",
                       "placeholder": "Ex : Tomate, Gombo, Pastèque…"}
            ),
            "unite_rendement": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "t"}
            ),
        }
        labels = {
            "nom": "Nom de la culture",
            "unite_rendement": "Unité de rendement",
        }


class FicheCultureForm(forms.ModelForm):
    class Meta:
        model = FicheCulture
        fields = ("date_debut", "superficie_ha", "note")
        widgets = {
            "date_debut": forms.DateInput(
                attrs={"type": "date", "class": "form-control"},
                format="%Y-%m-%d",
            ),
            "superficie_ha": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "placeholder": "Ex : 0.50"}
            ),
            "note": forms.Textarea(
                attrs={"class": "form-control", "rows": 2,
                       "placeholder": "Description de la  culture…"}
            ),
        }
        labels = {
            "date_debut": "Date de démarrage",
            "superficie_ha": "Superficie (ha)",
            "note": "Description",
        }


class BesoinCultureForm(forms.ModelForm):
    class Meta:
        model = BesoinCulture
        fields = (
            "culture",
            "semence_quantite",
            "semence_unite",
            "engrais",
            "produit_phyto",
            "rendement_estime",
        )
        widgets = {
            "culture": forms.Select(attrs={"class": "form-select"}),
            "semence_quantite": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "placeholder": "Ex : 10"}
            ),
            "semence_unite": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "kg"}
            ),
            "engrais": forms.Textarea(
                attrs={"class": "form-control", "rows": 2,
                       "placeholder": "Ex : 2 sacs NPK, 1 sac Urée"}
            ),
            "produit_phyto": forms.Textarea(
                attrs={"class": "form-control", "rows": 2,
                       "placeholder": "Ex : Herbicide sélectif 1L, Insecticide Dimétho 0.5L"}
            ),
            "rendement_estime": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "placeholder": "Ex : 1.5"}
            ),
        }
        labels = {
            "semence_quantite": "Qte Semence",
            "semence_unite": "Unité",
            "engrais": "Engrais fournis",
            "produit_phyto": "Produits phytosanitaires",
            "rendement_estime": "Objectif de rendement",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["culture"].queryset = Culture.objects.filter(actif=True)


BesoinCultureFormSet = inlineformset_factory(
    FicheCulture,
    BesoinCulture,
    form=BesoinCultureForm,
    fk_name="fiche",
    extra=1,
    can_delete=True,
)


class SuiviRendementForm(forms.ModelForm):
    class Meta:
        model = BesoinCulture
        fields = ("rendement_reel", "date_recolte", "observation_direction")
        widgets = {
            "rendement_reel": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "placeholder": "Ex : 1.8"}
            ),
            "date_recolte": forms.DateInput(
                attrs={"type": "date", "class": "form-control"},
                format="%Y-%m-%d",
            ),
            "observation_direction": forms.Textarea(
                attrs={"class": "form-control", "rows": 3,
                       "placeholder": "Remarques utiles pour l'analyse…"}
            ),
        }
        labels = {
            "rendement_reel": "Rendement obtenu",
            "date_recolte": "Date de récolte",
            "observation_direction": "Observation",
        }


class PassageRecolteForm(forms.ModelForm):
    class Meta:
        model = PassageRecolte
        fields = ("date_passage", "quantite", "observation")
        widgets = {
            "date_passage": forms.DateInput(
                attrs={"type": "date", "class": "form-control"},
                format="%Y-%m-%d",
            ),
            "quantite": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "placeholder": "Ex : 0.8"}
            ),
            "observation": forms.TextInput(
                attrs={"class": "form-control",
                       "placeholder": "Remarques sur ce passage (optionnel)"}
            ),
        }
        labels = {
            "date_passage": "Date du passage",
            "quantite": "Quantité récoltée",
            "observation": "Observation",
        }


class RapportCultureForm(forms.ModelForm):
    class Meta:
        model = RapportCulture
        fields = ("bilan_activites", "problemes", "solutions", "resultats", "perspectives")
        widgets = {
            "bilan_activites": forms.Textarea(
                attrs={"class": "form-control", "rows": 3,
                       "placeholder": "Résumé des travaux effectués sur ce cycle…"}
            ),
            "problemes": forms.Textarea(
                attrs={"class": "form-control", "rows": 3,
                       "placeholder": "Difficultés rencontrées (maladies, manque d'eau, etc.)…"}
            ),
            "solutions": forms.Textarea(
                attrs={"class": "form-control", "rows": 3,
                       "placeholder": "Solutions appliquées…"}
            ),
            "resultats": forms.Textarea(
                attrs={"class": "form-control", "rows": 3,
                       "placeholder": "Résultats obtenus…"}
            ),
            "perspectives": forms.Textarea(
                attrs={"class": "form-control", "rows": 3,
                       "placeholder": "Perspectives pour le prochain cycle…"}
            ),
        }


class ParticipationCultureForm(forms.ModelForm):
    class Meta:
        model = ParticipationCulture
        fields = ("agent", "implication", "maitrise", "observation")
        widgets = {
            "agent":       forms.Select(attrs={"class": "form-select"}),
            "implication": forms.Select(attrs={"class": "form-select"}),
            "maitrise":    forms.Select(attrs={"class": "form-select"}),
            "observation": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Observation (optionnel)"}
            ),
        }
        labels = {
            "agent":       "Agent",
            "implication": "Implication",
            "maitrise":    "Maîtrise de la culture",
            "observation": "Observation",
        }


ParticipationCultureFormSet = inlineformset_factory(
    RapportCulture,
    ParticipationCulture,
    form=ParticipationCultureForm,
    extra=1,
    can_delete=True,
)
