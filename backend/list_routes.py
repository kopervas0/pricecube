import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pricecube.settings")
django.setup()

from django.urls import get_resolver

print("=== URLS (db + redis + redis) ===")
for p in get_resolver().url_patterns:
    s = getattr(p, "pattern", "")
    name = getattr(p, "name", "")
    print("  ", getattr(p, "callback", None), "|", s, "|", name)
