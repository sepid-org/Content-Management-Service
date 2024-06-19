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
from apps.fsm.serializers.widget_polymorphic import WidgetPolymorphicSerializer
from apps.scoring.views.apply_scores_on_user import apply_cost, apply_reward
from proxies.assess_answer_service.main import assess_answer


class AnswerViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes([MultiPartParser])
    queryset = Widget.objects.all()
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
        context.update({'editable': True})
        context.update(
            {'domain': self.request.build_absolute_uri('/api/')[:-5]})
        return context

    @swagger_auto_schema(responses={200: MockAnswerSerializer}, tags=['answers'])
    @action(detail=True, methods=['post'], serializer_class=AnswerPolymorphicSerializer,
            permission_classes=[CanAnswerWidget])
    @transaction.atomic
    def submit_answer(self, request, *args, **kwargs):
        # check if user has already answered this question correctly
        question = self.get_object()
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
        comment = ''
        if question.be_corrected:
            apply_cost(
                question.cost, request.user, 'کسر هزینه بابت تصحیح پاسخ', f'بابت تصحیح پاسخ سوال {question.id} از شما امتیاز کسر شد')

            correctness_percentage, comment = assess_answer(
                self.get_object(), given_answer_object)

            if correctness_percentage == 100:
                given_answer_object.is_correct = True
                given_answer_object.save()
                apply_reward(
                    given_answer_object.problem.reward, request.user, 'پاداش حل سوال', f'بابت حل سوال {question.id} به شما امتیاز اضافه شد')

            return Response(data={'correctness_percentage': correctness_percentage, 'comment': comment})

        return Response()

    @swagger_auto_schema(tags=['answers'])
    @transaction.atomic
    @action(detail=True, methods=['get'], permission_classes=[CanAnswerWidget, ])
    def clear_widget_answer(self, request, *args, **kwargs):
        self.get_object().unfinalize_older_answers(request.user)
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=['answers'])
    @transaction.atomic
    @action(detail=True, methods=['get'], permission_classes=[CanAnswerWidget, ])
    def answers(self, request, *args, **kwargs):
        teammates = Team.objects.get_teammates_from_widget(
            user=request.user, widget=self.get_object())
        older_answers = PROBLEM_ANSWER_MAPPING[self.get_object().widget_type].objects.filter(problem=self.get_object(),
                                                                                             submitted_by__in=teammates)
        return Response(data=AnswerPolymorphicSerializer(older_answers, many=True).data, status=status.HTTP_200_OK)
