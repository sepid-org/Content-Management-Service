

from django.db import models

from apps.fsm.models.base import Paper, Widget, clone_widget


class Placeholder(Widget):

    def clone(self, paper):
        return clone_widget(self, paper)

    def __str__(self):
        return f'<{self.id}-{self.widget_type}>:{self.name}'


class TextWidget(Widget):
    text = models.TextField()

    def clone(self, paper):
        return clone_widget(self, paper)

    def __str__(self):
        return f'<{self.id}-{self.widget_type}>:{self.name}'


class DetailBoxWidget(Widget):
    title = models.TextField()
    details = models.ForeignKey(Paper, on_delete=models.CASCADE)

    def clone(self, paper):
        cloned_details = self.details  # todo
        return clone_widget(self, paper, details=cloned_details)

    def __str__(self):
        return f'<{self.id}-{self.widget_type}>:{self.name}'


class Iframe(Widget):
    link = models.URLField()

    def clone(self, paper):
        return clone_widget(self, paper)

    def __str__(self):
        return f'<{self.id}-{self.widget_type}>:{self.name}'


class Video(Widget):
    link = models.URLField(null=True, blank=True)

    def clone(self, paper):
        return clone_widget(self, paper)

    def __str__(self):
        return f'<{self.id}-{self.widget_type}>:{self.name}'


class Audio(Widget):
    link = models.URLField(null=True, blank=True)
    autoplay = models.BooleanField(default=False)

    def clone(self, paper):
        return clone_widget(self, paper)

    def __str__(self):
        return f'<{self.id}-{self.widget_type}>:{self.name}'


class Aparat(Widget):
    video_id = models.TextField()

    def clone(self, paper):
        return clone_widget(self, paper)

    def __str__(self):
        return f'<{self.id}-{self.widget_type}>:{self.name}'


class Image(Widget):
    link = models.URLField(null=True, blank=True)

    def clone(self, paper):
        return clone_widget(self, paper)

    def __str__(self):
        return f'<{self.id}-{self.widget_type}>:{self.name}'
