from django.db import models


class ContentLog(models.Model):
    EVENT_TYPES = (
        ('play', 'Play'),
        ('pause', 'Pause'),
        ('progress', 'Progress'),
        ('seeking', 'Seeking'),
        ('completed', 'Completed'),
    )

    content_id = models.IntegerField(max_length=100)
    user_id = models.UUIDField(null=True, blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.get_event_type_display()} event on content {self.content_id} at {self.timestamp}"

    class Meta:
        verbose_name = "Content Log"
        verbose_name_plural = "Content Logs"
        ordering = ['-timestamp']
