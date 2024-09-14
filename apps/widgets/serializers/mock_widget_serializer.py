from rest_framework import serializers

from apps.widgets.serializers.content_widgets.content_widget_serializers\
    import TextWidgetSerializer, ImageSerializer, VideoSerializer, AparatSerializer, \
    IframeSerializer
from apps.widgets.serializers.question_widgets.question_widget_serializers \
    import SmallAnswerProblemSerializer, BigAnswerProblemSerializer, MultiChoiceProblemSerializer, UploadFileProblemSerializer


class MockWidgetSerializer(serializers.Serializer):
    IframeSerializer = IframeSerializer(required=False)
    VideoSerializer = VideoSerializer(required=False)
    AparatSerializer = AparatSerializer(required=False)
    ImageSerializer = ImageSerializer(required=False)
    TextSerializer = TextWidgetSerializer(required=False)
    SmallAnswerProblemSerializer = SmallAnswerProblemSerializer(required=False)
    BigAnswerProblemSerializer = BigAnswerProblemSerializer(required=False)
    MultiChoiceProblemSerializer = MultiChoiceProblemSerializer(required=False)
    UploadFileProblemSerializer = UploadFileProblemSerializer(required=False)
