# Generated by Django 4.1.3 on 2024-10-08 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsm', '0202_alter_state_papers'),
    ]

    operations = [
        migrations.AddField(
            model_name='state',
            name='papers',
            field=models.ManyToManyField(default=list, related_name='states', through='fsm.StatePaper', to='fsm.paper'),
        ),
    ]