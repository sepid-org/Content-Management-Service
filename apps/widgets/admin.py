from django.contrib import admin

from apps.fsm.admin import WidgetAdmin
from apps.widgets.models import ButtonWidget, RandomWidget
from apps.widgets.models.other_widgets.random import SeenWidget


@admin.register(ButtonWidget)
class ButtonWidgetAdmin(WidgetAdmin):
    list_display = ['id', 'label', 'destination_page_url']
    list_filter = ['destination_page_url']
    search_fields = ['label', 'destination_page_url']


@admin.register(RandomWidget)
class RandomWidgetAdmin(WidgetAdmin):
    search_fields = ['id']
    list_display = ['box_paper_id', 'unique_widgets_only']
    list_filter = ['box_paper_id', 'unique_widgets_only']


@admin.register(SeenWidget)
class SeenWidgetAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'seen_at']
    list_filter = ['container_random_widget', 'seen_at']
    search_fields = []
    autocomplete_fields = [
        'player', 'target_widget', 'container_random_widget']
