from datetime import datetime
from rest_framework import serializers
from rest_framework.exceptions import ParseError
from errors.error_codes import serialize_error
from apps.fsm.models import Answer, SmallAnswer, BigAnswer, MultiChoiceAnswer, UploadFileAnswer, Choice
from apps.fsm.serializers.validators import multi_choice_answer_validator


class AnswerSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = validated_data.get('submitted_by', None)
        validated_data.get('problem').unfinalize_older_answers(user)
        return super().create({'submitted_by': user, **validated_data})

    def update(self, instance, validated_data):
        user = validated_data.get('submitted_by', None)
        if 'problem' not in validated_data.keys():
            validated_data['problem'] = instance.problem
        elif validated_data.get('problem', None) != instance.problem:
            raise ParseError(serialize_error('4102'))
        instance.problem.unfinalize_older_answers(user)
        return super(AnswerSerializer, self).update(instance, {'is_final_answer': True, **validated_data})

    class Meta:
        model = Answer
        fields = ['id', 'answer_type', 'answer_sheet', 'submitted_by',
                  'created_at', 'is_final_answer', 'is_correct', 'problem']
        read_only_fields = ['id', 'answer_type', 'created_at']


class SmallAnswerSerializer(AnswerSerializer):
    def create(self, validated_data):
        validated_data['answer_type'] = 'SmallAnswer'
        return super().create(validated_data)

    class Meta(AnswerSerializer.Meta):
        model = SmallAnswer
        fields = AnswerSerializer.Meta.fields + ['text']


class BigAnswerSerializer(AnswerSerializer):
    def create(self, validated_data):
        validated_data['answer_type'] = 'BigAnswer'
        return super().create(validated_data)

    class Meta(AnswerSerializer.Meta):
        model = BigAnswer
        fields = AnswerSerializer.Meta.fields + ['text']


class ChoiceSerializer(serializers.ModelSerializer):
    is_correct = serializers.BooleanField(required=False)

    class Meta:
        model = Choice
        fields = ['id', 'text', 'is_correct']
        read_only_fields = ['id']

    def to_internal_value(self, data):
        internal_value = super(ChoiceSerializer, self).to_internal_value(data)
        internal_value.update({"id": data.get("id")})
        return internal_value


class MultiChoiceAnswerSerializer(AnswerSerializer):
    choices = serializers.PrimaryKeyRelatedField(
        queryset=Choice.objects.all(), many=True, required=False)

    def create(self, validated_data):
        choices_instances = validated_data.pop('choices', [])

        validated_data['answer_type'] = 'MultiChoiceAnswer'
        answer_instance = super().create(validated_data)
        answer_instance.choices.add(*choices_instances)
        answer_instance.save()

        return answer_instance

    def validate(self, attrs):
        attrs = super().validate(attrs)
        choices = attrs.get('choices', [])
        problem = attrs.get('problem')
        multi_choice_answer_validator(
            choices, problem.max_selections)
        return attrs

    class Meta(AnswerSerializer.Meta):
        model = MultiChoiceAnswer
        fields = AnswerSerializer.Meta.fields + ['choices']


class UploadFileAnswerSerializer(AnswerSerializer):

    def create(self, validated_data):
        validated_data['answer_type'] = 'UploadFileAnswer'
        return super().create(validated_data)

    class Meta(AnswerSerializer.Meta):
        model = UploadFileAnswer
        fields = AnswerSerializer.Meta.fields + ['answer_file']
