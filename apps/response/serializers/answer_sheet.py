from rest_framework import serializers
from rest_framework.exceptions import ParseError

from apps.accounts.models import User
from apps.fsm.models.form import Form
from errors.error_codes import serialize_error
from apps.fsm.models import AnswerSheet, Problem
from apps.response.serializers.answers.answer_polymorphic_serializer import AnswerPolymorphicSerializer


class AnswerSheetSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), allow_null=True)
    form = serializers.PrimaryKeyRelatedField(
        queryset=Form.objects.all())

    def create(self, validated_data):
        answer_sheet = super().create(validated_data)

        answers = self.initial_data.get('answers', [])
        for answer in answers:
            # todo: use AnswerSubmissionHandler for submitting answers:
            serializer = AnswerPolymorphicSerializer(data={
                'submitted_by': validated_data.get('user').id if validated_data.get('user') else None,
                'answer_sheet': answer_sheet.id,
                **answer
            })
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return answer_sheet

    def validate(self, attrs):
        form = attrs.get('form', None)
        if form is not None:
            answers = self.initial_data.get('answers', [])
            answers_problems = [answer.get('problem', None)
                                for answer in answers]
            for widget in form.widgets.all():
                if isinstance(widget, Problem) and widget.is_required and widget.id not in answers_problems:
                    raise ParseError(serialize_error(
                        '4029', {'problem': widget}))
        return attrs

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        answers = instance.answers
        from apps.response.serializers.answers.answer_polymorphic_serializer import AnswerPolymorphicSerializer
        representation['answers'] = AnswerPolymorphicSerializer(
            answers, many=True).data
        return representation

    class Meta:
        model = AnswerSheet
        fields = ['id', 'answer_sheet_type', 'user',
                  'form', 'created_at', 'updated_at']
        read_only_fields = ['id', 'answer_sheet_type',
                            'created_at', 'updated_at']
