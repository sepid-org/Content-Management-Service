from django.contrib.auth import get_user_model
from django.db import models
from apps.fsm.models.base import Widget, clone_widget
import random

from apps.fsm.models.fsm import Player


class RandomWidget(Widget):
    box_paper_id = models.PositiveIntegerField()
    unique_widgets_only = models.BooleanField(
        default=False,
        help_text="If True, shows only unseen widgets. If False, shows any random widget.",
    )

    def clone(self, paper):
        return clone_widget(self, paper)

    def get_random_widget(self, player):
        from apps.fsm.models.base import Widget

        # Get all widgets in the same box paper
        box_widgets = Widget.objects.filter(paper_id=self.box_paper_id)

        if self.unique_widgets_only:
            # First check if user has seen any widgets through this random widget
            seen_records = SeenWidget.objects.filter(
                user=player.user,
                player=player,
                container_random_widget=self,
            )

            if seen_records.exists():
                # If user has seen widgets, return one of them randomly
                random_seen_record = random.choice(seen_records)
                return random_seen_record.target_widget

            # If no seen widgets, proceed with finding a new one
            seen_widget_ids = seen_records.values_list(
                'target_widget_id', flat=True)
            available_widgets = box_widgets.exclude(id__in=seen_widget_ids)
        else:
            # Use all widgets if unique_widgets_only is False
            available_widgets = box_widgets

        if available_widgets.exists():
            random_widget = random.choice(available_widgets)

            if self.unique_widgets_only:
                # Track that it was seen through this random widget
                SeenWidget.objects.create(
                    user=player.user,
                    player=player,
                    target_widget=random_widget,
                    container_random_widget=self
                )

            return random_widget

        return None

    def __str__(self):
        return f'<{self.id}-{self.widget_type}>:{self.name}'


User = get_user_model()


class SeenWidget(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="seen_widget_records",
    )
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="seen_widget_records",
        null=True,
    )
    target_widget = models.ForeignKey(
        Widget,
        on_delete=models.CASCADE,
        related_name="seen_widget_records",
    )
    container_random_widget = models.ForeignKey(
        RandomWidget,
        on_delete=models.CASCADE,
        related_name="container_seen_widget_records"
    )
    seen_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'player', 'target_widget',
                           'container_random_widget')
        indexes = [
            models.Index(fields=['user', 'player',
                         'target_widget', 'container_random_widget']),
        ]
