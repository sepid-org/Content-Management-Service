from rest_polymorphic.serializers import PolymorphicSerializer

from apps.fsm.serializers.papers.article_serializer import ArticleSerializer
from apps.fsm.serializers.papers.hint_serializer import HintSerializer
from apps.fsm.serializers.papers.paper_serializer import PaperSerializer
from apps.widgets.serializers.widget_hint_serializer import WidgetHintSerializer


class PaperPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        'General': PaperSerializer,
        'Article': ArticleSerializer,
        'Hint': HintSerializer,
        'WidgetHint': WidgetHintSerializer,
    }

    resource_type_field_name = 'paper_type'
