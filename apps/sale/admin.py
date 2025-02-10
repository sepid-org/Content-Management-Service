
from django.contrib import admin
from apps.accounts.models import Purchase, DiscountCode, Merchandise, Voucher


@admin.register(Merchandise)
class MerchandiseCustomAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'program',
                    'price', 'discounted_price', 'is_active', 'is_deleted']
    list_filter = ['is_active', 'program']
    search_fields = ['name']


@admin.register(Purchase)
class CustomPurchaseAdmin(admin.ModelAdmin):
    list_display = ['id', 'ref_id', 'amount',
                    'status', 'created_at', 'user', 'merchandise']
    search_fields = ['ref_id', 'user__username']
    list_filter = ['merchandise']
    autocomplete_fields = ['user', 'merchandise', 'voucher', 'discount_code']


@admin.register(Voucher)
class CustomVoucherAdmin(admin.ModelAdmin):
    search_fields = ['code']


@admin.register(DiscountCode)
class CustomDiscountCodeAdmin(admin.ModelAdmin):
    search_fields = ['code']
