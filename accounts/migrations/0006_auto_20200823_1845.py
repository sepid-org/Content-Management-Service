# Generated by Django 3.0.8 on 2020-08-23 14:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_answerfile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='participant',
            name='id',
        ),
        migrations.AddField(
            model_name='participant',
            name='ent_answer',
            field=models.FileField(blank=True, null=True, upload_to='ent_answers'),
        ),
        migrations.AlterField(
            model_name='participant',
            name='member',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='participant', serialize=False, to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='AnswerFile',
        ),
    ]