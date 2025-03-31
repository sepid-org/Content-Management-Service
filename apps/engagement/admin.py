from django.contrib import admin

from .models import ContentLog


@admin.register(ContentLog)
class ContentLogAdmin(admin.ModelAdmin):
    list_display = ('content_id', 'user_id',
                    'event_type', 'details', 'timestamp')
    list_filter = ('event_type', 'timestamp')
    search_fields = ('content_id', 'user_id')
    ordering = ('-timestamp',)
