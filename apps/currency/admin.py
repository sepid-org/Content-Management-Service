from django.contrib import admin

from apps.currency.models import Spend


@admin.register(Spend)
class SpendAdmin(admin.ModelAdmin):
    list_display = ('user', 'object', 'fund', 'spent_at', 'transaction_id')
    search_fields = ('user', 'object__name', 'transaction_id')
    list_filter = ('spent_at',)
    readonly_fields = ('spent_at',)
