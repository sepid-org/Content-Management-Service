# Generated by Django 4.1.3 on 2024-11-01 23:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsm', '0220_alter_player_receipt'),
    ]

    operations = [
        migrations.AddField(
            model_name='audio',
            name='autoplay',
            field=models.BooleanField(default=False),
        ),
    ]