from django.contrib.auth import authenticate, login, logout
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render
)

from django.contrib.auth.decorators import login_required
from users.forms import AgentForm,LoginForm

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from users.models import Agent

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


@login_required
def agent_create(request):
    if request.method == 'POST':

        form = AgentForm(request.POST)

        if form.is_valid():

            agent = form.save(commit=False)

            agent.superviseur = request.user

            agent.save()

            messages.success(
                request,
                "Agent créé avec succès."
            )

            return redirect('agent_list')

    else:

        form = AgentForm()

    context = {
        'form': form
    }

    return render(
        request,
        'users/agents/agent_form.html',
        context
    )


@login_required
def agent_list(request):

    agents = (
        request.user.agents
        .all()
        .order_by('nom', 'prenom')
    )

    context = {
        'agents': agents
    }

    return render(
        request,
        'users/agents/agent_list.html',
        context
    )


@login_required
def agent_update(request, pk):

    agent = get_object_or_404(
        Agent,
        pk=pk,
        superviseur=request.user
    )

    if request.method == 'POST':

        form = AgentForm(
            request.POST,
            instance=agent
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Agent modifié avec succès."
            )

            return redirect(
                'agent_list'
            )
    else:

        form = AgentForm(
            instance=agent
        )
    context = {
        'form': form,
        'agent': agent,
        'is_update': True
    }

    return render(
        request,
        'users/agents/agent_form.html',
        context
    )