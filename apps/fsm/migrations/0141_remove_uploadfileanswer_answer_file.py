# Generated by Django 4.1.3 on 2024-07-18 20:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fsm', '0140_alter_uploadfileanswer_answer_file2'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='uploadfileanswer',
            name='answer_file',
        ),
    ]