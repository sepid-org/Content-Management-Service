from apps.fsm.serializers.fsm_serializers import EdgeSerializer
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ParseError, PermissionDenied, ValidationError
from rest_polymorphic.serializers import PolymorphicSerializer

from errors.error_codes import serialize_error
from apps.fsm.models import Program, Paper, WidgetHint, FSM, RegistrationForm, Article, Hint, Edge, State, Tag
from apps.fsm.serializers.certificate_serializer import CertificateTemplateSerializer
from apps.fsm.serializers.widgets.widget_polymorphic_serializer import WidgetPolymorphicSerializer


class PaperMinimalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Paper
        fields = ['id', 'paper_type']


class PaperSerializer(serializers.ModelSerializer):
    widgets = WidgetPolymorphicSerializer(many=True)

    @transaction.atomic
    def create(self, validated_data):
        widgets = validated_data.pop('widgets', [])
        user = self.context.get('user', None)
        instance = super().create({'creator': user, **validated_data})
        for widget in widgets:
            widget['creator'] = user
            serializer = WidgetPolymorphicSerializer(
                data=widget, context=self.context)
            if serializer.is_valid(raise_exception=True):
                serializer.validated_data['paper'] = instance
                serializer.save()
        return instance

    class Meta:
        model = Paper
        fields = ['id', 'widgets']
        read_only_fields = ['id']


class RegistrationFormSerializer(PaperSerializer):
    min_grade = serializers.IntegerField(required=False, validators=[
                                         MaxValueValidator(12), MinValueValidator(0)])
    max_grade = serializers.IntegerField(required=False, validators=[
                                         MaxValueValidator(12), MinValueValidator(0)])
    program = serializers.PrimaryKeyRelatedField(
        queryset=Program.objects.all(), required=False, allow_null=True)
    fsm = serializers.PrimaryKeyRelatedField(
        queryset=FSM.objects.all(), required=False, allow_null=True)
    certificate_templates = CertificateTemplateSerializer(
        many=True, read_only=True)

    @transaction.atomic
    def create(self, validated_data):
        program = validated_data.get('program', None)
        fsm = validated_data.get('fsm', None)
        instance = super(RegistrationFormSerializer,
                         self).create(validated_data)
        if program is not None:
            program.registration_form = instance
            program.save()
        elif fsm is not None:
            fsm.registration_form = instance
            fsm.save()

        return instance

    def validate_program(self, program):
        if program is not None and self.context.get('user', None) not in program.modifiers:
            raise PermissionDenied(serialize_error('4026'))
        return program

    def validate_fsm(self, fsm):
        if fsm is not None and self.context.get('user', None) not in fsm.modifiers:
            raise PermissionDenied(serialize_error('4026'))
        return fsm

    class Meta(PaperSerializer.Meta):
        model = RegistrationForm
        ref_name = 'registration_form'
        fields = PaperSerializer.Meta.fields + ['min_grade', 'max_grade', 'program', 'fsm', 'paper_type', 'accepting_status',
                                                'certificate_templates', 'has_certificate', 'certificates_ready', 'audience_type', 'gender_partition_status']
        read_only_fields = PaperSerializer.Meta.read_only_fields + \
            []


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ['id']


