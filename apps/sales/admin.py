
from django.contrib import admin
from apps.accounts.models import Purchase, DiscountCode, Merchandise, Voucher


@admin.register(Merchandise)
class MerchandiseCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'program',
                    'price', 'discounted_price', 'is_active', 'is_deleted']
    list_filter = ['is_active', 'program']


@admin.register(Purchase)
class CustomPurchaseAdmin(admin.ModelAdmin):
    model = Purchase
    list_display = ['id', 'ref_id', 'amount',
                    'status', 'created_at', 'user', 'merchandise']
    search_fields = ['user__username']


admin.site.register(Voucher)
admin.site.register(DiscountCode)
