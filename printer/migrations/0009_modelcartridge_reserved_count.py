# Generated by Django 3.0.4 on 2020-07-31 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('printer', '0008_auto_20200731_1011'),
    ]

    operations = [
        migrations.AddField(
            model_name='modelcartridge',
            name='reserved_count',
            field=models.IntegerField(default=0),
        ),
    ]
