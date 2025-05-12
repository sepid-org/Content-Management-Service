from rest_framework import serializers
from apps.meeting.models import Meeting


class MeetingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Meeting
        fields = [
            'id', 'meeting_id', 'title', 'description', 'program', 'creator',
            'start_time', 'end_time', 'status', 'location_type', 'recording_url',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'creator', 'meeting_id'
        ]

    def validate(self, attrs):
        # Pull the new or existing values for both start and end
        start = attrs.get('start_time',
                          getattr(self.instance, 'start_time', None))
        end = attrs.get('end_time',
                        getattr(self.instance, 'end_time', None))

        if start and end and end <= start:
            raise serializers.ValidationError({
                'end_time': 'زمان پایان باید بعد از زمان شروع باشد.'
            })

        return attrs
