# Generated by Django 4.1.3 on 2024-11-05 09:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('attributes', '0011_reward_rename_funds_cost'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('performableaction_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='attributes.performableaction')),
                ('question_id', models.PositiveIntegerField()),
                ('answer_type', models.CharField(choices=[('SmallAnswer', 'Smallanswer'), ('BigAnswer', 'Biganswer'), ('MultiChoiceAnswer', 'Multichoiceanswer'), ('UploadFileAnswer', 'Uploadfileanswer')], max_length=20)),
                ('provided_answer', models.JSONField(default=dict)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('attributes.performableaction',),
        ),
    ]