from rest_framework import serializers


class SpendSerializer(serializers.Serializer):
    object_id = serializers.CharField()
    funds = serializers.DictField(
        child=serializers.IntegerField(min_value=1)
    )
