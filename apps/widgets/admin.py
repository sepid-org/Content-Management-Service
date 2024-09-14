from django.contrib import admin

from apps.widgets.models import DialogWidget, BackgroundSoundWidget


@admin.register(DialogWidget)
class DialogWidgetCustomAdmin(admin.ModelAdmin):
    list_display = ['id']
    list_filter = []


@admin.register(BackgroundSoundWidget)
class BackgroundSoundWidgetCustomAdmin(admin.ModelAdmin):
    list_display = ['id']
    list_filter = []
