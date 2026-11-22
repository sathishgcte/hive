from datetime import date
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from .models import Flat, MonthlyCharge, Expense
from .services import generate_charges, receive_payment

class AccountsTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='tester', password='test-only-password')
        self.flat = Flat.objects.create(number='A-101', resident_name='Ravi', monthly_maintenance=Decimal('2000'))
        self.month = date(2026, 11, 1)

    def test_charge_generation_is_idempotent_and_preserves_history(self):
        self.assertEqual(generate_charges(self.month), 1)
        self.flat.monthly_maintenance = Decimal('2500')
        self.flat.save()
        self.assertEqual(generate_charges(self.month), 0)
        self.assertEqual(MonthlyCharge.objects.get().amount_due, Decimal('2000'))

    def test_inactive_flats_are_skipped(self):
        self.flat.active = False
        self.flat.save()
        self.assertEqual(generate_charges(self.month), 0)

    def test_partial_payment_and_overpayment_rejection(self):
        generate_charges(self.month)
        charge = MonthlyCharge.objects.get()
        receive_payment(charge.pk, date=self.month, amount=Decimal('1000'), mode='UPI')
        self.assertEqual(charge.outstanding, Decimal('1000'))
        self.assertEqual(charge.status, 'Partial')
        with self.assertRaises(ValidationError):
            receive_payment(charge.pk, date=self.month, amount=Decimal('1001'), mode='CASH')
        receive_payment(charge.pk, date=self.month, amount=Decimal('1000'), mode='BANK')
        self.assertEqual(charge.status, 'Paid')

    def test_nonpositive_payment_rejected(self):
        generate_charges(self.month)
        charge = MonthlyCharge.objects.get()
        for amount in [Decimal('0'), Decimal('-1')]:
            with self.assertRaises(ValidationError):
                receive_payment(charge.pk, date=self.month, amount=amount, mode='CASH')

    def test_login_required(self):
        for url in ['/', '/flats/', '/charges/', '/expenses/']:
            self.assertEqual(self.client.get(url).status_code, 302)

    def test_pages_render_and_invalid_month_is_rejected(self):
        self.client.force_login(self.user)
        generate_charges(self.month)
        charge = MonthlyCharge.objects.get()
        for url in ['/', '/flats/', '/charges/?month=2026-11', '/expenses/', f'/charges/{charge.pk}/pay/']:
            self.assertEqual(self.client.get(url).status_code, 200)
        self.assertEqual(self.client.get('/?month=invalid').status_code, 400)

    def test_dashboard_separates_receipt_month_from_charge_month(self):
        generate_charges(self.month)
        receive_payment(MonthlyCharge.objects.get().pk, date=date(2026, 12, 5), amount=Decimal('1000'), mode='BANK')
        Expense.objects.create(date=self.month, category='Cleaning', description='Cleaning', amount=Decimal('300'), mode='CASH')
        self.client.force_login(self.user)
        response = self.client.get('/?month=2026-11')
        self.assertEqual(response.context['received'], Decimal('0'))
        self.assertEqual(response.context['spent'], Decimal('300'))
        self.assertEqual(response.context['outstanding'], Decimal('1000'))
