from rest_framework import status
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, ParseError
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny

from apps.fsm.models import Program
from apps.fsm.pagination import StandardPagination
from apps.fsm.permissions import ProgramAdminPermission
from apps.fsm.serializers.program_serializers import ProgramSerializer, ProgramSummarySerializer
from apps.accounts.serializers.user_serializer import UserSerializer
from apps.accounts.utils.user_management import find_user_in_website
from apps.fsm.utils.utils import add_admin_to_program
from errors.error_codes import serialize_error
from utils.cache_enabled_model_viewset import CacheEnabledModelViewSet
from content_management_service.authentication.safe_auth import SafeTokenAuthentication


class ProgramViewSet(CacheEnabledModelViewSet):
    queryset = Program.objects.filter(is_deleted=False)
    serializer_class = ProgramSerializer
    pagination_class = StandardPagination
    authentication_classes = [SafeTokenAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = super().get_queryset()
        website = self.request.website

        if not website:
            raise ValidationError("Website header is required")

        queryset = queryset.filter(website=website.name)

        is_visible = self.request.query_params.get('is_visible')
        if is_visible:
            is_visible = is_visible.lower() == 'true'
            queryset = queryset.filter(is_visible=is_visible)

        return queryset

    def get_permissions(self):
        if self.action in ['retrieve', 'list']:
            permission_classes = [AllowAny]
        elif self.action in ['get_user_permissions', 'get_user_fsms_status']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'list':
            return ProgramSummarySerializer
        return ProgramSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        return context

    def create(self, request, *args, **kwargs):
        request.data['website'] = request.website.name
        return super().create(request, *args, **kwargs)

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
        user = self._find_user(
            serializer.validated_data,
            request.website,
        )
        add_admin_to_program(user, program)
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def remove_admin(self, request, slug=None):
        program = self.get_object()
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        removed_admin = self._find_user(
            serializer.validated_data,
            website=request.website,
        )
        self._ensure_not_creator(removed_admin, program)
        program.admins.remove(removed_admin)
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='delete')
    def soft_delete(self, request, slug=None):
        program = self.get_object()
        program.is_deleted = True
        program.deleted_at = timezone.now()
        program.save()
        self.cache.invalidate_list_cache(
            website_name=request.website.name,
        )
        return Response()

    @action(detail=True, methods=['get'], url_path='user-permissions')
    def get_user_permissions(self, request, slug=None):
        program = self.get_object()
        return Response({
            'is_manager': request.user in program.modifiers,
        })

    @action(detail=True, methods=['get'], url_path='user-fsms-status')
    def get_user_fsms_status(self, request, slug=None):
        program = self.get_object()
        user = request.user
        fsms = program.fsms.all()
        fsm_status_list = []
        from apps.fsm.utils.utils import get_players
        for fsm in fsms:
            players = get_players(user, fsm)
            fsm_status_list.append({
                'fsm_id': fsm.id,
                'has_active_player': players.filter(finished_at__isnull=True).exists(),
                'finished_players_count': players.filter(finished_at__isnull=False).count(),
                'is_user_mentor': fsm.get_mentor_role(user.id) is not None,
                'is_enabled_for_user': fsm.is_enabled(user=user),
            })

        return Response(fsm_status_list)

    def _find_user(self, user_data, website):
        return find_user_in_website(
            user_data=user_data,
            website=website,
            raise_exception=True,
        )

    def _ensure_not_creator(self, user, program):
        if user == program.creator:
            raise ParseError(serialize_error('5007'))
