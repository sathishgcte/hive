from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Flat, MonthlyCharge, Payment

@transaction.atomic
def generate_charges(month):
    month = month.replace(day=1)
    count = 0
    for flat in Flat.objects.filter(active=True):
        _, created = MonthlyCharge.objects.get_or_create(
            flat=flat, month=month,
            defaults={'amount_due': flat.monthly_maintenance},
        )
        count += int(created)
    return count

@transaction.atomic
def receive_payment(charge_id, *, date, amount, mode, reference=''):
    charge = MonthlyCharge.objects.select_for_update().get(pk=charge_id)
    if amount <= 0:
        raise ValidationError('Payment must be greater than zero.')
    if amount > charge.outstanding:
        raise ValidationError('Payment exceeds the outstanding amount.')
    payment = Payment(charge=charge, date=date, amount=amount, mode=mode, reference=reference)
    payment.full_clean()
    payment.save()
    return payment
