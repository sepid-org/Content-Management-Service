from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from django.db import transaction
from rest_framework.exceptions import ParseError

from apps.response.serializers.answers.mock_answer_serializer import MockAnswerSerializer
from errors.error_codes import serialize_error
from apps.fsm.models import *
from apps.response.serializers.answers.answer_polymorphic_serializer import AnswerPolymorphicSerializer


def get_question(question_id: int):
    return Widget.objects.get(id=question_id)


class AnswerViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Answer.objects.all()
    serializer_class = AnswerPolymorphicSerializer
    my_tags = ['answers']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            'user': self.request.user,
            'domain': self.request.build_absolute_uri('/api/')[:-5],
        })
        return context

    @swagger_auto_schema(responses={200: MockAnswerSerializer}, tags=['answers'])
    @action(detail=False, methods=['post'])
    @transaction.atomic
    def submit_answer(self, request, *args, **kwargs):
        question = get_question(request.data.get("question"))
        player_id = request.data.get("player")
        if player_id:
            player = get_object_or_404(Player, id=player_id)
        user = request.user

        # check if user has already answered this question correctly
        if question.correct_answer:
            user_correctly_answered_problems = Answer.objects.filter(
                submitted_by=user, is_correct=True)
            for answer in user_correctly_answered_problems:
                if answer.problem == question:
                    raise ParseError(serialize_error('6000'))

        # create submitted answer object
        answer_data = {
            'is_final_answer': True,
            'problem': question.id,
            **request.data
        }
        serializer = self.get_serializer(
            data=answer_data,
            context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        answer = serializer.save()

        # save answer in the player answer-sheet (if player exists):
        if player:
            answer_sheet = player.answer_sheet
            answer.answer_sheet = answer_sheet
            answer.save()

        # perform posterior actions
        for attribute in question.attributes.all():
            from apps.attributes.models import PerformableAction
            if isinstance(attribute, PerformableAction):
                attribute.perform(
                    player=player,
                    request=request,
                )

        return Response(status=status.HTTP_202_ACCEPTED)

    @swagger_auto_schema(tags=['answers'])
    @transaction.atomic
    @action(detail=False, methods=['post'])
    def clear_question_answer(self, request, *args, **kwargs):
        question = get_question(request.data.get("question_id"))
        question.unfinalize_older_answers(request.user)
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

    @action(detail=False, methods=['get'])
    def answer_sheet_answers(self, request, *args, **kwargs):
        answer_sheet_id = request.GET.get('answer_sheet')
        answer_sheet = AnswerSheet.objects.get(id=answer_sheet_id)
        answers = answer_sheet.answers
        return Response(self.get_serializer(answers, many=True).data)
