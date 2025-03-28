# Generated by Django 5.1.5 on 2025-03-21 20:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ecolution', '0019_gamekeeper'),
    ]

    operations = [
        migrations.AddField(
            model_name='pet',
            name='hat',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Ecolution.shopitem'),
        ),
        migrations.AddField(
            model_name='shopitem',
            name='is_hat',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='task',
            name='event',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Ecolution.event'),
        ),
    ]
