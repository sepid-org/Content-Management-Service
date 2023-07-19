# Generated by Django 4.1.7 on 2023-06-19 11:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='paper',
            options={},
        ),
        migrations.RemoveField(
            model_name='paper',
            name='duration',
        ),
        migrations.RemoveField(
            model_name='paper',
            name='is_exam',
        ),
        migrations.RemoveField(
            model_name='paper',
            name='since',
        ),
        migrations.RemoveField(
            model_name='paper',
            name='till',
        ),
        migrations.RemoveField(
            model_name='widget',
            name='file',
        ),
        migrations.AddField(
            model_name='paper',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='paper',
            name='update_date',
            field=models.DateTimeField(default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='widget',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='widget',
            name='update_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='paper',
            name='creator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='paper',
            name='paper_type',
            field=models.CharField(choices=[('Form', 'Form'), ('FSMState', 'Fsmstate'), ('Hint', 'Hint'), ('Article', 'Article')], max_length=25),
        ),
        migrations.AlterField(
            model_name='widget',
            name='creator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='widget',
            name='paper',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='widgets', to='base.paper'),
        ),
        migrations.AlterField(
            model_name='widget',
            name='widget_type',
            field=models.CharField(choices=[('Question', 'Question'), ('Content', 'Content')], max_length=30),
        ),
        migrations.CreateModel(
            name='Hint',
            fields=[
                ('paper_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='base.paper')),
                ('reference', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hints', to='base.widget')),
            ],
            options={
                'abstract': False,
            },
            bases=('base.paper',),
        ),
    ]