class ArticleSerializer(PaperSerializer):
    tags = serializers.ListSerializer(required=False, child=serializers.CharField(min_length=1, max_length=100),
                                      allow_null=True, allow_empty=True)

    @transaction.atomic
    def create(self, validated_data):
        user = self.context.get('user', None)
        tags = validated_data.pop(
            'tags') if 'tags' in validated_data.keys() else []
        article = super(ArticleSerializer, self).create(
            {'paper_type': 'Article', 'creator': user, **validated_data})
        for t in tags:
            tag = Tag.objects.filter(name=t).first()
            if tag:
                article.tags.add(tag)
            else:
                tag_serializer = TagSerializer(
                    data={'name': t}, context=self.context)
                if tag_serializer.is_valid(raise_exception=True):
                    article.tags.add(tag_serializer.save())
        article.save()
        return article

    def validate_tags(self, tags):
        if len(tags) > 5:
            raise ValidationError(serialize_error('4106'))
        return tags

    def validate(self, attrs):
        publisher = attrs.get('publisher', None)
        user = self.context.get('user', None)
        if publisher and user not in publisher.admins.all():
            raise PermissionDenied(serialize_error('4105'))

        return super(ArticleSerializer, self).validate(attrs)

    def to_representation(self, instance):
        representation = super(
            ArticleSerializer, self).to_representation(instance)
        representation['tags'] = TagSerializer(
            instance.tags.all(), context=self.context, many=True).data
        return representation

    class Meta(PaperSerializer.Meta):
        model = Article
        ref_name = 'article'
        fields = PaperSerializer.Meta.fields + ['name', 'description', 'tags',
                                                'is_draft', 'publisher', 'cover_page']
        read_only_fields = PaperSerializer.Meta.read_only_fields + []


class HintSerializer(PaperSerializer):

    @transaction.atomic
    def create(self, validated_data):
        user = self.context.get('user', None)
        return super(HintSerializer, self).create({'paper_type': 'Hint', 'creator': user, **validated_data})

    def validate(self, attrs):
        reference = attrs.get('reference', None)
        user = self.context.get('user', None)
        if user not in reference.fsm.mentors.all():
            raise PermissionDenied(serialize_error('4075'))

        return super(HintSerializer, self).validate(attrs)

    class Meta(PaperSerializer.Meta):
        model = Hint
        ref_name = 'hint'
        fields = PaperSerializer.Meta.fields + ['reference']
        read_only_fields = PaperSerializer.Meta.read_only_fields + []


class WidgetHintSerializer(PaperSerializer):

    @transaction.atomic
    def create(self, validated_data):
        user = self.context.get('user', None)
        return super(WidgetHintSerializer, self).create({'paper_type': 'Widgethint', 'creator': user, **validated_data})

    class Meta(PaperSerializer.Meta):
        model = WidgetHint
        ref_name = 'hint'
        fields = PaperSerializer.Meta.fields + ['reference']
        read_only_fields = PaperSerializer.Meta.read_only_fields + []


class StateSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['name']
        read_only_fields = ['name']


class StateSerializer(PaperSerializer):
    hints = HintSerializer(many=True, read_only=True)
    outward_edges = EdgeSerializer(many=True, read_only=True)
    inward_edges = EdgeSerializer(many=True, read_only=True)

    @transaction.atomic
    def create(self, validated_data):
        fsm = validated_data.get('fsm', None)
        instance = super(StateSerializer, self).create(
            {'paper_type': 'State', **validated_data})
        if fsm.first_state is None:
            fsm.first_state = instance
            fsm.save()

        return instance

    def validate(self, attrs):
        fsm = attrs.get('fsm', None)
        user = self.context.get('user', None)
        if user not in fsm.mentors.all():
            raise PermissionDenied(serialize_error('4075'))

        return super(StateSerializer, self).validate(attrs)

    class Meta(PaperSerializer.Meta):
        model = State
        ref_name = 'state'
        fields = ['id', 'name', 'fsm', 'hints',
                  'inward_edges', 'outward_edges', 'template']
        read_only_fields = PaperSerializer.Meta.read_only_fields + \
            ['hints', 'inward_edges', 'outward_edges']


class PaperPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        'Paper': PaperSerializer,
        'RegistrationForm': RegistrationFormSerializer,
        'Article': ArticleSerializer,
        'State': StateSerializer,
        'Hint': HintSerializer,
        'WidgetHint': WidgetHintSerializer,
    }

    resource_type_field_name = 'paper_type'


class ChangeWidgetOrderSerializer(serializers.Serializer):
    order = serializers.ListField(
        child=serializers.IntegerField(min_value=1), allow_empty=True)
