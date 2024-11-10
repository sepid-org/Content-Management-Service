from rest_framework import status
from rest_framework import viewsets
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.attributes.utils import is_object_free_to_buy
from apps.fsm.models import Hint
from apps.fsm.models.base import Resource, Paper
from apps.fsm.permissions import IsHintModifier
from apps.fsm.serializers.resource import PublicResourceSerializer, ResourceSerializer
from apps.fsm.serializers.papers.hint_serializer import HintSerializer
from apps.treasury.utils import has_user_spent_on_object


class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    my_tags = ['resources']

    def get_permissions(self):
        if self.action in ['retrieve', 'list', 'by_object']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsHintModifier]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action in ['retrieve', 'by_type']:
            return ResourceSerializer
        return PublicResourceSerializer

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        obj = self.get_object()

        if has_user_spent_on_object(user.id, obj.id) or is_object_free_to_buy(obj):
            return super().retrieve(request, *args, **kwargs)
        else:
            return Response(
                {"error": "Access to this resource is restricted."},
                status=status.HTTP_403_FORBIDDEN
            )

    @action(detail=False, methods=['get'], url_path='by-type')
    def by_type(self, request):
        resource_type = request.query_params.get('type')
        if not resource_type:
            return Response(
                {"error": "type query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        object_id = request.query_params.get('object_id')
        if object_id:
            resources = Resource.objects.filter(
                target_object_id=object_id,
                type=resource_type
            )
        else:
            resources = Resource.objects.filter(type=resource_type)
        serializer = self.get_serializer(
            resources,
            many=True,
            context=self.get_serializer_context(),
        )
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-object')
    def by_object(self, request):
        object_id = request.query_params.get('object_id')
        if not object_id:
            return Response(
                {"error": "object_id query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        resource_type = request.query_params.get('type')
        if resource_type:
            resources = Resource.objects.filter(
                target_object_id=object_id,
                type=resource_type
            )
        else:
            resources = Resource.objects.filter(target_object_id=object_id)
        serializer = self.get_serializer(
            resources,
            many=True,
            context=self.get_serializer_context(),
        )
        return Response(serializer.data)


class HintViewSet(viewsets.ModelViewSet):
    serializer_class = HintSerializer
    queryset = Hint.objects.all()
    my_tags = ['hint']

    def get_permissions(self):
        if self.action == 'retrieve' or self.action == 'list':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsHintModifier]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        request.data['paper_type'] = Paper.PaperType.Hint
        request.data['creator'] = request.user.id
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='by-fsm-state')
    def by_fsm_state(self, request):
        fsm_state_id = request.query_params.get('fsm_state_id')

        if not fsm_state_id:
            return Response(
                {"error": "fsm_state_id query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        hints = self.queryset.filter(reference=fsm_state_id)
        serializer = self.get_serializer(hints, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
