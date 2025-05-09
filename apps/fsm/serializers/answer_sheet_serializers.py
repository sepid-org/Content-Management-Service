from rest_framework import serializers
from rest_framework.exceptions import ParseError

from apps.accounts.models import User
from apps.accounts.serializers.user_serializer import AcademicStudentshipReadOnlySerializer, SchoolStudentshipReadOnlySerializer, UserRegistrationReceiptInfoSerializer
from apps.engagement.serializers.answer_sheet import AnswerSheetSerializer
from errors.error_codes import serialize_error
from apps.fsm.models import AnswerSheet, RegistrationReceipt


class RegistrationReceiptSerializer(AnswerSheetSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    school_studentship = serializers.SerializerMethodField()
    academic_studentship = serializers.SerializerMethodField()

    def get_school_studentship(self, obj):
        school_studentship = getattr(obj.user, 'school_studentship', None)
        if school_studentship is not None:
            return SchoolStudentshipReadOnlySerializer(school_studentship).data
        return None

    def get_academic_studentship(self, obj):
        academic_studentship = getattr(obj.user, 'academic_studentship', None)
        if academic_studentship is not None:
            return AcademicStudentshipReadOnlySerializer(academic_studentship).data
        return None

    def create(self, validated_data):
        validated_data['answer_sheet_type'] = AnswerSheet.AnswerSheetType.RegistrationReceipt
        return super().create(validated_data)

    def validate(self, attrs):
        user = attrs.get('user')
        form = attrs.get('form')
        if RegistrationReceipt.objects.filter(form=form, user=user).count() > 0:
            raise ParseError(serialize_error('4028'))
        return super().validate(attrs)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.user:
            representation['user'] = UserRegistrationReceiptInfoSerializer(
                instance.user).data
        return representation

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
