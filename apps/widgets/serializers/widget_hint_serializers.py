from django.db import transaction

from apps.fsm.serializers.papers.paper_serializers import PaperSerializer
from apps.fsm.models import WidgetHint


class WidgetHintSerializer(PaperSerializer):

    @transaction.atomic
    def create(self, validated_data):
        user = self.context.get('user', None)
        return super(WidgetHintSerializer, self).create({'paper_type': 'Widgethint', 'creator': user, **validated_data})

    class Meta(PaperSerializer.Meta):
        model = WidgetHint
        ref_name = 'hint'
        fields = PaperSerializer.Meta.fields + ['reference']
        read_only_fields = PaperSerializer.Meta.read_only_fields + []
