# Generated by Django 4.1.3 on 2024-01-02 10:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('question_widget', '0004_delete_multichoicequestion'),
    ]

    operations = [
        migrations.DeleteModel(
            name='InviteeUsernameQuestion',
        ),
    ]