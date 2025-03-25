import os
import shutil
from django.conf import settings
from django.test import TestCase

class BaseTestCase(TestCase):
    def tearDown(self):
        # Assuming QR codes are saved in MEDIA_ROOT/qr_codes/
        qr_codes_dir = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
        if os.path.exists(qr_codes_dir):
            shutil.rmtree(qr_codes_dir)
        # Call the parent tearDown to ensure proper cleanup
        super().tearDown()