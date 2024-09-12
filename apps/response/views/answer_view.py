from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action, parser_classes
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.parsers import MultiPartParser
from django.db import transaction
from rest_framework.exceptions import ParseError

from apps.response.serializers.answers.mock_answer_serializer import MockAnswerSerializer
from errors.error_codes import serialize_error
from apps.fsm.models import *
from apps.fsm.permissions import CanAnswerWidget
from apps.response.serializers.answers.answer_polymorphic_serializer import AnswerPolymorphicSerializer
from apps.fsm.serializers.widgets.widget_polymorphic_serializer import WidgetPolymorphicSerializer
from proxies.assess_answer_service.main import assess_answer
from proxies.bank_service.main import BankProxy
from proxies.instant_messaging_service.main import InstantMessagingServiceProxy


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
    @action(detail=False, methods=['post'], serializer_class=AnswerPolymorphicSerializer, permission_classes=[CanAnswerWidget])
    @transaction.atomic
    def submit_answer(self, request, *args, **kwargs):
        question = get_question(request.data.get("question"))
        user = request.user

        # check if user has already answered this question correctly
        if question.correct_answer:
            user_correctly_answered_problems = Answer.objects.filter(
                submitted_by=user, is_correct=True)
            for answer in user_correctly_answered_problems:
                if answer.problem == question:
                    raise ParseError(serialize_error('6000'))

        # withdraw the submission cost from user wallet
        _apply_submission_answer_cost(
            user=user, question=question, website=request.headers.get('Website'))

        # create submitted answer object
        given_answer_data = {
            'is_final_answer': True,
            'problem': question.id,
            **request.data
        }
        serializer = AnswerPolymorphicSerializer(
            data=given_answer_data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        given_answer_object = serializer.save()

        # assess the answer (is any correct answer is provided)
        # if question.correct_answer:
        #     score, feedback, improvement_suggestion = assess_answer(
        #         question=question, given_answer=given_answer_object)
        #     if score >= question.correctness_threshold:
        #         given_answer_object.is_correct = True
        #         given_answer_object.save()
        #         _apply_solve_question_reward(
        #             user=user, question=question, website=request.headers.get('Website'))
        #     return Response(data={'score': score, 'feedback': feedback, 'improvement_suggestion': improvement_suggestion})

        return Response(status=status.HTTP_202_ACCEPTED)

    @swagger_auto_schema(tags=['answers'])
    @transaction.atomic
    @action(detail=False, methods=['post'], permission_classes=[CanAnswerWidget])
    def clear_question_answer(self, request, *args, **kwargs):
        question = get_question(request.data.get("question_id"))
        question.unfinalize_older_answers(request.user)
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=['answers'])
    @transaction.atomic
    @action(detail=True, methods=['get'], permission_classes=[CanAnswerWidget])
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


def _apply_submission_answer_cost(user, question, website):
    if question.submission_cost:
        bank_proxy = BankProxy(website=website)
        bank_proxy.withdraw(user=user, money=question.submission_cost)
        notification_proxy = InstantMessagingServiceProxy(website=website)
        notification_proxy.send_submit_answer_cost_notification(
            recipient=user, question_id=question.id, cost=question.submission_cost)


def _apply_solve_question_reward(user, question, website):
    if question.solve_reward:
        bank_proxy = BankProxy(website=website)
        bank_proxy.deposit(user=user, money=question.solve_reward)
        notification_proxy = InstantMessagingServiceProxy(
            website=website)
        notification_proxy.send_solve_question_reward_notification(
            recipient=user, question_id=question.id, cost=question.solve_reward)
