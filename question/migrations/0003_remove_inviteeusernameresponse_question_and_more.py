# Generated by Django 4.1.7 on 2023-06-02 23:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('question', '0002_response_answer_sheet'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inviteeusernameresponse',
            name='question',
        ),
        migrations.RemoveField(
            model_name='inviteeusernameresponse',
            name='response_ptr',
        ),
        migrations.RemoveField(
            model_name='question',
            name='scorable_ptr',
        ),
        migrations.RemoveField(
            model_name='response',
            name='answer_sheet',
        ),
        migrations.RemoveField(
            model_name='response',
            name='deliverable_ptr',
        ),
        migrations.DeleteModel(
            name='InviteeUsernameQuestion',
        ),
        migrations.DeleteModel(
            name='InviteeUsernameResponse',
        ),
        migrations.DeleteModel(
            name='Question',
        ),
        migrations.DeleteModel(
            name='Response',
        ),
    ]