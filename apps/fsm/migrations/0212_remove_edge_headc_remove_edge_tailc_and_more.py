# Generated by Django 4.1.3 on 2024-10-16 22:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fsm', '0211_add_flag_field'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='edge',
            name='headc',
        ),
        migrations.RemoveField(
            model_name='edge',
            name='tailc',
        ),
        migrations.RemoveField(
            model_name='fsm',
            name='first_statec',
        ),
        migrations.RemoveField(
            model_name='hint',
            name='referencec',
        ),
        migrations.RemoveField(
            model_name='player',
            name='current_statec',
        ),
        migrations.RemoveField(
            model_name='playerstatehistory',
            name='statec',
        ),
        migrations.RemoveField(
            model_name='playertransition',
            name='source_statec',
        ),
        migrations.RemoveField(
            model_name='playertransition',
            name='target_statec',
        ),
        migrations.DeleteModel(
            name='Statec',
        ),
    ]