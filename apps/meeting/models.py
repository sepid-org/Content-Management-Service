from django.db import models
from django.core.validators import MinLengthValidator, MinValueValidator
import datetime

from apps.fsm.models.program import Program
from apps.meeting.utils import generate_meeting_id


class Meeting(models.Model):
    class MeetingStatus(models.TextChoices):
        SCHEDULED = 'scheduled', 'Scheduled'
        ONGOING = 'ongoing', 'Ongoing'
        ENDED = 'ended', 'Ended'
        CANCELED = 'canceled', 'Canceled'

    class LocationType(models.TextChoices):
        ONLINE = 'online', 'Online'
        PHYSICAL = 'physical', 'Physical'
        HYBRID = 'hybrid', 'Hybrid'

    # Core Fields
    meeting_id = models.CharField(
        max_length=255,
        unique=True,
        validators=[MinLengthValidator(3)],
        editable=False,
        help_text="Unique identifier for the meeting"
    )
    title = models.CharField(
        max_length=200,
        help_text="Short meeting title"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed meeting description"
    )

    # Relationships
    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name='meetings',
    )
    creator = models.UUIDField()

    # Time-related Fields
    start_time = models.DateTimeField(
        help_text="Date and time when the meeting starts"
    )
    duration = models.DurationField(
        default=datetime.timedelta(minutes=75),
        validators=[MinValueValidator(
            limit_value=datetime.timedelta(minutes=1))],
        help_text="Length of the meeting as a duration"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Status & Metadata
    status = models.CharField(
        max_length=20,
        choices=MeetingStatus.choices,
        default=MeetingStatus.SCHEDULED
    )
    location_type = models.CharField(
        max_length=20,
        choices=LocationType.choices,
        default=LocationType.ONLINE
    )
    recording_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL for meeting recording"
    )

    deleted_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Auto-generate a unique meeting_id if none provided
        if not self.meeting_id:
            for _ in range(5):  # try up to 5 times
                candidate = generate_meeting_id()
                if not Meeting.objects.filter(meeting_id=candidate).exists():
                    self.meeting_id = candidate
                    break
            else:
                # fallback to UUID4 hex
                import uuid
                self.meeting_id = uuid.uuid4().hex[:8]
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['start_time']),
            models.Index(fields=['status']),
        ]
        permissions = [
            ('can_schedule_meeting', 'Can schedule meetings'),
            ('can_cancel_meeting', 'Can cancel meetings'),
        ]

    def __str__(self):
        # Format duration in hours and minutes
        total_seconds = int(self.duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes = remainder // 60
        duration_str = f"{hours}h {minutes}m" if hours else f"{minutes}m"
        return f"{self.title} ({self.start_time:%Y-%m-%d %H:%M}, {duration_str})"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.duration <= datetime.timedelta(0):
            raise ValidationError("Duration must be positive and non-zero")
