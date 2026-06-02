
from django import forms
from finance.models import Operation,Categorie,Produit,ProductionAgent
from django.db.models import Q
from users.models import Agent

class BaseOperationForm(forms.ModelForm):

    class Meta:

        model = Operation

        fields = [
            'categorie',
            'label',
            'quantity',
            'unit_price',
            'operation_date',
            'note',
        ]

        widgets = {

            'categorie': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),

            'label': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),

            'quantity': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                }
            ),

            'unit_price': forms.NumberInput(
                attrs={
                    'class': 'form-control',
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
                }
            ),
        }

class RevenueForm(BaseOperationForm):

    def clean(self):

        cleaned_data = super().clean()

        quantity = cleaned_data.get(
            'quantity'
        )

        unit_price = cleaned_data.get(
            'unit_price'
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

        return cleaned_data

    def save(self, commit=True):

        instance = super().save(
            commit=False
        )

        instance.operation_type = 'revenu'

        if commit:
            instance.save()

        return instance

class ExpenseForm(BaseOperationForm):


    def clean(self):

        cleaned_data = super().clean()

        categorie = cleaned_data.get(
            'categorie'
        )

        quantity = cleaned_data.get(
            'quantity'
        )

        unit_price = cleaned_data.get(
            'unit_price'
        )

        if not categorie:

            self.add_error(
                'categorie',
                'La catégorie est obligatoire.'
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

        return cleaned_data

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields[
            'categorie'
        ].queryset = Categorie.objects.filter(
            Q(usage_type='depense')
            |
            Q(usage_type='both')
        )

    def save(self, commit=True):

        instance = super().save(
            commit=False
        )

        instance.operation_type = 'depense'

        if commit:
            instance.save()

        return instance

class StockForm(BaseOperationForm):


    def clean(self):

        cleaned_data = super().clean()

        quantity = cleaned_data.get(
            'quantity'
        )

        unit_price = cleaned_data.get(
            'unit_price'
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

        return cleaned_data

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields[
            'categorie'
        ].queryset = Categorie.objects.filter(
            Q(usage_type='stock')
            |
            Q(usage_type='both')
        )
    


    def save(self, commit=True):
    
        instance = super().save(
            commit=False
        )
    
        instance.operation_type = 'stock'
    
        if commit:
        
            instance.save()
    
            Produit.objects.create(
            
                nom=instance.label,
    
                operation_stock=instance,
            )
    
        return instance

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
    def clean_amount(self):

        amount = self.cleaned_data.get('amount')

        if amount is not None and amount <= 0:

            raise forms.ValidationError(
                'Le montant doit être supérieur à zéro.'
            )

        return amount

class ProduitForm(forms.ModelForm):

    class Meta:

        model = Produit

        fields = [
            'quantite_initiale',
            'quantite_vendue',
            'quantite_perdue',
            'quantite_offerte',
            'note',
        ]

        widgets = {

            'quantite_initiale': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '0'
                }
            ),

            'quantite_vendue': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '0'
                }
            ),

            'quantite_perdue': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '0'
                }
            ),

            'quantite_offerte': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '0'
                }
            ),

            'note': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                }
            ),
        }
        
    def clean(self):

        cleaned_data = super().clean()

        initiale = (
            cleaned_data.get(
                'quantite_initiale'
            ) or 0
        )

        vendue = (
            cleaned_data.get(
                'quantite_vendue'
            ) or 0
        )

        perdue = (
            cleaned_data.get(
                'quantite_perdue'
            ) or 0
        )

        offerte = (
            cleaned_data.get(
                'quantite_offerte'
            ) or 0
        )

        total = (
            vendue
            + perdue
            + offerte
        )

        if total > initiale:

            raise forms.ValidationError(
                (
                    'Le total vendu, perdu et offert '
                    'dépasse la quantité initiale.'
                )
            )

        return cleaned_data

class ProductionAgentForm(forms.ModelForm):

    class Meta:
        model = ProductionAgent
        fields = [
            'agent',
            'quantite_attachee'
        ]
        widgets = {
            'agent': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),
            'quantite_attachee': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': 0
                }
            ),
        }

    def __init__(
        self,
        *args,
        superviseur=None,
        **kwargs
    ):

        super().__init__(*args, **kwargs)

        if superviseur:

            self.fields['agent'].queryset = (
                Agent.objects.filter(
                    superviseur=superviseur,
                    actif=True
                )
            )