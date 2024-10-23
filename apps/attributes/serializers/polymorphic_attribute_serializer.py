from rest_polymorphic.serializers import PolymorphicSerializer

from apps.attributes.models import *
from apps.attributes.serializers.base import AttributeSerializer, IntrinsicAttributeSerializer, PerformableActionSerializer
from apps.attributes.serializers.intrinsic_attributes import *
from apps.attributes.serializers.performable_actions import *


class AttributePolymorphicSerializer(PolymorphicSerializer):
    """
    Polymorphic serializer that can handle all attribute types.
    Use this serializer when you need to work with mixed attribute types.
    """
    model_serializer_mapping = {
        Attribute: AttributeSerializer,
        # intrinsic
        IntrinsicAttribute: IntrinsicAttributeSerializer,
        Cost: CostSerializer,
        Reward: RewardSerializer,
        Condition: ConditionSerializer,
        Enabled: EnabledSerializer,
        # actions
        PerformableAction: PerformableActionSerializer,
        Transition: TransitionSerializer,
        Buy: BuySerializer,
        Submission: SubmissionSerializer,
    }

    resource_type_field_name = 'type'

    class Meta:
        model = Attribute
        fields = '__all__'
