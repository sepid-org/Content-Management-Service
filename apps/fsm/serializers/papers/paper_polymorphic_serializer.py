from rest_polymorphic.serializers import PolymorphicSerializer

from apps.fsm.serializers.papers.paper_serializers import ArticleSerializer, HintSerializer, PaperSerializer, RegistrationFormSerializer, StateSerializer
from apps.widgets.serializers.widget_hint_serializers import WidgetHintSerializer


class PaperPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        'Paper': PaperSerializer,
        'RegistrationForm': RegistrationFormSerializer,
        'Article': ArticleSerializer,
        'State': StateSerializer,
        'Hint': HintSerializer,
        'WidgetHint': WidgetHintSerializer,
    }

    resource_type_field_name = 'paper_type'
