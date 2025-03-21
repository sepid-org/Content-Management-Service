from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.accounts.models import EducationalInstitute, School
from apps.accounts.permissions import IsInstituteOwner, IsInstituteAdmin
from apps.accounts.serializers.user_serializer import UserSerializer
from apps.accounts.serializers.institute_serializer import InstituteSerializer
from apps.accounts.utils.user_management import find_user_in_website
from errors.error_codes import serialize_error


class InstituteViewSet(ModelViewSet):
    queryset = EducationalInstitute.objects.all()
    serializer_class = InstituteSerializer
    serializer_action_classes = {
        'add_admin': UserSerializer
    }
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['city']
    my_tags = ['institutes']
    pagination_class = None

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()

    def get_permissions(self):
        if self.action == 'create' or self.action == 'retrieve' or self.action == 'list':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'add_admin' or self.action == 'delete':
            permission_classes = [IsInstituteOwner]
        else:
            permission_classes = [IsInstituteAdmin]
        return [permission() for permission in permission_classes]

    @transaction.atomic
    def create(self, request):
        data = request.data
        serializer = InstituteSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            user = request.user
            serializer.validated_data['creator'] = user
            instance = serializer.save()
            return Response(InstituteSerializer(instance).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(responses={200: InstituteSerializer,
                                    400: "error code 4010 for institute not being approved"
                                    })
    @transaction.atomic
    @action(detail=True, methods=['post'], permission_classes=[IsInstituteOwner])
    def add_admin(self, request, pk=None):
        institute = self.get_object()
        if institute.is_approved:
            serializer = UserSerializer(many=False, data=request.data)
            serializer.is_valid(raise_exception=True)
            new_admin = find_user_in_website(
                user_data={**serializer.validated_data},
                website=website,
            )
            institute.admins.add(new_admin)
            return Response(InstituteSerializer(institute).data, status=status.HTTP_200_OK)
        else:
            raise PermissionDenied(serialize_error("4010"))


class SchoolViewSet(InstituteViewSet):
    queryset = School.objects.all()
    filterset_fields = ['city', 'gender_type']
