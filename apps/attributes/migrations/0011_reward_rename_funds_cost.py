# Generated by Django 4.1.3 on 2024-10-23 20:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('attributes', '0010_rename_cost_funds_delete_reward'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reward',
            fields=[
                ('intrinsicattribute_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='attributes.intrinsicattribute')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('attributes.intrinsicattribute',),
        ),
        migrations.RenameModel(
            old_name='Funds',
            new_name='Cost',
        ),
    ]