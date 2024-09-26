from rest_polymorphic.serializers import PolymorphicSerializer

from apps.fsm.serializers.papers.article_serializer import ArticleSerializer
from apps.fsm.serializers.papers.hint_serializer import HintSerializer
from apps.fsm.serializers.papers.paper_serializer import PaperSerializer
from apps.fsm.serializers.papers.registration_form_serializer import RegistrationFormSerializer
from apps.fsm.serializers.papers.state_serializer import StateSerializer
from apps.widgets.serializers.widget_hint_serializer import WidgetHintSerializer


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
