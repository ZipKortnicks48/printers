# Generated by Django 3.0.4 on 2020-05-29 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('req', '0009_auto_20200529_1307'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='req',
            name='mobile_phone',
        ),
        migrations.AlterField(
            model_name='req',
            name='phone',
            field=models.CharField(blank=True, max_length=11, null=True),
        ),
    ]