from rest_framework import serializers
from rest_framework.exceptions import ParseError

from apps.accounts.serializers.user_serializer import AcademicStudentshipReadOnlySerializer, SchoolStudentshipReadOnlySerializer, UserRegistrationReceiptInfoSerializer
from apps.response.serializers.answer_sheet import AnswerSheetSerializer
from errors.error_codes import serialize_error
from apps.fsm.models import AnswerSheet, RegistrationReceipt


class RegistrationReceiptSerializer(AnswerSheetSerializer):
    school_studentship = serializers.SerializerMethodField()
    academic_studentship = serializers.SerializerMethodField()

    def get_school_studentship(self, obj):
        return SchoolStudentshipReadOnlySerializer(obj.user.school_studentship).data

    def get_academic_studentship(self, obj):
        return AcademicStudentshipReadOnlySerializer(obj.user.academic_studentship).data

    def create(self, validated_data):
        validated_data['answer_sheet_type'] = AnswerSheet.AnswerSheetType.RegistrationReceipt
        registration_receipt = super().create(validated_data)
        return registration_receipt

    def validate(self, attrs):
        user = attrs.get('user')
        # todo: complete it
        if not user:
            raise ParseError("registration receipt must have user")
        form = attrs.get('form')
        if len(RegistrationReceipt.objects.filter(form=form, user=user)) > 0:
            raise ParseError(serialize_error('4028'))
        return super().validate(attrs)

    class Meta(AnswerSheetSerializer.Meta):
        model = RegistrationReceipt
        fields = AnswerSheetSerializer.Meta.fields + \
            ['form', 'status', 'is_participating', 'team', 'certificate',
                'school_studentship', 'academic_studentship']
        read_only_fields = AnswerSheetSerializer.Meta.read_only_fields + \
            ['status', 'is_participating', 'team', 'certificate',
                'school_studentship', 'academic_studentship']


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
