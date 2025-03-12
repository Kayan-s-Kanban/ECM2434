# Generated by Django 5.1.5 on 2025-03-12 13:38

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ecolution', '0014_shopitem_image_path_alter_pet_pet_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='qr_code',
            field=models.ImageField(blank=True, null=True, upload_to='qr_codes/'),
        ),
        migrations.AddField(
            model_name='event',
            name='unique_token',
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='url_qr_code',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userevent',
            name='validated',
            field=models.BooleanField(default=False),
        ),
    ]
