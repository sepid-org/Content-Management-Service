from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from apps.fsm.models import Program
from apps.fsm.permissions import ProgramAdminPermission

from apps.fsm.serializers.program_serializers import ProgramSerializer

from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.response import Response

from apps.accounts.serializers import AccountSerializer
from apps.accounts.utils import find_user
from apps.fsm.utils import register_user_in_program
from errors.error_codes import serialize_error


class ProgramViewSet(ModelViewSet):
    serializer_class = ProgramSerializer
    queryset = Program.objects.filter(is_deleted=False)
    my_tags = ['program']
    filterset_fields = ['website', 'is_private']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        return context

    def get_permissions(self):
        if self.action == 'retrieve' or self.action == 'list':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [ProgramAdminPermission]
        return [permission() for permission in permission_classes]

    # @method_decorator(cache_page(60 * 1,  key_prefix="program"))
    def list(self, request, *args, **kwargs):
        return super().list(self, request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def get_admins(self, request, pk):
        admins = self.get_object().admins
        return Response(data=AccountSerializer(admins, many=True).data)

    @action(detail=True, methods=['post'], serializer_class=AccountSerializer)
    def add_admin(self, request, pk=None):
        program = self.get_object()
        user_serializer = AccountSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)
        new_admin = find_user(user_serializer.validated_data)
        program.admins.add(new_admin)
        register_user_in_program(new_admin, program)
        return Response()

    @action(detail=True, methods=['post'], serializer_class=AccountSerializer)
    def remove_admin(self, request, pk=None):
        program = self.get_object()
        serializer = AccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        removed_admin = find_user(serializer.validated_data)
        if removed_admin == program.creator:
            raise ParseError(serialize_error('5007'))
        if removed_admin in program.admins.all():
            program.admins.remove(removed_admin)
        return Response()

    @action(detail=True, methods=['get'])
    def soft_remove_program(self, request, pk=None):
        program = self.get_object()
        program.is_deleted = True
        program.save()
        return Response()
