from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum

POSITIVE = MinValueValidator(Decimal('0.01'))
MODES = [('UPI', 'UPI'), ('BANK', 'Bank transfer'), ('CASH', 'Cash'), ('CHEQUE', 'Cheque')]

class Flat(models.Model):
    number = models.CharField(max_length=30, unique=True)
    resident_name = models.CharField(max_length=120)
    monthly_maintenance = models.DecimalField(max_digits=10, decimal_places=2, validators=[POSITIVE])
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['number']

    def __str__(self):
        return self.number

class MonthlyCharge(models.Model):
    flat = models.ForeignKey(Flat, on_delete=models.PROTECT, related_name='charges')
    month = models.DateField(help_text='First day of the maintenance month.')
    amount_due = models.DecimalField(max_digits=10, decimal_places=2, validators=[POSITIVE])

    class Meta:
        ordering = ['flat__number']
        constraints = [models.UniqueConstraint(fields=['flat', 'month'], name='one_charge_per_flat_month')]

    @property
    def paid(self):
        return self.payments.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    @property
    def outstanding(self):
        return self.amount_due - self.paid

    @property
    def status(self):
        if self.outstanding <= 0:
            return 'Paid'
        return 'Partial' if self.paid else 'Unpaid'

    def __str__(self):
        return f'{self.flat} / {self.month:%B %Y}'

class Payment(models.Model):
    charge = models.ForeignKey(MonthlyCharge, on_delete=models.PROTECT, related_name='payments')
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[POSITIVE])
    mode = models.CharField(max_length=10, choices=MODES)
    reference = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-date', '-pk']

class Expense(models.Model):
    CATEGORIES = [(x, x) for x in ['Cleaning', 'Electricity', 'Water', 'Repairs', 'Other']]
    date = models.DateField()
    category = models.CharField(max_length=30, choices=CATEGORIES)
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[POSITIVE])
    mode = models.CharField(max_length=10, choices=MODES)

    class Meta:
        ordering = ['-date', '-pk']
