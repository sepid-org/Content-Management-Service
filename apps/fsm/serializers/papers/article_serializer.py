from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.fsm.serializers.papers.paper_serializer import PaperSerializer
from errors.error_codes import serialize_error
from apps.fsm.models import Article, Tag


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ['id']


class ArticleSerializer(PaperSerializer):
    tags = serializers.ListSerializer(required=False, child=serializers.CharField(min_length=1, max_length=100),
                                      allow_null=True, allow_empty=True)
    is_hidden = serializers.SerializerMethodField()

    def get_is_hidden(self, obj):
        return obj.is_hidden

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        validated_data['paper_type'] = 'Article'
        article = super().create(validated_data)

        for tag_name in tags:
            tag_object = Tag.objects.filter(name=tag_name).first()
            if not tag_object:
                tag_serializer = TagSerializer(data={'name': tag_name})
                tag_serializer.is_valid(raise_exception=True)
                tag_object = tag_serializer.save()
            article.tags.add(tag_object)

        # set is_private to False (articles are public objects)
        article.object.is_private = False
        article.object.save()

        article.save()
        return article

    def validate_tags(self, tags):
        if len(tags) > 5:
            raise ValidationError(serialize_error('4106'))
        return tags

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['tags'] = TagSerializer(
            instance.tags.all(), many=True).data
        return representation

    class Meta(PaperSerializer.Meta):
        model = Article
        fields = [field for field in PaperSerializer.Meta.fields if field != 'widgets'] +\
            ['name', 'description', 'tags', 'cover_image', 'is_hidden', 'website']
        read_only_fields = PaperSerializer.Meta.read_only_fields + []
