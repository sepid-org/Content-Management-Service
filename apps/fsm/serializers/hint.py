from apps.fsm.models.base import GeneralHint
from apps.fsm.serializers.object_serializer import ObjectSerializer, TreasuryObjectSerializer


class PublicGeneralHintSerializer(TreasuryObjectSerializer):
    class Meta(ObjectSerializer.Meta):
        model = GeneralHint
        fields = ObjectSerializer.Meta.fields + []
        read_only_fields = ObjectSerializer.Meta.read_only_fields


class DetailedGeneralHintSerializer(ObjectSerializer):
    class Meta(ObjectSerializer.Meta):
        model = GeneralHint
        fields = ObjectSerializer.Meta.fields + ['hint_content']
        read_only_fields = ObjectSerializer.Meta.read_only_fields
