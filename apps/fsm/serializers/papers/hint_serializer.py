from apps.fsm.serializers.papers.paper_serializer import PaperSerializer
from apps.fsm.models import Hint


class HintSerializer(PaperSerializer):

    class Meta(PaperSerializer.Meta):
        model = Hint
        fields = [field for field in PaperSerializer.Meta.fields if field != 'widgets'] +\
            ['reference']
        read_only_fields = PaperSerializer.Meta.read_only_fields + []
