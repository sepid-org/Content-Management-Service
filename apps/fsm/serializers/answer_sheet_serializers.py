
from rest_framework import serializers
from rest_framework.exceptions import ParseError

from apps.accounts.serializers.user_serializer import UserSerializer, StudentshipSerializer
from errors.error_codes import serialize_error
from apps.fsm.models import RegistrationReceipt, Problem
from apps.fsm.serializers.answer_serializers import AnswerPolymorphicSerializer


class AnswerSheetSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        answers = self.initial_data.get('answers', [])
        registration_receipt = super().create({
            'user': self.context.get('user'),
            **validated_data
        })

        for answer in answers:
            serializer = AnswerPolymorphicSerializer(data={
                'answer_sheet': registration_receipt.id,
                **answer
            }, context=self.context)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return registration_receipt

    def validate(self, attrs):
        answers = attrs.get('answers', [])
        problems = [a.get('problem', None) for a in answers]
        paper = self.context.get('answer_sheet_of', None)
        if paper is not None:
            for w in paper.widgets.all():
                if isinstance(w, Problem):
                    if w.required and w not in problems:
                        raise ParseError(serialize_error(
                            '4029', {'problem': w}))

        return attrs


class RegistrationReceiptSerializer(AnswerSheetSerializer):
    user = UserSerializer(required=False)
    answers = serializers.SerializerMethodField()
    school_studentship = serializers.SerializerMethodField()
    academic_studentship = serializers.SerializerMethodField()

    def get_answers(self, obj):
        return AnswerPolymorphicSerializer(obj.answers, many=True).data

    def get_school_studentship(self, obj):
        return StudentshipSerializer(obj.user.school_studentship).data

    def get_academic_studentship(self, obj):
        return StudentshipSerializer(obj.user.academic_studentship).data

    class Meta:
        model = RegistrationReceipt
        fields = ['id', 'user', 'answer_sheet_of', 'answers', 'status', 'is_participating', 'team',
                  'certificate', 'school_studentship', 'academic_studentship']
        read_only_fields = ['id', 'user', 'status', 'answer_sheet_of',
                            'is_participating', 'team', 'certificate']

    def validate(self, attrs):
        user = self.context.get('user', None)
        answer_sheet_of = self.context.get('answer_sheet_of', None)

        if not user and not answer_sheet_of:
            if len(RegistrationReceipt.objects.filter(answer_sheet_of=answer_sheet_of, user=user)) > 0:
                raise ParseError(serialize_error('4028'))
        return super().validate(attrs)


# TODO: fix class name
class MyRegistrationReceiptSerializer(AnswerSheetSerializer):
    class Meta:
        model = RegistrationReceipt
        fields = ['id', 'user', 'answer_sheet_type',
                  'answer_sheet_of', 'status', 'is_participating']
        read_only_fields = ['id']


class RegistrationPerCitySerializer(serializers.Serializer):
    city = serializers.CharField(max_length=50)
    registration_count = serializers.IntegerField(min_value=0)


class RegistrationStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=RegistrationReceipt.RegistrationStatus.choices)


class ReceiptGetSerializer(serializers.Serializer):
    receipt = serializers.PrimaryKeyRelatedField(queryset=RegistrationReceipt.objects.filter(is_participating=True),
                                                 required=True)
