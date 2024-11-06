from rest_framework import viewsets
from rest_framework import permissions

from apps.fsm.models.form import AnswerSheet
from apps.response.serializers.answer_sheet import AnswerSheetSerializer
from tkinter import Widget
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from django.db import transaction

from apps.attributes.models.performable_actions import Answer
from apps.fsm.models.fsm import Player
from apps.fsm.models.question_widgets import PROBLEM_ANSWER_MAPPING
from apps.fsm.models.team import Team
from apps.response.serializers.answers.mock_answer_serializer import MockAnswerSerializer
from apps.response.utils import AnswerFacade
from apps.response.serializers.answers.answer_polymorphic_serializer import AnswerPolymorphicSerializer


class AnswerSheetViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = AnswerSheet.objects.all()
    serializer_class = AnswerSheetSerializer
    my_tags = ['answer-sheets']

    @transaction.atomic
    @action(detail=False, methods=['get'], url_path='by-player')
    def by_paper(self, request, *args, **kwargs):
        player_id = request.GET.get('player_id')
        player = get_object_or_404(Player, id=player_id)
        return Response(
            data=self.get_serializer(player.answer_sheet).data,
            status=status.HTTP_200_OK,
        )
