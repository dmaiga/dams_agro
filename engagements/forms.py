from django import forms

from engagements.models import RemboursementEngagement
from engagements.services import enregistrer_remboursement


class RemboursementForm(forms.ModelForm):

    class Meta:
        model = RemboursementEngagement
        fields = [
            'montant',
            'date_remboursement',
        ]

        widgets = {

            'montant': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Montant remboursé',
                    'step': '0.01',
                }
            ),

            'date_remboursement': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                }
            ),
        }

    def __init__(self, *args, engagement=None, **kwargs):
        self.engagement = engagement
        super().__init__(*args, **kwargs)
        self.fields['date_remboursement'].required = False

    def clean_montant(self):
        montant = self.cleaned_data.get('montant')

        if montant is None:
            return montant

        if montant <= 0:
            raise forms.ValidationError('Le montant doit être supérieur à zéro.')

        if self.engagement and montant > self.engagement.reste_a_rembourser:
            raise forms.ValidationError(
                f"Le montant dépasse le reste à rembourser ({self.engagement.reste_a_rembourser})."
            )

        return montant

    def save(self, commit=True):
        return enregistrer_remboursement(
            engagement=self.engagement,
            montant=self.cleaned_data['montant'],
            date_remboursement=self.cleaned_data.get('date_remboursement'),
        )
