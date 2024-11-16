from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from django.db import transaction

from apps.attributes.models.performable_actions import Answer
from apps.fsm.models.base import Widget
from apps.fsm.models.fsm import Player
from apps.fsm.models.question_widgets import PROBLEM_ANSWER_MAPPING
from apps.fsm.models.team import Team
from apps.response.serializers.answers.mock_answer_serializer import MockAnswerSerializer
from apps.response.utils import AnswerFacade
from apps.response.serializers.answers.answer_polymorphic_serializer import AnswerPolymorphicSerializer


def get_question(question_id: int):
    return Widget.objects.get(id=question_id)


class AnswerViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Answer.objects.all()
    serializer_class = AnswerPolymorphicSerializer
    my_tags = ['answers']

    @swagger_auto_schema(responses={200: MockAnswerSerializer}, tags=['answers'])
    @action(detail=False, methods=['post'], url_path='submit-answer')
    @transaction.atomic
    def submit_answer(self, request, *args, **kwargs):
        question = get_question(request.data.get("question"))
        player_id = request.data.get("player_id")
        player = None
        if player_id:
            player = get_object_or_404(Player, id=player_id)
        user = request.user

        facade = AnswerFacade()
        facade.submit_answer(
            user=user,
            player=player,
            provided_answer=request.data,
            question=question,
        )

        from apps.attributes.utils import perform_posterior_actions
        perform_posterior_actions(
            attributes=question.attributes,
            player=player,
            user=user,
            request=request,
        )

        return Response(status=status.HTTP_202_ACCEPTED)

    @swagger_auto_schema(tags=['answers'])
    @transaction.atomic
    @action(detail=False, methods=['post'])
    def clear_question_answer(self, request, *args, **kwargs):
        question = get_question(request.data.get("question_id"))
        question.unfinalize_user_previous_answers(request.user)
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=['answers'])
    @transaction.atomic
    @action(detail=True, methods=['get'])
    def answers(self, request, *args, **kwargs):
        question = get_question(request.data.get("question_id"))
        teammates = Team.objects.get_teammates_from_widget(
            user=request.user, widget=question)
        older_answers = PROBLEM_ANSWER_MAPPING[question.widget_type].objects.filter(
            problem=question, submitted_by__in=teammates)
        return Response(
            data=self.get_serializer(older_answers, many=True).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=['get'])
    def question_answers(self, request, *args, **kwargs):
        question_id = request.GET.get('widget')
        question = get_question(question_id=question_id)
        # todo
        return Response()
