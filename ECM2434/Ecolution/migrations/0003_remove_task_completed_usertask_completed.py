# Generated by Django 5.1.5 on 2025-02-12 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ecolution', '0002_task_completed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='completed',
        ),
        migrations.AddField(
            model_name='usertask',
            name='completed',
            field=models.BooleanField(default=False),
        ),
    ]
