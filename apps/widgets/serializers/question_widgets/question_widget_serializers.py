from django.db import transaction
from apps.widgets.serializers.widget_serializer import WidgetSerializer

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
        validated_data['widget_type'] = Widget.WidgetTypes.SmallAnswerProblem
        instance = super().create(validated_data)
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


class BigAnswerProblemSerializer(QuestionWidgetSerializer):

    class Meta(QuestionWidgetSerializer.Meta):
        model = BigAnswerProblem
        fields = QuestionWidgetSerializer.Meta.fields + []

    @transaction.atomic
    def create(self, validated_data):
        validated_data['widget_type'] = Widget.WidgetTypes.BigAnswerProblem
        instance = super().create(validated_data)
        return instance


def get_active_player(fsm_id, user_id):
    from apps.fsm.models import Player
    return Player.objects.filter(user__id=user_id, fsm__id=fsm_id, finished_at__isnull=True).last()


class MultiChoiceProblemSerializer(QuestionWidgetSerializer):
    choices = ChoiceSerializer(many=True)

    class Meta(QuestionWidgetSerializer.Meta):
        model = MultiChoiceProblem
        fields = QuestionWidgetSerializer.Meta.fields + \
            ['min_selections', 'max_selections',
                'disable_after_answer', 'randomize_choices', 'choices']

    def create(self, validated_data):
        choices_data = validated_data.pop('choices')
        validated_data['widget_type'] = Widget.WidgetTypes.MultiChoiceProblem
        multi_choice_question_instance = super().create(validated_data)
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


class UploadFileProblemSerializer(WidgetSerializer):

    class Meta(QuestionWidgetSerializer.Meta):
        model = UploadFileProblem
        fields = QuestionWidgetSerializer.Meta.fields + []

    @transaction.atomic
    def create(self, validated_data):
        validated_data['widget_type'] = Widget.WidgetTypes.UploadFileProblem
        instance = super().create(validated_data)
        return instance
