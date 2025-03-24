import os
from django.apps import AppConfig

class EcolutionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Ecolution'

     def ready(self):
        # Ensure the MEDIA_ROOT folder exists
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)