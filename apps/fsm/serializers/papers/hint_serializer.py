from apps.fsm.serializers.papers.paper_serializer import PaperSerializer
from apps.fsm.models import Hint


class HintSerializer(PaperSerializer):

    class Meta(PaperSerializer.Meta):
        model = Hint
        ref_name = 'hint'
        fields = PaperSerializer.Meta.get_fields() + ['reference']
        read_only_fields = PaperSerializer.Meta.read_only_fields + []
