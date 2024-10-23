from apps.attributes.models import Condition, Funds, Enabled
from apps.attributes.serializers.base import IntrinsicAttributeSerializer


class ConditionSerializer(IntrinsicAttributeSerializer):

    class Meta(IntrinsicAttributeSerializer.Meta):
        model = Condition
        fields = IntrinsicAttributeSerializer.Meta.fields + []
        read_only_fields = IntrinsicAttributeSerializer.Meta.read_only_fields + []


class FundsSerializer(IntrinsicAttributeSerializer):

    class Meta(IntrinsicAttributeSerializer.Meta):
        model = Funds
        fields = IntrinsicAttributeSerializer.Meta.fields
        read_only_fields = IntrinsicAttributeSerializer.Meta.read_only_fields + []


class EnabledSerializer(IntrinsicAttributeSerializer):

    class Meta(IntrinsicAttributeSerializer.Meta):
        model = Enabled
        fields = IntrinsicAttributeSerializer.Meta.fields
        read_only_fields = IntrinsicAttributeSerializer.Meta.read_only_fields + []
