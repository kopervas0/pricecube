import os
from pathlib import Path

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pricecube.settings")

app = Celery("pricecube")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Django settings are not a real module for Celery, so we load them explicitly
import django  # noqa: E402

django.setup()
