# Generated by Django 4.1.3 on 2024-09-25 16:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fsm', '0181_registrationformc_remove_fsm_registration_form_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fsm',
            name='registration_form',
        ),
        migrations.AlterField(
            model_name='program',
            name='registration_formc',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='programc', to='fsm.registrationformc'),
        ),
    ]