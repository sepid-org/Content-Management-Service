# Generated by Django 5.1 on 2025-05-23 22:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsm', '0251_playertransition_is_backward'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playertransition',
            name='time',
            field=models.DateTimeField(),
        ),
    ]
