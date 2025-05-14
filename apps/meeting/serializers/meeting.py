from rest_framework import serializers
from apps.meeting.models import Meeting


class MeetingSerializer(serializers.ModelSerializer):
    # Computed end_time for convenience
    end_time = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Meeting
        fields = [
            'id', 'meeting_id', 'title', 'description', 'program', 'creator',
            'start_time', 'duration', 'end_time', 'status', 'location_type', 'recording_url',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'creator', 'meeting_id', 'end_time'
        ]

    def get_end_time(self, obj):
        # Calculate end_time based on start_time and duration
        if obj.start_time and obj.duration:
            return obj.start_time + obj.duration
        return None

    def validate(self, attrs):
        # Ensure duration is positive
        duration = attrs.get('duration', getattr(
            self.instance, 'duration', None))
        if duration is not None and duration.total_seconds() <= 0:
            raise serializers.ValidationError({
                'duration': 'Duration must be greater than zero.'
            })
        return attrs
