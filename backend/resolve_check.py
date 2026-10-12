import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pricecube.settings')
django.setup()

from django.urls import resolve

r = resolve('/api/export/')
print('MATCH:', r.func.__name__ if hasattr(r, 'func') else r.func, '|', r.url_name)
