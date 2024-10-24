from rest_framework import status
from django.utils import timezone
from django.db.models import Prefetch
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, ParseError
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny

from apps.fsm.models import Program, Player, RegistrationReceipt
from apps.fsm.pagination import ProgramsPagination
from apps.fsm.permissions import ProgramAdminPermission
from apps.fsm.serializers.program_serializers import ProgramSerializer, ProgramSummarySerializer
from apps.accounts.serializers.user_serializer import UserSerializer
from apps.accounts.utils import find_user_in_website
from apps.fsm.utils import add_admin_to_program
from errors.error_codes import serialize_error
from utils.cache_enabled_model_viewset import CacheEnabledModelViewSet
from utils.safe_auth import SafeTokenAuthentication


class ProgramViewSet(CacheEnabledModelViewSet):
    queryset = Program.objects.filter(is_deleted=False)
    serializer_class = ProgramSerializer
    pagination_class = ProgramsPagination
    authentication_classes = [SafeTokenAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = super().get_queryset()
        website = self.request.headers.get('Website')

        if website:
            queryset = queryset.filter(website=website)
        else:
            raise ValidationError("Website header is required")

        return queryset

    def get_permissions(self):
        if self.action in ['retrieve', 'list', 'get_user_permissions', 'get_fsms_user_permissions']:
            return [AllowAny()]
        return [ProgramAdminPermission()]

    def get_serializer_class(self):
        if self.action == 'list':
            return ProgramSummarySerializer
        return ProgramSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        return context

    def create(self, request, *args, **kwargs):
        request.data['website'] = request.headers.get('Website')
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
        user = self._find_user(serializer.validated_data,
                               request.headers.get("Website"))
        add_admin_to_program(user, program)
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def remove_admin(self, request, slug=None):
        program = self.get_object()
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        removed_admin = self._find_user(
            serializer.validated_data, request.headers.get("Website"))
        self._ensure_not_creator(removed_admin, program)
        program.admins.remove(removed_admin)
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def soft_delete(self, request, slug=None):
        program = self.get_object()
        program.is_deleted = True
        program.deleted_at = timezone.now()
        program.save()
        self.cache.invalidate_list_cache(request.headers.get('Website'))
        return Response()

    @action(detail=True, methods=['get'])
    def get_user_permissions(self, request, slug=None):
        program = self.get_object()
        return Response({
            'is_manager': request.user in program.modifiers,
        })

    @action(detail=True, methods=['get'])
    def get_user_fsms_status(self, request, slug=None):
        """Get FSM status for a user with optimized database queries."""
        program = self.get_object()
        user = request.user

        # Prefetch related FSMs with necessary relationships
        fsms = program.fsms.prefetch_related(
            'mentors',
            Prefetch(
                'players',
                queryset=Player.objects.filter(
                    user=user,
                    is_active=True
                ).select_related('receipt'),
                to_attr='user_players'
            )
        ).all()

        # Get all relevant registration receipts in one query
        receipts = {
            receipt.form_id: receipt
            for receipt in RegistrationReceipt.objects.filter(
                user=user,
                form=program.registration_form,
                is_participating=True
            )
        }

        # Build status list without additional queries
        status = []
        for fsm in fsms:
            player = next(
                (p for p in fsm.user_players
                 if p.receipt_id == receipts.get(fsm.program.registration_form_id)),
                None
            )

            status.append({
                'fsm_id': fsm.id,
                'is_finished': bool(player and player.finished_at),
                'is_mentor': user in fsm.mentors.all(),
            })

        return Response(status)

    def _find_user(self, user_data, website):
        return find_user_in_website(user_data=user_data, website=website, raise_exception=True)

    def _ensure_not_creator(self, user, program):
        if user == program.creator:
            raise ParseError(serialize_error('5007'))
