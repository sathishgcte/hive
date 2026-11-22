from django.contrib import admin
from .models import Flat, MonthlyCharge, Payment, Expense

admin.site.register(Flat)

class LedgerAdmin(admin.ModelAdmin):
    # Use application workflows for writes so ledger checks cannot be bypassed.
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(MonthlyCharge, LedgerAdmin)
admin.site.register(Payment, LedgerAdmin)
admin.site.register(Expense, LedgerAdmin)
