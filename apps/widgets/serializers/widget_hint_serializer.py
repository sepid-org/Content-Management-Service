from apps.fsm.models import WidgetHint
from apps.fsm.serializers.papers.paper_serializer import PaperSerializer


class WidgetHintSerializer(PaperSerializer):

    class Meta(PaperSerializer.Meta):
        model = WidgetHint
        ref_name = 'hint'
        fields = PaperSerializer.Meta.fields + ['reference']
        read_only_fields = PaperSerializer.Meta.read_only_fields + []
