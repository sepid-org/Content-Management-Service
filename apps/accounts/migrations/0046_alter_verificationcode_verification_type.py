# Generated by Django 4.1.3 on 2025-01-13 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0045_alter_purchase_discount_code_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='verificationcode',
            name='verification_type',
            field=models.CharField(choices=[('create-user-account', 'Createuseraccount'), ('reset-user-password', 'Resetuserpassword'), ('change-user-phone-number', 'Changeuserphonenumber')], max_length=30, null=True),
        ),
    ]
