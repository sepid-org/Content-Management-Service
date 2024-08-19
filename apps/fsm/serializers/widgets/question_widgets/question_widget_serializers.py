from django.db import transaction
from rest_framework.exceptions import ParseError
from apps.fsm.serializers.widgets.widget_serializer import WidgetSerializer
from errors.error_codes import serialize_error

from apps.fsm.models import SmallAnswerProblem, MultiChoiceProblem, Choice, UploadFileProblem, BigAnswerProblem, Widget
from apps.response.serializers.answers.answer_serializers import SmallAnswerSerializer, ChoiceSerializer, UploadFileAnswerSerializer


class QuestionWidgetSerializer(WidgetSerializer):
    class Meta(WidgetSerializer.Meta):
        fields = WidgetSerializer.Meta.fields + \
            ['text', 'is_required', 'solution']
        read_only_fields = WidgetSerializer.Meta.read_only_fields + []


class SmallAnswerProblemSerializer(QuestionWidgetSerializer):
    correct_answer = SmallAnswerSerializer(required=False)

    class Meta(QuestionWidgetSerializer.Meta):
        model = SmallAnswerProblem
        fields = QuestionWidgetSerializer.Meta.fields + ['correct_answer']

    @transaction.atomic
    def create(self, validated_data):
        has_answer = 'correct_answer' in validated_data.keys()
        if has_answer:
            answer = validated_data.pop('correct_answer')
        instance = super().create(
            {'widget_type': Widget.WidgetTypes.SmallAnswerProblem, **validated_data})
        if has_answer:
            serializer = SmallAnswerSerializer(data={'problem': instance,
                                                     'is_final_answer': True,
                                                     'is_correct': True,
                                                     **answer})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        has_answer = 'correct_answer' in validated_data.keys()
        if has_answer:
            answer = validated_data.pop('correct_answer')
        instance = super().update(instance, {**validated_data})
        if has_answer:
            answer_object = instance.correct_answer
            if answer_object:
                answer_object.text = answer['text']
                answer_object.save()
            else:
                serializer = SmallAnswerSerializer(
                    data={'problem': instance, 'is_final_answer': True, 'is_correct': True, **answer})
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user = self.context.get('user')
        if hasattr(instance.paper, 'fsm') and user and not user in instance.paper.fsm.mentors.all():
            del representation['correct_answer']
        return representation


class BigAnswerProblemSerializer(QuestionWidgetSerializer):

    class Meta(QuestionWidgetSerializer.Meta):
        model = BigAnswerProblem
        fields = QuestionWidgetSerializer.Meta.fields + []

    @transaction.atomic
    def create(self, validated_data):
        instance = super().create(
            {'widget_type': Widget.WidgetTypes.BigAnswerProblem, **validated_data})
        return instance


class MultiChoiceProblemSerializer(QuestionWidgetSerializer):
    choices = ChoiceSerializer(many=True)

    class Meta(QuestionWidgetSerializer.Meta):
        model = MultiChoiceProblem
        fields = QuestionWidgetSerializer.Meta.fields + \
            ['maximum_choices_could_be_chosen', 'choices']

    def create(self, validated_data):
        choices_data = validated_data.pop('choices')
        multi_choice_question_instance = super().create(
            {'widget_type': Widget.WidgetTypes.MultiChoiceProblem, **validated_data})
        choices_instances = [Choice.create_instance(multi_choice_question_instance, choice_data)
                             for choice_data in choices_data]
        multi_choice_question_instance.choices.add(*choices_instances)
        return multi_choice_question_instance

    def update(self, question_instance, validated_data):
        choices_data = validated_data.pop('choices')

        # remove deleted choices
        for choice in question_instance.choices.all():
            is_there = False
            for choice_data in choices_data:
                if choice_data['id'] == choice.id:
                    is_there = True
            if not is_there:
                choice.delete()

        for choice_data in choices_data:
            if question_instance.choices and question_instance.choices.filter(id=choice_data.get('id')):
                # update changed choices
                choice_instance = question_instance.choices.get(
                    id=choice_data.get('id'))
                for attr, value in choice_data.items():
                    setattr(choice_instance, attr, value)
                choice_instance.save()
            else:
                # create new choices
                choice_instance = Choice.create_instance(
                    question_instance, choice_data)
                question_instance.choices.add(choice_instance)

        # update question self
        for attr, value in validated_data.items():
            setattr(question_instance, attr, value)

        question_instance.save()
        return question_instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user = self.context.get('user')
        if hasattr(instance.paper, 'fsm') and user and not user in instance.paper.fsm.mentors.all():
            for choice in representation['choices']:
                del choice['is_correct']
        return representation


class UploadFileProblemSerializer(WidgetSerializer):

    class Meta(QuestionWidgetSerializer.Meta):
        model = UploadFileProblem
        fields = QuestionWidgetSerializer.Meta.fields + []

    def validate_answer(self, answer):
        if answer.problem is not None:
            raise ParseError(serialize_error('4047'))
        elif answer.submitted_by != self.context.get('user', None):
            raise ParseError(serialize_error('4048'))
        return answer

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.correct_answer and not instance.paper.is_exam:
            representation['correct_answer'] = UploadFileAnswerSerializer(
            ).to_representation(instance.correct_answer)
        return representation

    @transaction.atomic
    def create(self, validated_data):
        instance = super().create(
            {'widget_type': Widget.WidgetTypes.UploadFileProblem, **validated_data})
        return instance
