# Generated by Django 4.1.3 on 2024-10-07 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('widgets', '0002_buttonwidget_customwidget'),
    ]

    operations = [
        migrations.RenameField(
            model_name='buttonwidget',
            old_name='destination_state_ids',
            new_name='edges_to_destination_states',
        ),
        migrations.AlterField(
            model_name='buttonwidget',
            name='label',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]