from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import FlatForm, MonthForm, PaymentForm, ExpenseForm
from .models import Flat, MonthlyCharge, Payment, Expense
from .services import generate_charges, receive_payment


def selected_month(request):
    form = MonthForm(request.GET if 'month' in request.GET else {'month': timezone.localdate().strftime('%Y-%m')})
    return form, form.cleaned_data['month'] if form.is_valid() else None


def total(queryset, field):
    return queryset.aggregate(value=Sum(field))['value'] or Decimal('0.00')


@login_required
def dashboard(request):
    form, month = selected_month(request)
    if month is None:
        return HttpResponseBadRequest('Invalid month. Use YYYY-MM.')
    payments = Payment.objects.filter(date__year=month.year, date__month=month.month)
    expenses = Expense.objects.filter(date__year=month.year, date__month=month.month)
    charges = MonthlyCharge.objects.filter(month=month)
    received = total(payments, 'amount')
    spent = total(expenses, 'amount')
    outstanding = sum((charge.outstanding for charge in charges), Decimal('0.00'))
    return render(request, 'dashboard.html', {'month_form': form, 'month': month,
        'received': received, 'spent': spent, 'net': received - spent,
        'outstanding': outstanding, 'charge_count': charges.count()})


@login_required
def flats(request, pk=None):
    flat = get_object_or_404(Flat, pk=pk) if pk else None
    form = FlatForm(request.POST or None, instance=flat)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Flat saved. Existing monthly charges are unchanged.')
        return redirect('flats')
    return render(request, 'flats.html', {'form': form, 'flats': Flat.objects.all(), 'editing': flat})


@login_required
def charges(request):
    month_form, month = selected_month(request)
    if month is None:
        return HttpResponseBadRequest('Invalid month. Use YYYY-MM.')
    if request.method == 'POST':
        form = MonthForm(request.POST)
        if form.is_valid():
            month = form.cleaned_data['month']
            count = generate_charges(month)
            messages.success(request, f'{count} new charges created. Existing charges were preserved.')
            return redirect(f"/charges/?month={month:%Y-%m}")
        return HttpResponseBadRequest('Invalid month. Use YYYY-MM.')
    rows = MonthlyCharge.objects.filter(month=month).select_related('flat')
    return render(request, 'charges.html', {'month_form': month_form, 'month': month, 'charges': rows})


@login_required
def payment(request, pk):
    charge = get_object_or_404(MonthlyCharge.objects.select_related('flat'), pk=pk)
    form = PaymentForm(request.POST or None, initial={'date': timezone.localdate()})
    if request.method == 'POST' and form.is_valid():
        try:
            receive_payment(charge.pk, **form.cleaned_data)
        except ValidationError as error:
            form.add_error(None, error)
        else:
            messages.success(request, 'Payment recorded.')
            return redirect(f'/charges/?month={charge.month:%Y-%m}')
    return render(request, 'payment.html', {'form': form, 'charge': charge, 'payments': charge.payments.all()})


@login_required
def expenses(request):
    month_form, month = selected_month(request)
    if month is None:
        return HttpResponseBadRequest('Invalid month. Use YYYY-MM.')
    form = ExpenseForm(request.POST or None, initial={'date': timezone.localdate()})
    if request.method == 'POST' and form.is_valid():
        expense = form.save()
        messages.success(request, 'Expense recorded.')
        return redirect(f'/expenses/?month={expense.date:%Y-%m}')
    rows = Expense.objects.filter(date__year=month.year, date__month=month.month)
    return render(request, 'expenses.html', {'form': form, 'month_form': month_form, 'expenses': rows})
