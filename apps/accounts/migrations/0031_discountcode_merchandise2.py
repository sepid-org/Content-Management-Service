# Generated by Django 4.1.3 on 2024-08-09 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0030_alter_merchandise_discounted_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='discountcode',
            name='merchandise2',
            field=models.ManyToManyField(related_name='discount_codes2', to='accounts.merchandise'),
        ),
    ]