
from rest_framework import serializers

from apps.fsm.models import Object


class ObjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Object
        fields = ['title', 'created_at', 'updated_at', 'attributes']
        read_only_fields = ['created_at', 'updated_at', 'attributes']
