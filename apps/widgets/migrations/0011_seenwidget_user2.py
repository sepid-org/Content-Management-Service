# Generated by Django 5.1 on 2025-04-23 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('widgets', '0010_remove_buttonwidget_disable_ripple_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='seenwidget',
            name='user2',
            field=models.UUIDField(blank=True, null=True),
        ),
    ]
