from apps.fsm.models.base import Paper
from apps.fsm.serializers.form.form_serializer import FormSerializer
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import transaction
from rest_framework import serializers

from apps.fsm.models import Program, RegistrationForm
from apps.fsm.serializers.certificate_serializer import CertificateTemplateSerializer


class RegistrationFormSerializer(FormSerializer):
    min_grade = serializers.IntegerField(required=False, validators=[
                                         MaxValueValidator(12), MinValueValidator(0)])
    max_grade = serializers.IntegerField(required=False, validators=[
                                         MaxValueValidator(12), MinValueValidator(0)])
    program = serializers.PrimaryKeyRelatedField(
        queryset=Program.objects.all(), required=False, allow_null=True)
    certificate_templates = CertificateTemplateSerializer(
        many=True, read_only=True)

    @transaction.atomic
    def create(self, validated_data):
        validated_data['paper_type'] = Paper.PaperType.RegistrationForm
        instance = super().create(validated_data)
        program = validated_data.get('program', None)
        if program is not None:
            program.registration_form = instance
            program.save()

        return instance

    class Meta(FormSerializer.Meta):
        model = RegistrationForm
        fields = FormSerializer.Meta.fields + ['min_grade', 'max_grade', 'program', 'accepting_status',
                                               'certificate_templates', 'has_certificate', 'certificates_ready', 'gender_partition_status']
        read_only_fields = FormSerializer.Meta.read_only_fields + []
