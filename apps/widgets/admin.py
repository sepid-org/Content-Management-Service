from django.db import models
from django.contrib import admin
from django.forms import Textarea

from apps.widgets.models import DialogWidget, BackgroundSoundWidget
from apps.widgets.models.other_widgets.button import ButtonWidget


@admin.register(DialogWidget)
class DialogWidgetCustomAdmin(admin.ModelAdmin):
    list_display = ['id']
    list_filter = []


@admin.register(BackgroundSoundWidget)
class BackgroundSoundWidgetCustomAdmin(admin.ModelAdmin):
    list_display = ['id']
    list_filter = []


@admin.register(ButtonWidget)
class ButtonAdmin(admin.ModelAdmin):
    list_display = ['id', 'label', 'destination_page_url']
    list_filter = ['destination_page_url']
    search_fields = ['label', 'destination_page_url']
