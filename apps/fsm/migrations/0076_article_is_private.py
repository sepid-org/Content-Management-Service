# Generated by Django 4.1.3 on 2023-11-02 22:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsm', '0075_alter_certificatetemplate_name_x_percentage_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='is_private',
            field=models.BooleanField(default=False),
        ),
    ]