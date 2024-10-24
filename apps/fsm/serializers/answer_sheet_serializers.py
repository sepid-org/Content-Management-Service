
from rest_framework import serializers
from rest_framework.exceptions import ParseError
from django.contrib.auth.models import AnonymousUser

from apps.accounts.serializers.user_serializer import AcademicStudentshipReadOnlySerializer, SchoolStudentshipReadOnlySerializer, UserRegistrationReceiptInfoSerializer
from errors.error_codes import serialize_error
from apps.fsm.models import AnswerSheet, RegistrationReceipt, Problem
from apps.response.serializers.answers.answer_polymorphic_serializer import AnswerPolymorphicSerializer


class AnswerSheetSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        answers = self.initial_data.get('answers', [])
        user = self.context.get('user', None)
        if isinstance(user, AnonymousUser):
            self.context['user'] = None
        else:
            self.context['user'] = user

        answer_sheet = super().create({
            'user': self.context.get('user'),
            'form': self.context.get('form'),
            **validated_data
        })

        for answer in answers:
            serializer = AnswerPolymorphicSerializer(data={
                'answer_sheet': answer_sheet.id,
                **answer
            }, context=self.context)
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
        fields = ['id', 'answer_sheet_type', 'form', 'user']
        read_only_fields = ['id', 'answer_sheet_type', 'user', 'form']


class RegistrationReceiptSerializer(AnswerSheetSerializer):
    user = UserRegistrationReceiptInfoSerializer(required=False)
    school_studentship = serializers.SerializerMethodField()
    academic_studentship = serializers.SerializerMethodField()

    def get_school_studentship(self, obj):
        return SchoolStudentshipReadOnlySerializer(obj.user.school_studentship).data

    def get_academic_studentship(self, obj):
        return AcademicStudentshipReadOnlySerializer(obj.user.academic_studentship).data

    def create(self, validated_data):
        registration_receipt = super().create({
            'answer_sheet_type': AnswerSheet.AnswerSheetType.RegistrationReceipt,
            **validated_data
        })
        return registration_receipt

    def validate(self, attrs):
        user = self.context.get('user', None)
        form = self.context.get('form', None)

        if not user and not form:
            if len(RegistrationReceipt.objects.filter(form=form, user=user)) > 0:
                raise ParseError(serialize_error('4028'))
        return super().validate(attrs)

    class Meta(AnswerSheetSerializer.Meta):
        model = RegistrationReceipt
        fields = AnswerSheetSerializer.Meta.fields + \
            ['status', 'is_participating', 'team', 'certificate',
                'school_studentship', 'academic_studentship']
        read_only_fields = AnswerSheetSerializer.Meta.read_only_fields + \
            ['status', 'is_participating', 'team', 'certificate']


class MinimalRegistrationReceiptSerializer(AnswerSheetSerializer):
    class Meta(AnswerSheetSerializer.Meta):
        model = RegistrationReceipt
        fields = AnswerSheetSerializer.Meta.fields + \
            ['status', 'is_participating']
        read_only_fields = AnswerSheetSerializer.Meta.read_only_fields + []


class RegistrationStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=RegistrationReceipt.RegistrationStatus.choices)


class ReceiptGetSerializer(serializers.Serializer):
    receipt = serializers.PrimaryKeyRelatedField(queryset=RegistrationReceipt.objects.filter(is_participating=True),
                                                 required=True)
