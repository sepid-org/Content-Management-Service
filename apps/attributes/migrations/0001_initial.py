# Generated by Django 4.1.3 on 2024-08-15 08:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('attributes', models.ManyToManyField(blank=True, to='attributes.attribute')),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_%(app_label)s.%(class)s_set+', to='contenttypes.contenttype')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
        ),
        migrations.CreateModel(
            name='IntrinsicAttribute',
            fields=[
                ('attribute_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='attributes.attribute')),
                ('value', models.JSONField(blank=True, default=dict, null=True)),
                ('type', models.CharField(choices=[('cost', 'Cost'), ('reward', 'Reward'), ('required_balance', 'Required Balance')], max_length=20)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('attributes.attribute',),
        ),
        migrations.CreateModel(
            name='PerformableAction',
            fields=[
                ('attribute_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='attributes.attribute')),
                ('type', models.CharField(choices=[('see', 'See'), ('purchase', 'Purchase'), ('sell', 'Sell'), ('copy', 'Copy')], max_length=20)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('attributes.attribute',),
        ),
    ]