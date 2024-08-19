from rest_framework import serializers
from .models import *


class ContactMessageSerializers(serializers.ModelSerializer):
    text = serializers.CharField(required=False)

    class Meta:
        model = ContactMessage
        fields = ['id', 'object', 'text', 'email']
