from rest_framework import serializers

from apps.engagement.models import ContentLog


class ContentLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentLog
        fields = '__all__'
