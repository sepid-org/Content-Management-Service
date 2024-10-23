from rest_framework import serializers

from apps.attributes.models.base import Attribute, IntrinsicAttribute, PerformableAction


class AttributeSerializer(serializers.ModelSerializer):
    """Base serializer for all attributes."""
    attributes = serializers.SerializerMethodField()

    def get_attributes(self, obj):
        from apps.attributes.serializers.polymorphic_attribute_serializer import AttributePolymorphicSerializer
        return AttributePolymorphicSerializer(obj.attributes, many=True).data

    class Meta:
        model = Attribute
        fields = ['id', 'title', 'description', 'order', 'attributes']
        read_only_fields = ['id', 'attributes']


class IntrinsicAttributeSerializer(AttributeSerializer):
    """Serializer for IntrinsicAttribute model."""

    class Meta:
        model = IntrinsicAttribute
        fields = AttributeSerializer.Meta.fields + ['value']
        read_only_fields = AttributeSerializer.Meta.read_only_fields + []


class PerformableActionSerializer(AttributeSerializer):
    """Serializer for PerformableAction model."""

    class Meta:
        model = PerformableAction
        fields = AttributeSerializer.Meta.fields + []
        read_only_fields = AttributeSerializer.Meta.read_only_fields + []
