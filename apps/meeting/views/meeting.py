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


class MeetingViewSet(viewsets.ModelViewSet):
    """
    Provides create, retrieve, update, partial_update, destroy
    and a custom join action for Meeting instances.
    """
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'meeting_id'
    lookup_value_regex = '[^/]+'

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['program']

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
        old_end = meeting.end_time

        updated_meeting = serializer.save()
        if (
            updated_meeting.title != old_title or
            updated_meeting.start_time != old_start or
            updated_meeting.end_time != old_end
        ):
            if not ensure_meeting_session(updated_meeting.meeting_id, updated_meeting.title):
                raise APIException(
                    "Failed to update remote BigBlueButton session")

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
            user_name=str(request.user),
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
            user_name=str(request.user),
            user_id=str(request.user.id),
            meeting_id=meeting.meeting_id,
            is_moderator=False
        )

        return Response({'join_url': join_url})
