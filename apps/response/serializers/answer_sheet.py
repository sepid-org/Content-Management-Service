from rest_framework import serializers
from rest_framework.exceptions import ParseError

from apps.accounts.models import User
from errors.error_codes import serialize_error
from apps.fsm.models import AnswerSheet, Problem
from apps.response.serializers.answers.answer_polymorphic_serializer import AnswerPolymorphicSerializer


class AnswerSheetSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    def create(self, validated_data):
        answers = self.initial_data.get('answers', [])
        answer_sheet = super().create(validated_data)

        for answer in answers:
            serializer = AnswerPolymorphicSerializer(data={
                'answer_sheet': answer_sheet.id,
                **answer
            })
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return answer_sheet

    def validate(self, attrs):
        answers = self.initial_data.get('answers', [])
        problems = [answer.get('problem', None) for answer in answers]
        paper = self.context.get('form', None)
        if paper is not None:
            for widget in paper.widgets.all():
                if isinstance(widget, Problem) and widget.is_required and widget.id not in problems:
                    raise ParseError(serialize_error(
                        '4029', {'problem': widget}))
        return attrs

    class Meta:
        model = AnswerSheet
        fields = ['id', 'answer_sheet_type', 'user']
        read_only_fields = ['id', 'answer_sheet_type']