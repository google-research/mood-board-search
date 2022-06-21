import os

from django.apps import AppConfig
from django.conf import settings


class CAVstudioBackendConfig(AppConfig):
    name = 'cavstudio_backend'

    def ready(self):
        if not os.path.exists(settings.USER_DATA_DIR):
            os.makedirs(settings.USER_DATA_DIR, exist_ok=True)

        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
