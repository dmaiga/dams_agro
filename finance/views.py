from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib import messages
from finance.forms import ExpenseForm,RevenueForm,StockForm,CorrectionForm,ProduitForm,ProductionAgentForm
from finance.models import Categorie, Operation, Produit,ProductionAgent



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
def operation_entry(request):

    return render(
        request,
        'finance/operations/entry_forms.html'
    )

@login_required
def revenue_create(request):

    if request.method == 'POST':

        form = RevenueForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect(
                'operation_list'
            )

    else:

        form = RevenueForm()

    return render(
        request,
        'finance/operations/revenue_form.html',
        {
            'form': form
        }
    )


@login_required
def expense_create(request):

    if request.method == 'POST':

        form = ExpenseForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect(
                'operation_list'
            )

    else:

        form = ExpenseForm()

    return render(
        request,
        'finance/operations/expense_form.html',
        {
            'form': form
        }
    )

@login_required
def stock_create(request):

    if request.method == 'POST':

        form = StockForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect(
                'operation_list'
            )

    else:

        form = StockForm()

    return render(
        request,
        'finance/operations/stock_form.html',
        {
            'form': form
        }
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


@login_required
def product_list(request):

    products = Produit.objects.select_related(
        'operation_stock',
        'operation_stock__categorie'
    ).order_by('-created_at')
    
    context = {
        'products': products
    }

    return render(
        request,
        'finance/products/list.html',
        context
    )

@login_required
def product_detail(request, pk):

    product = get_object_or_404(
        Produit.objects.select_related(
            'operation_stock'
        ),
        pk=pk
    )

    context = {
        'product': product,
        'contributions': (
            product.contributions
            .select_related('agent')
            .all()
            .order_by('-quantite_attachee')
        )
    }

    return render(
        request,
        'finance/products/detail.html',
        context
    )

@login_required
def product_update(request, pk):
    product = get_object_or_404(
        Produit,
        pk=pk
    )
    if request.method == 'POST':
        form = ProduitForm(
            request.POST,
            instance=product
        )
        if form.is_valid():
            form.save()
            return redirect(
                'product_detail',
                pk=product.pk
            )
    else:
        form = ProduitForm(
            instance=product
        )
    context = {
        'form': form,
        'product': product,
    }

    return render(
        request,
        'finance/products/form.html',
        context
    )

@login_required
def production_create(request, produit_id):
    produit = get_object_or_404(
        Produit,
        pk=produit_id
    )
    if request.method == 'POST':
        form = ProductionAgentForm(
            request.POST,
            superviseur=request.user
        )
        if form.is_valid():
            production = form.save(
                commit=False
            )
            production.produit = produit
            production.save()
            messages.success(
                request,
                "Production enregistrée."
            )
            return redirect(
                'product_list'
            )
    else:
        form = ProductionAgentForm(
            superviseur=request.user
        )
    return render(
        request,
        'finance/products/production/form.html',
        {
            'form': form,
            'produit': produit
        }
    )

@login_required
def production_update(request, pk):

    production = get_object_or_404(
        ProductionAgent,
        pk=pk
    )
    if request.method == 'POST':

        form = ProductionAgentForm(
            request.POST,
            instance=production,
            superviseur=request.user
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Production modifiée avec succès."
            )

            return redirect(
                'product_detail',
                pk=production.produit.pk
            )

    else:

        form = ProductionAgentForm(
            instance=production,
            superviseur=request.user
        )

    return render(
        request,
        'finance/products/production/form.html',
        {
            'form': form,
            'produit': production.produit,
            'is_update': True
        }
    )