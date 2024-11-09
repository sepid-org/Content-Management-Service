from rest_framework import serializers

from apps.currency.models import Spend


class SpendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Spend
        fields = ['id', 'user', 'item_id',
                  'fund', 'spent_at', 'transaction_id']
        read_only_fields = ['id', 'spent_at', 'transaction_id']

    def validate_fund(self, value):
        # Optional: Add custom validation logic for 'fund' if needed
        if not value:
            raise serializers.ValidationError("Funds are required.")
        if not isinstance(value, dict):
            raise serializers.ValidationError("Funds must be a dictionary.")
        return value
