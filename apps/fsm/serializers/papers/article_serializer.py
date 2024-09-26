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
        fields = PaperSerializer.Meta.get_fields() + ['name', 'description', 'tags',
                                                      'is_draft', 'publisher', 'cover_page']
        read_only_fields = PaperSerializer.Meta.read_only_fields + []
