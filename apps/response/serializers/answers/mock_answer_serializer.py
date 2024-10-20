from apps.response.serializers.answers.answer_serializers import SmallAnswerSerializer, BigAnswerSerializer, MultiChoiceAnswerSerializer, UploadFileAnswerSerializer
from rest_framework import serializers


class MockAnswerSerializer(serializers.Serializer):
    SmallAnswerSerializer = SmallAnswerSerializer(required=False)
    BigAnswerSerializer = BigAnswerSerializer(required=False)
    MultiChoiceAnswerSerializer = MultiChoiceAnswerSerializer(required=False)
    UploadFileAnswerSerializer = UploadFileAnswerSerializer(required=False)
