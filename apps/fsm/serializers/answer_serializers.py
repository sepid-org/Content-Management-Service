import os
from datetime import datetime
from rest_framework import serializers
from rest_framework.exceptions import ParseError
from rest_polymorphic.serializers import PolymorphicSerializer
from errors.error_codes import serialize_error
from apps.fsm.models import SmallAnswer, BigAnswer, MultiChoiceAnswer, UploadFileAnswer, Choice
from apps.fsm.serializers.validators import multi_choice_answer_validator


class AnswerSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = self.context.get('user', None)
        answer_sheet = self.context.get('answer_sheet', None)
        print("@@@@@@@@@@", answer_sheet)
        validated_data.get('problem').unfinalize_older_answers(user)
        return super().create({'submitted_by': user, **validated_data})

    def update(self, instance, validated_data):
        user = self.context.get('user', None)
        if 'problem' not in validated_data.keys():
            validated_data['problem'] = instance.problem
        elif validated_data.get('problem', None) != instance.problem:
            raise ParseError(serialize_error('4102'))
        instance.problem.unfinalize_older_answers(user)
        return super(AnswerSerializer, self).update(instance, {'is_final_answer': True, **validated_data})

    def validate(self, attrs):
        problem = attrs.get('problem', None)
        answer_sheet = self.context.get('answer_sheet', None)
        if answer_sheet is not None and problem is not None and problem.paper is not None:
            if answer_sheet.form != problem.paper:
                raise ParseError(serialize_error('4027', {'problem.paper': problem.paper,
                                                          'original paper': answer_sheet.form},
                                                 is_field_error=False))
        return attrs


class SmallAnswerSerializer(AnswerSerializer):
    def create(self, validated_data):
        return super().create({'answer_type': 'SmallAnswer', **validated_data})

    class Meta:
        model = SmallAnswer
        fields = ['id', 'answer_type', 'answer_sheet', 'submitted_by', 'created_at', 'is_final_answer', 'is_correct',
                  'problem', 'text']
        read_only_fields = ['id', 'submitted_by', 'created_at']


class BigAnswerSerializer(AnswerSerializer):
    def create(self, validated_data):
        return super().create({'answer_type': 'BigAnswer', **validated_data})

    class Meta:
        model = BigAnswer
        fields = ['id', 'answer_type', 'answer_sheet', 'submitted_by', 'created_at', 'is_final_answer', 'is_correct',
                  'problem', 'text']
        read_only_fields = ['id', 'submitted_by', 'created_at', 'is_correct']


class ChoiceSerializer(serializers.ModelSerializer):
    is_correct = serializers.BooleanField(required=False)

    class Meta:
        model = Choice
        fields = ['id', 'text', 'is_correct']

    def to_internal_value(self, data):
        internal_value = super(ChoiceSerializer, self).to_internal_value(data)
        internal_value.update({"id": data.get("id")})
        return internal_value


class MultiChoiceAnswerSerializer(AnswerSerializer):
    choices = ChoiceSerializer(many=True, required=False)

    class Meta:
        model = MultiChoiceAnswer
        fields = ['id', 'answer_type', 'answer_sheet', 'submitted_by', 'created_at', 'is_final_answer', 'is_correct',
                  'problem', 'choices']
        read_only_fields = ['id', 'submitted_by', 'created_at']

    def create(self, validated_data):
        choices_data = validated_data.pop('choices', [])
        choices_ids = [choice_data['id'] for choice_data in choices_data]
        choices_instances = Choice.objects.filter(id__in=choices_ids)
        instance = super(MultiChoiceAnswerSerializer, self).create(
            {'answer_type': 'MultiChoiceAnswer', **validated_data})
        instance.choices.add(*choices_instances)
        instance.save()
        self.context['choices'] = choices_instances
        return instance

    def validate(self, attrs):
        attrs = super(MultiChoiceAnswerSerializer, self).validate(attrs)
        choices = attrs.get('choices', [])
        problem = attrs.get('problem')
        multi_choice_answer_validator(
            choices, problem.maximum_choices_could_be_chosen)
        return attrs


class UploadFileAnswerSerializer(AnswerSerializer):

    class Meta:
        model = UploadFileAnswer
        fields = ['id', 'answer_type', 'answer_sheet', 'submitted_by', 'created_at', 'is_final_answer', 'is_correct',
                  'problem', 'answer_file']
        read_only_fields = ['id', 'answer_type',
                            'submitted_by', 'created_at', 'is_correct']

    def validate(self, attrs):
        problem = attrs.get('problem', None)
        if problem:
            if problem.paper:
                if (problem.paper.since and datetime.now(problem.paper.since.tzinfo) < problem.paper.since) or \
                        (problem.paper.till and datetime.now(problem.paper.till.tzinfo) > problem.paper.till):
                    raise ParseError(serialize_error('4104'))
        return attrs

    def to_representation(self, instance):
        representation = super(UploadFileAnswerSerializer,
                               self).to_representation(instance)
        answer_file = representation['answer_file']
        if answer_file.startswith('/api/'):
            domain = self.context.get('domain', None)
            if domain:
                representation['answer_file'] = domain + answer_file
        return representation


class MockAnswerSerializer(serializers.Serializer):
    SmallAnswerSerializer = SmallAnswerSerializer(required=False)
    BigAnswerSerializer = BigAnswerSerializer(required=False)
    MultiChoiceAnswerSerializer = MultiChoiceAnswerSerializer(required=False)
    UploadFileAnswerSerializer = UploadFileAnswerSerializer(required=False)


class AnswerPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        # Answer: AnswerSerializer,
        SmallAnswer: SmallAnswerSerializer,
        BigAnswer: BigAnswerSerializer,
        MultiChoiceAnswer: MultiChoiceAnswerSerializer,
        UploadFileAnswer: UploadFileAnswerSerializer,
    }

    resource_type_field_name = 'answer_type'
