from ast import Attribute
from rest_framework import serializers

from apps.attributes.models.base import IntrinsicAttribute, PerformableAction


class AttributeSerializer(serializers.ModelSerializer):
    """Base serializer for all attributes."""
    attributes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    model_type = serializers.SerializerMethodField()

    class Meta:
        model = Attribute
        fields = ['id', 'title', 'description',
                  'order', 'attributes', 'model_type']
        read_only_fields = ['id', 'model_type']

    def get_model_type(self, obj):
        return obj.__class__.__name__


class IntrinsicAttributeSerializer(AttributeSerializer):
    """Serializer for IntrinsicAttribute model."""

    class Meta:
        model = IntrinsicAttribute
        fields = AttributeSerializer.Meta.fields + ['value']
        read_only_fields = AttributeSerializer.Meta.read_only_fields


class PerformableActionSerializer(AttributeSerializer):
    """Serializer for PerformableAction model."""

    class Meta:
        model = PerformableAction
        fields = AttributeSerializer.Meta.fields
        read_only_fields = AttributeSerializer.Meta.read_only_fields
