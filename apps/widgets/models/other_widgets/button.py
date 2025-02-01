from django.db import models

from apps.fsm.models.base import Widget, clone_widget


class ButtonWidget(Widget):
    label = models.TextField(default='', null=True, blank=True)
    background_image = models.URLField(null=True, blank=True)
    destination_page_url = models.URLField(null=True, blank=True)
    destination_states = models.JSONField(default=[], null=True, blank=True)
    has_ripple_on_click = models.BooleanField(default=False)
    has_hover_effect = models.BooleanField(default=False)

    def clone(self, paper):
        return clone_widget(self, paper)

    def __str__(self):
        return f'<{self.id}-{self.widget_type}>:{self.name}'
