from django import forms
from finance.models import Operation


class OperationForm(forms.ModelForm):

    class Meta:
        model = Operation

        fields = [
            'operation_type',
            'categorie',
            'label',
            'quantity',
            'unit_price',
            'operation_date',
            'note',
        ]

        widgets = {

            'operation_type': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
            'categorie': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
            'label': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Exemple: Achat glace',
                }
            ),

            'quantity': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Exemple: 5',
                    'step': '0.01',
                }
            ),
            'unit_price': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Exemple: 150',
                    'step': '0.01',
                }
            ),

            'operation_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                }
            ),

            'note': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': (
                        'Ajouter une description '
                        'ou des détails complémentaires...'
                    )
                }
            ),
        }
   
    def clean(self):

        cleaned_data = super().clean()

        quantity = cleaned_data.get('quantity')

        unit_price = cleaned_data.get('unit_price')

        operation_type = cleaned_data.get(
            'operation_type'
        )

        categorie = cleaned_data.get(
            'categorie'
        )
        if not operation_type:
        
            self.add_error(
                'operation_type',
                'Veuillez sélectionner un type.'
            )
        if quantity is None:

            self.add_error(
                'quantity',
                'La quantité est obligatoire.'
            )

        if unit_price is None:

            self.add_error(
                'unit_price',
                'Le prix unitaire est obligatoire.'
            )

        if (
            operation_type == 'depense'
            and not categorie
        ):

            self.add_error(
                'categorie',
                'Une catégorie est obligatoire pour une dépense.'
            )

        return cleaned_data

class CorrectionForm(forms.ModelForm):

    class Meta:
        model = Operation

        fields = [
            'amount',
            'note',
        ]

        widgets = {

            'amount': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'le montant corrigé',
                    'step': '0.01',
                }
            ),

            'note': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 5,
                    'placeholder': (
                        'Expliquer la correction :\n'
                        '- erreur de prix unitaire\n'
                        '- quantité réelle\n'
                        '- montant corrigé'
                    )
                }
            ),
        }