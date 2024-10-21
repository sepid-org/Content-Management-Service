from ast import Attribute
from rest_polymorphic.serializers import PolymorphicSerializer

from apps.attributes.models.base import IntrinsicAttribute, PerformableAction
from apps.attributes.models.performable_actions import Transition
from apps.attributes.serializers.base import AttributeSerializer, IntrinsicAttributeSerializer, PerformableActionSerializer, TransitionSerializer


class PolymorphicAttributeSerializer(PolymorphicSerializer):
    """
    Polymorphic serializer that can handle all attribute types.
    Use this serializer when you need to work with mixed attribute types.
    """
    model_serializer_mapping = {
        IntrinsicAttribute: IntrinsicAttributeSerializer,
        PerformableAction: PerformableActionSerializer,
        Transition: TransitionSerializer,
        Attribute: AttributeSerializer,
    }

    class Meta:
        model = Attribute
        fields = '__all__'
