from rest_framework.exceptions import APIException
from apps.meeting.utils import is_meeting_running
from django.db import transaction
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from django.shortcuts import get_object_or_404

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

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def join(self, request, meeting_id=None):
        meeting = get_object_or_404(Meeting, meeting_id=meeting_id)

        # parse ?as_moderator=true
        requested_as_moderator = request.query_params.get(
            'as_moderator', 'false').lower() == 'true'
        is_mod_allowed = request.user in meeting.program.admins.all()
        is_moderator = requested_as_moderator and is_mod_allowed

        # check running state
        running = is_meeting_running(meeting.meeting_id)

        if not running:
            if is_moderator:
                # create the meeting on the fly for moderators
                if not ensure_meeting_session(meeting.meeting_id, meeting.title):
                    raise APIException("خطا در ایجاد جلسه روی سرور BBB")
            else:
                # viewers can only join if it's already running
                return Response(
                    {"error_code": "این جلسه هنوز آغاز نشده است."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # now generate the join URL
        join_url = generate_meeting_join_url(
            user_name=str(request.user),
            user_id=str(request.user.id),
            meeting_id=meeting.meeting_id,
            is_moderator=is_moderator
        )
        return Response({'join_url': join_url})
