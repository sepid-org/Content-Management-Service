from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, ListModelMixin, UpdateModelMixin
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from apps.fsm.filtersets import AnswerFilterSet
from apps.fsm.models import Answer, UploadFileAnswer
from apps.fsm.permissions import IsAnswerModifier, MentorCorrectionPermission
from apps.response.serializers.answers.answer_polymorphic_serializer import AnswerPolymorphicSerializer
from apps.response.serializers.answers.answer_serializers import UploadFileAnswerSerializer


# todo: should be deleted:
class UploadAnswerViewSet(GenericViewSet, CreateModelMixin, RetrieveModelMixin):
    serializer_class = UploadFileAnswerSerializer
    parser_classes = [MultiPartParser]
    queryset = UploadFileAnswer.objects.all()
    my_tags = ['answers']
    permission_classes = [IsAuthenticated, ]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        return context
