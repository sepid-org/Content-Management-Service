# Generated by Django 5.1 on 2025-06-13 03:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0053_remove_purchase_voucher_delete_voucher'),
    ]

    operations = [
        migrations.AlterField(
            model_name='merchandise',
            name='discounted_price',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
