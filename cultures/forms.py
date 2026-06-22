from django import forms
from django.forms import inlineformset_factory

from cultures.models import Culture, FicheCulture, BesoinCulture


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
            "semence_quantite": "Quantité",
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
