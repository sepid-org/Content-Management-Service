# Generated by Django 4.1.3 on 2024-08-23 20:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fsm', '0156_rename_program_type_program_participation_type_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='program',
            name='holder',
        ),
    ]