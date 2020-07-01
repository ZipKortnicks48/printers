# Generated by Django 3.0.4 on 2020-05-29 09:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('req', '0007_auto_20200525_1549'),
    ]

    operations = [
        migrations.AddField(
            model_name='req',
            name='executor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='req_have_executor', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='req',
            name='status',
            field=models.CharField(default='1', max_length=1),
        ),
    ]
