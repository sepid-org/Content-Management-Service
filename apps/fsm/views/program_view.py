from rest_framework import permissions
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from apps.accounts.models import User
from apps.fsm.models import Program
from apps.fsm.pagination import ProgramsPagination
from apps.fsm.permissions import ProgramAdminPermission

from apps.fsm.serializers.program_serializers import ProgramSerializer, ProgramSummarySerializer

from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.response import Response

from apps.accounts.serializers.user_serializer import UserSerializer
from apps.accounts.utils import find_user_in_website
from apps.fsm.utils import add_admin_to_program, register_user_in_program
from errors.error_codes import serialize_error
from utilities.safe_auth import SafeTokenAuthentication


class ProgramViewSet(ModelViewSet):
    serializer_class = ProgramSerializer
    queryset = Program.objects.filter(is_deleted=False)
    my_tags = ['program']
    filterset_fields = ['website']
    pagination_class = ProgramsPagination

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
        return Response()

    # @action(detail=True, methods=['get'])
    # def permission(self, request, pk=None):
    #     user = self.request.user
    #     program = self.get_object()
    #     receipt = user.get_receipt(form=program.registration_form)
    #     print(receipt)
    #     return Response("todo")

    # @action(detail=False, methods=['get'])
    # def permissions(self, request):
    #     user = self.request.user
    #     website = request.GET.get('website')
    #     programs = self.get_queryset().filter(website=website)
    #     permissions = []
    #     for program in programs:
    #         receipt = user.get_receipt(form=program.registration_form)
    #         if receipt:
    #             permissions.append(get_user_permission(receipt))
    #     return Response("todo")
