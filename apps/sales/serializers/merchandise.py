from rest_framework import serializers

from apps.accounts.models import Merchandise
from apps.sales.validators import price_validator


class MerchandiseSerializer(serializers.ModelSerializer):
    price = serializers.IntegerField(
        required=True, validators=[price_validator])
    discounted_price = serializers.IntegerField(
        required=False, validators=[price_validator], allow_null=True)

    class Meta:
        model = Merchandise
        fields = ['id', 'name', 'price', 'discounted_price', 'is_active', 'program', 'is_deleted']
        read_only_fields = ['id']
