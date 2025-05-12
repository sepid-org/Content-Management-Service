from django.contrib import admin
from .models import Meeting


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'meeting_id', 'program', 'creator',
        'start_time', 'end_time', 'status', 'location_type'
    )
    list_filter = ('status', 'location_type', 'start_time', 'program')
    search_fields = ('title', 'meeting_id', 'description')
    readonly_fields = ('meeting_id', 'created_at', 'updated_at')
    ordering = ('-start_time',)

    fieldsets = (
        (None, {
            'fields': ('meeting_id', 'title', 'description', 'program', 'creator')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time')
        }),
        ('Status & Location', {
            'fields': ('status', 'location_type', 'recording_url')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'deleted_at')
        }),
    )
