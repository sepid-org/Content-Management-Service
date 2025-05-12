from rest_framework.routers import DefaultRouter

from apps.sale.views.payment_view import PaymentViewSet
from apps.sale.views.merchandise_view import MerchandiseViewSet
from apps.sale.views.discount_code_view import DiscountCodeViewSet

router = DefaultRouter()

urlpatterns = []

router.register(r'payment', PaymentViewSet, basename='payment')
router.register(r'discount_code', DiscountCodeViewSet,
                basename='discount_codes')
router.register(r'merchandise', MerchandiseViewSet, basename='merchandises')

urlpatterns += router.urls
