from apps.fsm.models.base import Resource
from apps.fsm.serializers.object_serializer import ObjectSerializer, TreasuryObjectSerializer


class PublicResourceSerializer(TreasuryObjectSerializer):
    class Meta(TreasuryObjectSerializer.Meta):
        model = Resource
        fields = TreasuryObjectSerializer.Meta.fields + ['id']
        read_only_fields = TreasuryObjectSerializer.Meta.read_only_fields + \
            ['id']


class ResourceSerializer(ObjectSerializer):
    class Meta(ObjectSerializer.Meta):
        model = Resource
        fields = ObjectSerializer.Meta.fields + ['id', 'type', 'content']
        read_only_fields = ObjectSerializer.Meta.read_only_fields + ['id']
