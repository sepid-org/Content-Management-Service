from django.contrib import admin
from .models import Spend


@admin.register(Spend)
class SpendAdmin(admin.ModelAdmin):
    list_display = ('user', 'object_id', 'fund', 'spent_at', 'transaction_id')
    search_fields = ('user', 'object_id', 'transaction_id')
    list_filter = ('spent_at',)
    ordering = ('-spent_at',)
