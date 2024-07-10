# Generated by Django 4.1.3 on 2024-06-20 09:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fsm', '0135_remove_widget_duplication_of'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='playerstatehistory',
            name='arrival_time',
        ),
        migrations.RemoveField(
            model_name='playerstatehistory',
            name='departure_time',
        ),
        migrations.RemoveField(
            model_name='playerstatehistory',
            name='is_edge_transited_in_reverse',
        ),
        migrations.RemoveField(
            model_name='playerstatehistory',
            name='is_processed',
        ),
        migrations.RemoveField(
            model_name='playerstatehistory',
            name='is_processed2',
        ),
        migrations.RemoveField(
            model_name='playerstatehistory',
            name='transited_edge',
        ),
        migrations.AlterField(
            model_name='playerstatehistory',
            name='player',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='player_state_histories', to='fsm.player'),
        ),
        migrations.AlterField(
            model_name='playerstatehistory',
            name='state',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='player_state_histories', to='fsm.state'),
        ),
        migrations.AlterField(
            model_name='playertransition',
            name='player',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='player_transitions', to='fsm.player'),
        ),
        migrations.AlterField(
            model_name='playertransition',
            name='transited_edge',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='player_transitions', to='fsm.edge'),
        ),
    ]