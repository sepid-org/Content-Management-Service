# Generated by Django 4.1.3 on 2024-11-06 03:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fsm', '0223_fsm_participant_limit'),
    ]

    operations = [
        migrations.RenameField(
            model_name='multichoiceproblem',
            old_name='lock_after_answer',
            new_name='disable_after_answer',
        ),
    ]
