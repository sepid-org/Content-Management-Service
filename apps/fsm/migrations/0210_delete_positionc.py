# Generated by Django 4.1.3 on 2024-10-13 22:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fsm', '0209_alter_position_object_alter_positionc_object'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Positionc',
        ),
    ]
