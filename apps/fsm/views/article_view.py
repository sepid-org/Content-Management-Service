from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from django.views.decorators.cache import cache_page
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.http import JsonResponse

from apps.fsm.models import Article
from apps.fsm.permissions import IsArticleModifier
from apps.fsm.serializers.paper_serializers import ArticleSerializer, ChangeWidgetOrderSerializer
from apps.fsm.utils import SafeTokenAuthentication


@cache_page(60 * 1,  key_prefix="site1")
def say_hello(request):
    articles = Article.objects.all()
    data = []
    for i in articles:
        data.append(i.name)
    print(articles)
    return JsonResponse({"message": data})


class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()
    my_tags = ['articles']
    filterset_fields = ['website']

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

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        context.update({'editable': True})
        context.update(
            {'domain': self.request.build_absolute_uri('/api/')[:-5]})
        return context

    @swagger_auto_schema(responses={200: ArticleSerializer})
    @transaction.atomic
    @action(detail=True, methods=['post'], serializer_class=ChangeWidgetOrderSerializer)
    def change_order(self, request, pk=None):
        serializer = ChangeWidgetOrderSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            self.get_object().set_widget_order(serializer.validated_data.get('order'))
        return Response(data=ArticleSerializer(self.get_object()).data, status=status.HTTP_200_OK)

    # @method_decorator(cache_page(60 * 1,  key_prefix="article"))
    def list(self, request, *args, **kwargs):
        return super().list(self, request, *args, **kwargs)
