from django.forms import ValidationError
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from apps.fsm.models import Article
from apps.fsm.permissions import IsArticleModifier
from apps.fsm.serializers.papers.article_serializer import ArticleSerializer
from apps.fsm.utils.utils import SafeTokenAuthentication


class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()
    my_tags = ['articles']

    def get_queryset(self):
        queryset = super().get_queryset()
        website = self.request.headers.get('Website')

        if not website:
            raise ValidationError("Website header is required")

        queryset = queryset.filter(website=website)

        is_hidden = self.request.query_params.get('is_hidden')
        if is_hidden:
            is_hidden = is_hidden == 'true'
            queryset = queryset.filter(_object__is_hidden=is_hidden)

        return queryset

    def get_authenticators(self):
        if self.request.method == 'GET':
            self.authentication_classes = [SafeTokenAuthentication]
        return super().get_authenticators()

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ['update', 'destroy', 'partial_update', 'change_order']:
            permission_classes = [IsArticleModifier]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
