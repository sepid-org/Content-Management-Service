
from rest_framework import serializers

from apps.attributes.serializers.polymorphic_attribute_serializer import AttributePolymorphicSerializer
from apps.fsm.models import Object
from apps.fsm.models.base import Position
from apps.fsm.serializers.position_serializer import PositionSerializer


class ObjectSerializer(serializers.ModelSerializer):
    position = serializers.SerializerMethodField(
        required=False, read_only=True)

    def get_position(self, obj):
        if not hasattr(obj, 'position'):
            Position.objects.create(
                object=obj,
                x=0,  # Default x position
                y=0,  # Default y position
                width=300,  # Default width
                height=200  # Default height
            )
        return PositionSerializer(obj.position).data

    class Meta:
        model = Object
        fields = ['name', 'title', 'created_at', 'updated_at',
                  'attributes', 'order', 'is_private', 'position', 'is_hidden', 'website']
        read_only_fields = ['created_at', 'attributes', 'position']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['object_id'] = instance.id

        user = self.context.get('request').user

        permitted_attributes = []
        for attribute in instance.attributes.all():
            if attribute.is_permitted(user):
                permitted_attributes.append(attribute)

        representation['attributes'] = AttributePolymorphicSerializer(
            instance.attributes.all(), many=True).data
        representation['permitted_attributes'] = AttributePolymorphicSerializer(
            permitted_attributes, many=True).data

        return representation
