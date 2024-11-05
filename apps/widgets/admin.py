from django.contrib import admin

from apps.fsm.admin import WidgetAdmin
from apps.widgets.models.other_widgets.button import ButtonWidget


@admin.register(ButtonWidget)
class ButtonAdmin(WidgetAdmin):
    list_display = ['id', 'label', 'destination_page_url']
    list_filter = ['destination_page_url']
    search_fields = ['label', 'destination_page_url']
