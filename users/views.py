from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

from .forms import LoginForm


def login_view(request):

    if request.user.is_authenticated:
        return redirect('operation_list')

    form = LoginForm()

    if request.method == 'POST':

        form = LoginForm(request.POST)

        if form.is_valid():

            phone_number = form.cleaned_data['phone_number']

            password = form.cleaned_data['password']

            user = authenticate(
                request,
                phone_number=phone_number,
                password=password
            )

            if user is not None:

                login(request, user)

                return redirect('operation_list')

            messages.error(
                request,
                'Identifiants invalides.'
            )

    context = {
        'form': form
    }

    return render(
        request,
        'users/login.html',
        context
    )


def logout_view(request):

    logout(request)

    return redirect('login')