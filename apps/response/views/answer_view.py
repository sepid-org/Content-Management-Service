from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action, parser_classes
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.parsers import MultiPartParser
from django.db import transaction
from rest_framework.exceptions import ParseError

from errors.error_codes import serialize_error
from apps.fsm.models import *
from apps.fsm.permissions import CanAnswerWidget
from apps.fsm.serializers.answer_serializers import AnswerPolymorphicSerializer, MockAnswerSerializer
from apps.fsm.serializers.widgets.widget_polymorphic import WidgetPolymorphicSerializer
from apps.scoring.views.apply_scores_on_user import apply_cost, apply_reward
from proxies.assess_answer_service.main import assess_answer


def get_question(question_id: int):
    return Widget.objects.get(id=question_id)


class AnswerViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes([MultiPartParser])
    queryset = Answer.objects.all()
    serializer_class = WidgetPolymorphicSerializer
    my_tags = ['answers']

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()

    def get_permissions(self):
        permission_classes = [CanAnswerWidget]
        return [permission() for permission in permission_classes]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        context.update(
            {'domain': self.request.build_absolute_uri('/api/')[:-5]})
        return context

    @swagger_auto_schema(responses={200: MockAnswerSerializer}, tags=['answers'])
    @action(detail=False, methods=['post'], serializer_class=AnswerPolymorphicSerializer,
            permission_classes=[CanAnswerWidget])
    @transaction.atomic
    def submit_answer(self, request, *args, **kwargs):
        # check if user has already answered this question correctly
        question = get_question(request.data.get("question_id"))
        user = request.user
        if question.correct_answer:
            user_correctly_answered_problems = Answer.objects.filter(
                submitted_by=user, is_correct=True)
            for answer in user_correctly_answered_problems:
                if answer.problem == question:
                    raise ParseError(serialize_error('6000'))

        given_answer_data = {
            'is_final_answer': True,
            'problem': question.id,
            **request.data
        }
        serializer = AnswerPolymorphicSerializer(
            data=given_answer_data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        given_answer_object = serializer.save()

        correctness_percentage = -1
        comment = 'not assessed'
        if question.correct_answer:
            apply_cost(
                question.cost, request.user, 'کسر هزینه بابت تصحیح پاسخ', f'بابت تصحیح پاسخ سوال {question.id} از شما امتیاز کسر شد')

            correctness_percentage, comment = assess_answer(
                question=question, given_answer=given_answer_object)

            if correctness_percentage == 100:
                given_answer_object.is_correct = True
                given_answer_object.save()
                apply_reward(
                    given_answer_object.problem.reward, request.user, 'پاداش حل سوال', f'بابت حل سوال {question.id} به شما امتیاز اضافه شد')

            return Response(data={'correctness_percentage': correctness_percentage, 'comment': comment})

        return Response()

    @swagger_auto_schema(tags=['answers'])
    @transaction.atomic
    @action(detail=False, methods=['post'], permission_classes=[CanAnswerWidget, ])
    def clear_question_answer(self, request, *args, **kwargs):
        question = get_question(request.data.get("question_id"))
        question.unfinalize_older_answers(request.user)
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=['answers'])
    @transaction.atomic
    @action(detail=True, methods=['get'], permission_classes=[CanAnswerWidget, ])
    def answers(self, request, *args, **kwargs):
        question = get_question(request.data.get("question_id"))
        teammates = Team.objects.get_teammates_from_widget(
            user=request.user, widget=question)
        older_answers = PROBLEM_ANSWER_MAPPING[question.widget_type].objects.filter(
            problem=question, submitted_by__in=teammates)
        return Response(data=AnswerPolymorphicSerializer(older_answers, many=True).data, status=status.HTTP_200_OK)

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
        return Response(AnswerPolymorphicSerializer(answers, many=True).data)
