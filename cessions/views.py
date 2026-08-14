from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied

from cessions.forms import CessionForm
from cessions.models import Cession
from cessions.services import transmettre_cession


@login_required
def cession_list(request):

    # Déclaration des cessions réservée au responsable financier — un
    # technicien de terrain (superviseur) n'a pas à déclarer ce qui est
    # cédé à DAMS Distribution. Même branche que engagements/finance.
    if request.user.est_superviseur:
        raise PermissionDenied

    cessions = Cession.objects.select_related('produit')

    context = {
        'cessions': cessions,
    }

    return render(
        request,
        'cessions/list.html',
        context
    )


@login_required
def cession_create(request):

    if request.user.est_superviseur:
        raise PermissionDenied

    if request.method == 'POST':

        form = CessionForm(request.POST)

        if form.is_valid():

            cession = form.save()

            # La cession est déjà acquise localement à ce stade — la
            # transmission est une étape supplémentaire dont l'échec ne
            # doit jamais remettre en cause l'enregistrement local.
            if transmettre_cession(cession):

                messages.success(
                    request,
                    "Cession enregistrée et transmise à DAMS Distribution."
                )

            else:

                messages.warning(
                    request,
                    "Cession enregistrée, mais la transmission à DAMS "
                    "Distribution a échoué. Elle sera visible comme "
                    "« Échec de transmission » dans la liste."
                )

            return redirect('cession_list')

    else:

        form = CessionForm()

    context = {
        'form': form,
    }

    return render(
        request,
        'cessions/form.html',
        context
    )
