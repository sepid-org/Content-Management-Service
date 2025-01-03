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
        for tag in tags:
            tag = Tag.objects.filter(name=tag).first()
            if tag:
                article.tags.add(tag)
            else:
                tag_serializer = TagSerializer(data={'name': tag})
                if tag_serializer.is_valid(raise_exception=True):
                    tag = tag_serializer.save()
                    article.tags.add(tag)

        # set is_private to False (articles are public objects)
        article.is_private = False

        article.save()
        return article

    def validate_tags(self, tags):
        if len(tags) > 5:
            raise ValidationError(serialize_error('4106'))
        return tags

    def validate(self, attrs):
        publisher = attrs.get('publisher', None)
        creator = attrs.get('creator', None)
        if publisher and creator not in publisher.admins.all():
            raise PermissionDenied(serialize_error('4105'))

        return super(ArticleSerializer, self).validate(attrs)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['tags'] = TagSerializer(
            instance.tags.all(), many=True).data
        return representation

    class Meta(PaperSerializer.Meta):
        model = Article
        fields = [field for field in PaperSerializer.Meta.fields if field != 'widgets'] +\
            ['name', 'description', 'tags', 'is_draft',
                'publisher', 'cover_page', 'is_hidden']
        read_only_fields = PaperSerializer.Meta.read_only_fields + []
