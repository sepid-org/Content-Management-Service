from rest_framework import permissions
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import NotFound
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.views.decorators.cache import cache_page

from apps.fsm.models import Program
from apps.fsm.pagination import ProgramsPagination
from apps.fsm.permissions import ProgramAdminPermission
from apps.fsm.serializers.program_serializers import ProgramSerializer, ProgramSummarySerializer
from apps.accounts.serializers.user_serializer import UserSerializer
from apps.accounts.utils import find_user_in_website
from apps.fsm.utils import add_admin_to_program
from errors.error_codes import serialize_error
from utilities.safe_auth import SafeTokenAuthentication


class ProgramViewSet(ModelViewSet):
    serializer_class = ProgramSerializer
    queryset = Program.objects.filter(is_deleted=False)
    my_tags = ['program']
    filterset_fields = ['website']
    pagination_class = ProgramsPagination

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        # Add headers to prevent frontend caching
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'

        return response

    def get_object(self):
        lookup_value = self.kwargs.get(self.lookup_field)
        program = self.queryset.filter(slug=lookup_value).first(
        ) or self.queryset.filter(id=lookup_value).first()
        if not program:
            raise NotFound(f"No Program found with slug or id: {lookup_value}")
        return program

    def initialize_request(self, request, *args, **kwargs):
        self.action = self.action_map.get(request.method.lower())
        return super().initialize_request(request, *args, **kwargs)

    def get_authenticators(self):
        if self.action in ['retrieve', 'list']:
            return [SafeTokenAuthentication()]
        return super().get_authenticators()

    def get_serializer_class(self):
        if self.action == 'list':
            return ProgramSummarySerializer
        return ProgramSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        return context

    def get_permissions(self):
        if self.action in ['retrieve', 'list']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [ProgramAdminPermission]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['get'])
    def get_admins(self, request, pk):
        admins = self.get_object().admins
        return Response(data=UserSerializer(admins, many=True).data)

    @action(detail=True, methods=['post'], serializer_class=UserSerializer)
    def add_admin(self, request, pk=None):
        program = self.get_object()
        user_serializer = UserSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)
        user = find_user_in_website(
            user_data=user_serializer.validated_data,
            website=request.data.get("website"),
            raise_exception=True,
        )
        add_admin_to_program(user, program)
        return Response()

    @action(detail=True, methods=['post'], serializer_class=UserSerializer)
    def remove_admin(self, request, pk=None):
        program = self.get_object()
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        removed_admin = find_user_in_website(
            user_data={**serializer.validated_data}, website=request.data.get("website"))
        if removed_admin == program.creator:
            raise ParseError(serialize_error('5007'))
        if removed_admin in program.admins.all():
            program.admins.remove(removed_admin)
        return Response()

    @action(detail=True, methods=['get'])
    def soft_delete(self, request, pk=None):
        program = self.get_object()
        program.is_deleted = True
        program.deleted_at = timezone.now()
        program.save()
        self.invalidate_list_cache()
        return Response()

    @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        self.invalidate_list_cache()
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        self.invalidate_list_cache()
        return response

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        self.invalidate_list_cache()
        return response

    def invalidate_list_cache(self):
        cache_key = self.get_list_cache_key()
        cache.delete(cache_key)

    def get_list_cache_key(self):
        # This should match the key used by cache_page
        return f'program-view-set.{self.request.path}'
