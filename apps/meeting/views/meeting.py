from django.utils import timezone
from rest_framework.exceptions import APIException
from apps.meeting.utils import is_meeting_running
from django.db import transaction
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import APIException, PermissionDenied

from apps.meeting.models import Meeting
from apps.meeting.serializers.meeting import MeetingSerializer
from apps.meeting.utils import ensure_meeting_session, generate_meeting_join_url, is_meeting_running
from django_filters.rest_framework import DjangoFilterBackend
import django_filters

# Add the MeetingFilter class


class MeetingFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(
        field_name='start_time', lookup_expr='date')

    class Meta:
        model = Meeting
        fields = ['program', 'start_date']


class MeetingViewSet(viewsets.ModelViewSet):
    """
    Provides create, retrieve, update, partial_update, destroy
    and a custom join action for Meeting instances.
    """

    def get_queryset(self):
        return Meeting.objects.filter(deleted_at__isnull=True)
    serializer_class = MeetingSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'meeting_id'
    lookup_value_regex = '[^/]+'

    filter_backends = [DjangoFilterBackend]
    filterset_class = MeetingFilter

    @transaction.atomic
    def perform_create(self, serializer):
        """
        Save a new Meeting with the requesting user as creator,
        then ensure the BBB session exists. Roll back if that fails.
        """
        serializer.save(creator=self.request.user.id)
        meeting = serializer.instance
        if not ensure_meeting_session(meeting.meeting_id, meeting.title):
            raise APIException("Failed to create remote BigBlueButton session")

    @transaction.atomic
    def perform_update(self, serializer):
        """
        Save updates to the Meeting instance’s metadata
        and, if key fields changed, re-ensure the BBB session.
        Roll back if re-ensure fails.
        """
        meeting = self.get_object()
        old_title = meeting.title
        old_start = meeting.start_time
        old_duration = meeting.duration

        updated_meeting = serializer.save()
        if (
            updated_meeting.title != old_title or
            updated_meeting.start_time != old_start or
            updated_meeting.duration != old_duration
        ):
            if not ensure_meeting_session(updated_meeting.meeting_id, updated_meeting.title):
                raise APIException(
                    "Failed to update remote BigBlueButton session")

    def perform_destroy(self, instance):
        instance.deleted_at = timezone.now()
        instance.save()

    @action(detail=True, methods=['get'], url_path='join-link')
    def get_join_link(self, request, meeting_id=None):
        meeting = self.get_object()

        if request.user not in meeting.program.admins.all():
            raise PermissionDenied(detail="دسترسی غیرمجاز")

        if not ensure_meeting_session(meeting.meeting_id, meeting.title):
            raise APIException(detail="خطا در ایجاد جلسه روی سرور BBB")

        requested_as_moderator = request.query_params.get(
            'as_moderator', 'false').lower() == 'true'

        join_url = generate_meeting_join_url(
            # todo: should wrap the joining process with a custom page that gets any user fullname
            full_name='ارائه‌دهنده' if requested_as_moderator else 'شرکت‌کننده',
            user_id=str(request.user.id),
            meeting_id=meeting.meeting_id,
            is_moderator=requested_as_moderator
        )

        return Response({'join_url': join_url}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def join(self, request, meeting_id=None):
        meeting = self.get_object()

        if not is_meeting_running(meeting.meeting_id):
            return Response(
                {"error_code": "این جلسه هنوز آغاز نشده است."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        join_url = generate_meeting_join_url(
            full_name=request.user.full_name,
            user_id=str(request.user.id),
            meeting_id=meeting.meeting_id,
            is_moderator=False
        )

        return Response({'join_url': join_url})
