from rest_framework import permissions, status
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils.decorators import method_decorator
from django.core.cache import cache

from apps.fsm.models import Program
from apps.fsm.pagination import ProgramsPagination
from apps.fsm.permissions import ProgramAdminPermission
from apps.fsm.serializers.program_serializers import ProgramSerializer, ProgramSummarySerializer
from apps.accounts.serializers.user_serializer import UserSerializer
from apps.accounts.utils import find_user_in_website
from apps.fsm.utils import add_admin_to_program
from errors.error_codes import serialize_error
from utilities.custom_cache_key import custom_cache_page
from utilities.safe_auth import SafeTokenAuthentication


class ProgramViewSet(ModelViewSet):
    queryset = Program.objects.filter(is_deleted=False)
    serializer_class = ProgramSerializer
    pagination_class = ProgramsPagination
    authentication_classes = [SafeTokenAuthentication]
    permission_classes = [IsAuthenticated]
    filterset_fields = ['website']
    lookup_field = 'slug'

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        self._add_no_cache_headers(response)
        return response

    def get_object(self):
        lookup_value = self.kwargs.get(self.lookup_field)
        program = self.queryset.filter(slug=lookup_value).first(
        ) or self.queryset.filter(id=lookup_value).first()
        if not program:
            raise NotFound(f"No Program found with slug or id: {lookup_value}")
        return program

    def get_permissions(self):
        if self.action in ['retrieve', 'list']:
            return [AllowAny()]
        return [ProgramAdminPermission()]

    def get_serializer_class(self):
        if self.action == 'list':
            return ProgramSummarySerializer
        return ProgramSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

    @action(detail=True, methods=['get'])
    def get_admins(self, request, slug=None):
        program = self.get_object()
        serializer = UserSerializer(program.admins.all(), many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_admin(self, request, slug=None):
        program = self.get_object()
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self._find_user(serializer.validated_data,
                               request.data.get("website"))
        add_admin_to_program(user, program)
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def remove_admin(self, request, slug=None):
        program = self.get_object()
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        removed_admin = self._find_user(
            serializer.validated_data, request.data.get("website"))
        self._ensure_not_creator(removed_admin, program)
        program.admins.remove(removed_admin)
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def soft_delete(self, request, slug=None):
        program = self.get_object()
        program.is_deleted = True
        program.deleted_at = timezone.now()
        program.save()
        self._invalidate_list_cache()
        return Response()

    @method_decorator(custom_cache_page(60 * 15, cache_key_prefix='programs_list'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        self._invalidate_list_cache()
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        self._invalidate_list_cache()
        return response

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        self._invalidate_list_cache()
        return response

    def _add_no_cache_headers(self, response):
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'

    def _find_user(self, user_data, website):
        return find_user_in_website(user_data=user_data, website=website, raise_exception=True)

    def _ensure_not_creator(self, user, program):
        if user == program.creator:
            raise ParseError(serialize_error('5007'))

    def _invalidate_list_cache(self):
        cache.delete_pattern('programs_list:*')
