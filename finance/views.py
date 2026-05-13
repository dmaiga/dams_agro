from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now


from finance.models import Categorie, Operation
from finance.forms import OperationForm, CorrectionForm

from django.contrib.auth.decorators import login_required

@login_required
def category_list(request):

    categories = Categorie.objects.all()

    context = {
        'categories': categories
    }

    return render(
        request,
        'finance/categories/list.html',
        context
    )


@login_required
def operation_list(request):

    operations = Operation.objects.filter(
        corrects_operation__isnull=True
    )

    context = {
        'operations': operations
    }

    return render(
        request,
        'finance/operations/list.html',
        context
    )

@login_required
def operation_detail(request, pk):

    operation = get_object_or_404(
        Operation,
        pk=pk
    )

    corrections = operation.corrections.all()

    context = {
        'operation': operation,
        'corrections': corrections,
    }

    return render(
        request,
        'finance/operations/detail.html',
        context
    )

@login_required
def operation_create(request):

    if request.method == 'POST':

        form = OperationForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect('operation_list')

    else:
        form = OperationForm()

    context = {
        'form': form
    }

    return render(
        request,
        'finance/operations/form.html',
        context
    )

@login_required
def operation_correct(request, pk):

    operation = get_object_or_404(
        Operation,
        pk=pk
    )

    if request.method == 'POST':

        form = CorrectionForm(request.POST)

        if form.is_valid():

            correction = form.save(commit=False)

            correction.corrects_operation = operation

            correction.operation_type = operation.operation_type

            correction.operation_date = now().date()

            correction.label = (
                f"Correction - {operation.label}"
            )

            correction.is_manual_amount = True

            correction.save()

            return redirect(
                'operation_detail',
                pk=operation.pk
            )

    else:
        form = CorrectionForm()

    context = {
        'form': form,
        'operation': operation,
    }

    return render(
        request,
        'finance/operations/correction_form.html',
        context
    )