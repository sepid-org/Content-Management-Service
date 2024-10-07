from django.db import models

from apps.fsm.models.base import Widget, clone_widget


class ButtonWidget(Widget):
    label = models.TextField(default='', null=True, blank=True)
    background_image = models.URLField(null=True, blank=True)
    destination_page_url = models.URLField(null=True, blank=True)
    edges_to_destination_states = models.JSONField(default=list)

    def clone(self, paper):
        return clone_widget(self, paper)

    def __str__(self):
        return f'<{self.id}-{self.widget_type}>:{self.name}'
