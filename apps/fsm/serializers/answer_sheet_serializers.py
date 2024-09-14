
from rest_framework import serializers
from rest_framework.exceptions import ParseError

from apps.accounts.serializers.user_serializer import AcademicStudentshipReadOnlySerializer, SchoolStudentshipReadOnlySerializer, UserRegistrationReceiptInfoSerializer
from errors.error_codes import serialize_error
from apps.fsm.models import AnswerSheet, RegistrationReceipt, Problem
from apps.responses.serializers.answers.answer_polymorphic_serializer import AnswerPolymorphicSerializer


class AnswerSheetSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        answers = self.initial_data.get('answers', [])
        registration_receipt = super().create({
            'user': self.context.get('user'),
            'form': self.context.get('form'),
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
        answers = self.initial_data.get('answers', [])
        problems = [answer.get('problem', None) for answer in answers]
        paper = self.context.get('form', None)
        if paper is not None:
            for widget in paper.widgets.all():
                if isinstance(widget, Problem) and widget.is_required and widget.id not in problems:
                    raise ParseError(serialize_error(
                        '4029', {'problem': widget}))
        return attrs


class RegistrationReceiptSerializer(AnswerSheetSerializer):
    user = UserRegistrationReceiptInfoSerializer(required=False)
    school_studentship = serializers.SerializerMethodField()
    academic_studentship = serializers.SerializerMethodField()

    def get_school_studentship(self, obj):
        return SchoolStudentshipReadOnlySerializer(obj.user.school_studentship).data

    def get_academic_studentship(self, obj):
        return AcademicStudentshipReadOnlySerializer(obj.user.academic_studentship).data

    def create(self, validated_data):
        user = self.context.get('user')
        form = self.context.get('form')
        if len(RegistrationReceipt.objects.filter(user=user, form=form)) > 0:
            raise ParseError(serialize_error('6003'))

        registration_receipt = super().create({
            'answer_sheet_type': AnswerSheet.AnswerSheetType.RegistrationReceipt,
            **validated_data
        })
        return registration_receipt

    class Meta:
        model = RegistrationReceipt
        fields = ['id', 'user', 'form', 'status', 'is_participating', 'team',
                  'certificate', 'school_studentship', 'academic_studentship']
        read_only_fields = ['id', 'user', 'status', 'form',
                            'is_participating', 'team', 'certificate']

    def validate(self, attrs):
        user = self.context.get('user', None)
        form = self.context.get('form', None)

        if not user and not form:
            if len(RegistrationReceipt.objects.filter(form=form, user=user)) > 0:
                raise ParseError(serialize_error('4028'))
        return super().validate(attrs)


# TODO: fix class name
class MyRegistrationReceiptSerializer(AnswerSheetSerializer):
    class Meta:
        model = RegistrationReceipt
        fields = ['id', 'user', 'answer_sheet_type',
                  'form', 'status', 'is_participating']
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
