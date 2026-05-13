from django import forms


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