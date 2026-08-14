from django import forms

from cessions.models import Cession


class CessionForm(forms.ModelForm):

    class Meta:
        model = Cession

        fields = [
            'produit',
            'quantite',
            'prix_cession',
            'date_cession',
        ]

        widgets = {

            'produit': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),

            'quantite': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                }
            ),

            'prix_cession': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                }
            ),

            'date_cession': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                }
            ),
        }

    def clean_quantite(self):
        quantite = self.cleaned_data.get('quantite')

        if quantite is not None and quantite <= 0:
            raise forms.ValidationError('La quantité doit être supérieure à zéro.')

        return quantite

    def clean_prix_cession(self):
        prix_cession = self.cleaned_data.get('prix_cession')

        if prix_cession is not None and prix_cession <= 0:
            raise forms.ValidationError('Le prix de cession doit être supérieur à zéro.')

        return prix_cession
