# Generated by Django 5.1.5 on 2025-02-12 18:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Ecolution', '0004_event_alter_usertask_unique_together_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='EventTask',
            new_name='UserEvent',
        ),
    ]
