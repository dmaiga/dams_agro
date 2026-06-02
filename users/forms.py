from django import forms
from users.models import Agent

class LoginForm(forms.Form):

    phone_number = forms.CharField(
        label='Numéro de téléphone',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 70000000',
            }
        )
    )

    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Mot de passe',
            }
        )
    )



class AgentForm(forms.ModelForm):

    class Meta:

        model = Agent

        fields = [
            'prenom',
            'nom',
            'telephone',
            'actif',
            'note'
        ]

        widgets = {

            'prenom': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'nom': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'telephone': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'actif': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input'
                }
            ),

            'note': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3
                }
            ),
        }

        