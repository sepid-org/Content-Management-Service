from apps.fsm.models.base import GeneralHint
from apps.fsm.serializers.object_serializer import ObjectSerializer, TreasuryObjectSerializer


class PublicGeneralHintSerializer(TreasuryObjectSerializer):
    class Meta(TreasuryObjectSerializer.Meta):
        model = GeneralHint
        fields = TreasuryObjectSerializer.Meta.fields + ['id']
        read_only_fields = TreasuryObjectSerializer.Meta.read_only_fields + \
            ['id']


class DetailedGeneralHintSerializer(ObjectSerializer):
    class Meta(ObjectSerializer.Meta):
        model = GeneralHint
        fields = ObjectSerializer.Meta.fields + ['id', 'hint_content']
        read_only_fields = ObjectSerializer.Meta.read_only_fields + ['id']
