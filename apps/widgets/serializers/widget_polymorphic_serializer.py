from rest_polymorphic.serializers import PolymorphicSerializer

from apps.fsm.models import DetailBoxWidget, Iframe, Video, Image, TextWidget, SmallAnswerProblem, MultiChoiceProblem, UploadFileProblem, BigAnswerProblem, Aparat, Audio, Placeholder
from apps.widgets.models import ButtonWidget
from apps.widgets.models.other_widgets.random import RandomWidget
from apps.widgets.serializers.content_widgets.content_widget_serializers\
    import AudioSerializer, PlaceholderSerializer, DetailBoxWidgetSerializer, TextWidgetSerializer, ImageSerializer, VideoSerializer, AparatSerializer, \
    IframeSerializer
from apps.widgets.serializers.other_widgets.button_serializer import ButtonWidgetSerializer
from apps.widgets.serializers.other_widgets.random_widget_serializer import RandomWidgetSerializer
from apps.widgets.serializers.question_widgets.question_widget_serializers \
    import SmallAnswerProblemSerializer, BigAnswerProblemSerializer, MultiChoiceProblemSerializer, UploadFileProblemSerializer


class WidgetPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        # Widget
        TextWidget: TextWidgetSerializer,
        Image: ImageSerializer,
        Video: VideoSerializer,
        Audio: AudioSerializer,
        Aparat: AparatSerializer,
        Iframe: IframeSerializer,
        Placeholder: PlaceholderSerializer,
        DetailBoxWidget: DetailBoxWidgetSerializer,
        # Question,
        SmallAnswerProblem: SmallAnswerProblemSerializer,
        BigAnswerProblem: BigAnswerProblemSerializer,
        MultiChoiceProblem: MultiChoiceProblemSerializer,
        UploadFileProblem: UploadFileProblemSerializer,
        # Others
        ButtonWidget: ButtonWidgetSerializer,
        RandomWidget: RandomWidgetSerializer,
    }

    resource_type_field_name = 'widget_type'
