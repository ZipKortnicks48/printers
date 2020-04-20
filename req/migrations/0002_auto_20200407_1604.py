# Generated by Django 3.0.4 on 2020-04-07 13:04

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('req', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='req',
            name='date',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.date.today)),
                ('text', models.TextField()),
                ('req', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_have_req', to='req.Req')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_have_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
