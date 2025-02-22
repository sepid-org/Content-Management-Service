from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.fsm.models.base import Object
from apps.fsm.serializers.papers.paper_serializer import PaperSerializer
from errors.error_codes import serialize_error
from apps.fsm.models import Article, Tag


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ['id']


class ArticleSerializer(PaperSerializer):
    tags = serializers.ListSerializer(
        child=serializers.CharField(min_length=1, max_length=100),
        required=False,
        allow_null=True,
        allow_empty=True
    )
    is_hidden = serializers.SerializerMethodField()

    def get_is_hidden(self, obj):
        return obj.is_hidden

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        validated_data['paper_type'] = 'Article'
        validated_data['creator'] = self.context['request'].user
        instance = super().create(validated_data)

        for tag_name in tags:
            tag_object = Tag.objects.filter(name=tag_name).first()
            if not tag_object:
                tag_serializer = TagSerializer(data={'name': tag_name})
                tag_serializer.is_valid(raise_exception=True)
                tag_object = tag_serializer.save()
            instance.tags.add(tag_object)

        # set is_private to False (articles are public objects)
        Object.objects.filter(id=instance.object.id).update(
            is_private=False,
        )

        instance.save()
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', [])
        instance = super().update(instance, validated_data)

        # Clear existing tags and add new ones
        instance.tags.clear()
        for tag_name in tags:
            tag_object = Tag.objects.filter(name=tag_name).first()
            if not tag_object:
                tag_serializer = TagSerializer(data={'name': tag_name})
                tag_serializer.is_valid(raise_exception=True)
                tag_object = tag_serializer.save()
            instance.tags.add(tag_object)

        Object.objects.filter(id=instance.object.id).update(
            is_hidden=self.initial_data.get(
                'is_hidden', instance.object.is_hidden),
        )

        instance.save()
        return instance

    def validate_tags(self, tags):
        if len(tags) > 5:
            raise ValidationError(serialize_error('4106'))
        return tags

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Represent tags as a list of strings (tag names)
        representation['tags'] = [tag.name for tag in instance.tags.all()]
        return representation

    def to_internal_value(self, data):
        # Convert tags from list of strings to list of tag objects
        tags = data.get('tags', [])
        internal_value = super().to_internal_value(data)
        internal_value['tags'] = tags
        return internal_value

    class Meta(PaperSerializer.Meta):
        model = Article
        fields = [field for field in PaperSerializer.Meta.fields if field != 'widgets'] + \
                 ['name', 'description', 'tags',
                     'cover_image', 'is_hidden', 'website']
        read_only_fields = PaperSerializer.Meta.read_only_fields + []
