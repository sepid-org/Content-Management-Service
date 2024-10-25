from apps.fsm.models import WidgetHint
from apps.fsm.serializers.papers.paper_serializer import PaperSerializer


class WidgetHintSerializer(PaperSerializer):

    class Meta(PaperSerializer.Meta):
        model = WidgetHint
        fields = PaperSerializer.Meta.get_fields() + ['reference']
        read_only_fields = PaperSerializer.Meta.read_only_fields + []
